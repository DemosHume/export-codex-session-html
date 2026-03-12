#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


BOOTSTRAP_PREFIXES = (
    "# AGENTS.md instructions for ",
    "<environment_context>",
)

ROLE_LABELS = {
    "user": "User",
    "assistant": "Assistant",
    "developer": "Developer",
    "system": "System",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a Codex session JSONL transcript to HTML."
    )
    parser.add_argument(
        "--thread-id",
        help="Target thread ID. Defaults to the CODEX_THREAD_ID environment variable.",
    )
    parser.add_argument(
        "--codex-home",
        help="Override the Codex home directory. Defaults to CODEX_HOME or ~/.codex.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where the HTML file will be written. Defaults to the current directory.",
    )
    parser.add_argument(
        "--output-file",
        help="Explicit output HTML file path. Overrides the generated file name.",
    )
    parser.add_argument(
        "--include-bootstrap",
        action="store_true",
        help="Include bootstrap messages such as AGENTS and environment context.",
    )
    parser.add_argument(
        "--include-developer",
        action="store_true",
        help="Include developer and system messages in the transcript.",
    )
    return parser.parse_args()


def resolve_codex_home(raw_home: str | None) -> Path:
    if raw_home:
        return Path(raw_home).expanduser().resolve()

    env_home = os.environ.get("CODEX_HOME")
    if env_home:
        return Path(env_home).expanduser().resolve()

    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        return Path(user_profile, ".codex").resolve()

    return Path.home().joinpath(".codex").resolve()


def resolve_thread_id(explicit_thread_id: str | None) -> str:
    thread_id = explicit_thread_id or os.environ.get("CODEX_THREAD_ID")
    if not thread_id:
        raise SystemExit(
            "Missing thread ID. Pass --thread-id or run inside Codex with CODEX_THREAD_ID set."
        )
    return thread_id


def locate_session_file(codex_home: Path, thread_id: str) -> Path:
    candidates: list[Path] = []
    for folder_name in ("sessions", "archived_sessions"):
        base_dir = codex_home / folder_name
        if not base_dir.exists():
            continue
        for candidate in base_dir.rglob(f"*{thread_id}*.jsonl"):
            if candidate.is_file():
                candidates.append(candidate)

    if not candidates:
        raise SystemExit(
            f"Could not find a session file for thread {thread_id} under {codex_home}."
        )

    candidates.sort(key=lambda path: (path.stat().st_mtime, str(path)))
    return candidates[-1]


def iter_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(
                    f"Failed to parse JSON on line {line_number} of {path}: {exc}"
                ) from exc


def extract_text(content: object) -> str:
    if isinstance(content, str):
        return content.strip()

    if not isinstance(content, list):
        return ""

    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if isinstance(text, str) and text.strip():
            parts.append(text.strip())
            continue
        if item.get("type") in {"input_text", "output_text"}:
            value = item.get("text")
            if isinstance(value, str) and value.strip():
                parts.append(value.strip())
    return "\n\n".join(parts).strip()


def is_bootstrap_message(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    return any(stripped.startswith(prefix) for prefix in BOOTSTRAP_PREFIXES)


def parse_session_index_title(index_path: Path, thread_id: str) -> str | None:
    if not index_path.exists():
        return None

    title: str | None = None
    for record in iter_jsonl(index_path):
        if record.get("id") == thread_id:
            candidate = record.get("thread_name")
            if isinstance(candidate, str) and candidate.strip():
                title = candidate.strip()
    return title


def collect_messages(
    session_path: Path,
    include_bootstrap: bool,
    include_developer: bool,
) -> tuple[dict, list[dict]]:
    session_meta: dict = {}
    messages: list[dict] = []

    for record in iter_jsonl(session_path):
        record_type = record.get("type")
        payload = record.get("payload", {})

        if record_type == "session_meta" and isinstance(payload, dict):
            session_meta = payload
            continue

        if record_type != "response_item" or not isinstance(payload, dict):
            continue

        if payload.get("type") != "message":
            continue

        role = payload.get("role")
        if role not in {"user", "assistant", "developer", "system"}:
            continue
        if role in {"developer", "system"} and not include_developer:
            continue

        text = extract_text(payload.get("content"))
        if not text:
            continue
        if role == "user" and not include_bootstrap and is_bootstrap_message(text):
            continue

        messages.append(
            {
                "timestamp": record.get("timestamp") or session_meta.get("timestamp"),
                "role": role,
                "phase": payload.get("phase") or "",
                "text": text,
            }
        )

    return session_meta, messages


def first_real_user_message(messages: list[dict]) -> str | None:
    for message in messages:
        if message["role"] != "user":
            continue
        text = message["text"].strip()
        if text:
            return text.splitlines()[0].strip()
    return None


def sanitize_filename_component(value: str) -> str:
    value = re.sub(r"[<>:\"/\\\\|?*\x00-\x1f]", " ", value)
    value = re.sub(r"[`~!@#$%^&*()+={}\[\];',.]", " ", value)
    value = re.sub(r"\s+", "-", value.strip())
    value = re.sub(r"-{2,}", "-", value)
    value = value.strip("-.")
    return value[:24] if len(value) > 24 else value


def derive_title(index_title: str | None, messages: list[dict], thread_id: str) -> str:
    if index_title:
        return index_title

    first_message = first_real_user_message(messages)
    if first_message:
        return first_message[:60].strip()

    return f"Session {thread_id[:8]}"


def choose_output_path(
    output_dir: Path,
    explicit_output_file: str | None,
    title: str,
    thread_id: str,
    session_meta: dict,
) -> Path:
    if explicit_output_file:
        return Path(explicit_output_file).expanduser().resolve()

    raw_timestamp = session_meta.get("timestamp")
    date_part = "unknown-date"
    if isinstance(raw_timestamp, str):
        try:
            parsed = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
            date_part = parsed.astimezone().strftime("%Y-%m-%d")
        except ValueError:
            pass

    slug = sanitize_filename_component(title)
    if not slug:
        slug = thread_id[:8]

    short_id = thread_id[:8]
    if slug == short_id:
        file_name = f"codex-session-{date_part}-{slug}.html"
    else:
        file_name = f"codex-session-{date_part}-{slug}-{short_id}.html"
    return output_dir.resolve() / file_name


def format_timestamp(raw_timestamp: str | None) -> str:
    if not raw_timestamp:
        return ""
    try:
        parsed = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
    except ValueError:
        return raw_timestamp
    return parsed.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def render_html(
    *,
    title: str,
    thread_id: str,
    session_path: Path,
    session_meta: dict,
    messages: list[dict],
) -> str:
    exported_at = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    message_blocks: list[str] = []

    for message in messages:
        role = message["role"]
        role_label = ROLE_LABELS.get(role, role.title())
        role_class = f"role-{role}"
        phase_badge = ""
        if message["phase"]:
            phase_badge = (
                f'<span class="badge">{html.escape(str(message["phase"]))}</span>'
            )
        timestamp_text = format_timestamp(message["timestamp"])
        timestamp_html = ""
        if timestamp_text:
            timestamp_html = (
                f'<span class="timestamp">{html.escape(timestamp_text)}</span>'
            )
        body = html.escape(message["text"])
        message_blocks.append(
            "\n".join(
                [
                    f'<section class="message {role_class}">',
                    '  <header class="message-header">',
                    f'    <span class="role">{html.escape(role_label)}</span>{phase_badge}{timestamp_html}',
                    "  </header>",
                    f'  <div class="message-body">{body}</div>',
                    "</section>",
                ]
            )
        )

    session_started = format_timestamp(session_meta.get("timestamp"))
    cwd = html.escape(str(session_meta.get("cwd", "")))
    source_file = html.escape(str(session_path))

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f1e8;
      --panel: #fffdf8;
      --panel-strong: #f5ede1;
      --text: #22201d;
      --muted: #736a5d;
      --border: #d8cdbf;
      --user: #b74d2c;
      --assistant: #1f5f5b;
      --developer: #6a4bc2;
      --system: #555555;
      --badge: #efe4d4;
      --shadow: 0 14px 40px rgba(34, 32, 29, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(circle at top right, rgba(183, 77, 44, 0.12), transparent 28%),
        linear-gradient(180deg, #fbf6ef 0%, var(--bg) 100%);
      color: var(--text);
    }}
    main {{
      max-width: 980px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    .hero {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 28px;
      box-shadow: var(--shadow);
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: 32px;
      line-height: 1.2;
    }}
    .meta {{
      margin: 6px 0;
      color: var(--muted);
      word-break: break-all;
    }}
    .messages {{
      margin-top: 24px;
      display: grid;
      gap: 16px;
    }}
    .message {{
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 18px 18px 16px;
      box-shadow: var(--shadow);
    }}
    .message-header {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin-bottom: 10px;
    }}
    .role {{
      font-weight: 700;
      letter-spacing: 0.02em;
    }}
    .role-user .role {{ color: var(--user); }}
    .role-assistant .role {{ color: var(--assistant); }}
    .role-developer .role {{ color: var(--developer); }}
    .role-system .role {{ color: var(--system); }}
    .badge {{
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--badge);
      color: var(--muted);
      font-size: 12px;
    }}
    .timestamp {{
      color: var(--muted);
      font-size: 13px;
      margin-left: auto;
    }}
    .message-body {{
      white-space: pre-wrap;
      line-height: 1.65;
      word-break: break-word;
    }}
    @media (max-width: 720px) {{
      main {{ padding: 18px 12px 28px; }}
      .hero, .message {{ border-radius: 16px; }}
      h1 {{ font-size: 24px; }}
      .timestamp {{ margin-left: 0; width: 100%; }}
    }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>{html.escape(title)}</h1>
      <div class="meta">Thread ID: {html.escape(thread_id)}</div>
      <div class="meta">Session started: {html.escape(session_started)}</div>
      <div class="meta">Workspace: {cwd}</div>
      <div class="meta">Source JSONL: {source_file}</div>
      <div class="meta">Exported at: {html.escape(exported_at)}</div>
      <div class="meta">Messages: {len(messages)}</div>
    </section>
    <section class="messages">
      {''.join(message_blocks)}
    </section>
  </main>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    codex_home = resolve_codex_home(args.codex_home)
    thread_id = resolve_thread_id(args.thread_id)
    session_path = locate_session_file(codex_home, thread_id)
    session_meta, messages = collect_messages(
        session_path=session_path,
        include_bootstrap=args.include_bootstrap,
        include_developer=args.include_developer,
    )

    if not messages:
        raise SystemExit(f"No exportable messages found in {session_path}.")

    index_title = parse_session_index_title(codex_home / "session_index.jsonl", thread_id)
    title = derive_title(index_title, messages, thread_id)
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = choose_output_path(
        output_dir=output_dir,
        explicit_output_file=args.output_file,
        title=title,
        thread_id=thread_id,
        session_meta=session_meta,
    )

    html_text = render_html(
        title=title,
        thread_id=thread_id,
        session_path=session_path,
        session_meta=session_meta,
        messages=messages,
    )
    output_path.write_text(html_text, encoding="utf-8")
    print(f"Exported HTML: {output_path}")


if __name__ == "__main__":
    main()
