---
name: export-codex-session-html
description: Export the current Codex desktop session, or a specified thread, from local .codex JSONL session files into a readable HTML transcript in the current working directory. Use when the user asks to save, share, archive, or review Codex chat history as an HTML file.
---

# Export Codex Session HTML

## Overview

Use this skill when the user wants a Codex chat transcript exported to HTML.
It reads the local session JSONL file under the current user's Codex home, filters out bootstrap noise by default, and writes a readable HTML file into the current working directory.

## Workflow

1. Resolve the target thread.

- Default to the current thread by reading `CODEX_THREAD_ID`.
- If the user gives another thread ID, pass it with `--thread-id`.

2. Run the bundled exporter script.

- Script path: `scripts/export_session_html.py`
- The exporter resolves Codex home from `CODEX_HOME`, then falls back to `%USERPROFILE%\.codex` on Windows or `~/.codex` on other platforms.
- Prefer the Python wrapper from `$conda-codex-python` on Windows.

Example for the current session:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
& (Join-Path $codexHome "skills\local\conda-codex-python\scripts\run-python.ps1") `
  -ScriptPath (Join-Path $codexHome "skills\local\export-codex-session-html\scripts\export_session_html.py") `
  -WorkingDirectory "C:\path\to\workspace" `
  -ScriptArgs @("--output-dir", ".")
```

Example for a specific thread:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
& (Join-Path $codexHome "skills\local\conda-codex-python\scripts\run-python.ps1") `
  -ScriptPath (Join-Path $codexHome "skills\local\export-codex-session-html\scripts\export_session_html.py") `
  -WorkingDirectory "C:\path\to\workspace" `
  -ScriptArgs @("--thread-id", "your-thread-id-here", "--output-dir", ".")
```

3. Verify the generated file.

- Confirm the script prints the output path.
- Open the generated HTML if the user wants a quick check.

## Defaults

- Export only chat messages by default.
- Skip bootstrap context such as AGENTS and environment payloads.
- Skip tool calls and tool outputs unless explicitly extending the script later.
- Generate a safe filename from thread title or the first real user message; fall back to the thread ID.

## Output

The HTML transcript includes:

- Session title
- Thread ID
- Source JSONL path
- Export timestamp
- Chronological user and assistant messages
- Assistant phase badges when available, such as `commentary` or `final_answer`

## Guardrails

- Do not guess the session file path; resolve it from `CODEX_THREAD_ID` or `--thread-id`.
- Read from `~/.codex/sessions` first, then `~/.codex/archived_sessions` as fallback.
- Avoid dumping developer/system bootstrap messages unless the user explicitly wants the raw session.
- Write the HTML into the current working directory unless the user requests another output directory.
- Avoid embedding one person's absolute home directory in the skill instructions; use `CODEX_HOME`, `%USERPROFILE%`, or `~` based paths instead.
