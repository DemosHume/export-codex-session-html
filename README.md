# Export Codex Session HTML

[![CI](https://github.com/DemosHume/export-codex-session-html/actions/workflows/ci.yml/badge.svg)](https://github.com/DemosHume/export-codex-session-html/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-green)

Export local Codex Desktop session transcripts into clean, shareable HTML files.

[中文](#中文) | [English](#english)

## Highlights

- Export the current Codex thread or a specific thread ID
- Filter bootstrap noise by default
- Generate readable HTML transcripts for sharing or archiving
- Works with `CODEX_HOME`, Windows `%USERPROFILE%\.codex`, and Unix `~/.codex`

## 中文

### 这是什么

`export-codex-session-html` 是一个 Codex skill，用来把本地 Codex Desktop 会话记录导出成可阅读的 HTML 聊天稿。

它会从当前用户的 Codex 本地会话目录中读取 JSONL session 文件，过滤掉默认不需要看的启动上下文，然后把用户和助手的对话整理成一份适合分享、归档、复盘的 HTML 文件。

### 适合什么场景

- 需要把当前 Codex 对话导出成 HTML
- 需要按 thread ID 导出另一段会话
- 需要归档、分享、备份聊天记录
- 需要把技术排查或协作记录整理成一个可读文件

### 功能特点

- 默认导出当前会话，直接读取 `CODEX_THREAD_ID`
- 支持通过 `--thread-id` 导出指定会话
- 默认过滤 AGENTS、环境注入等启动噪音
- 自动从 thread title 或首条真实用户消息生成文件名
- 输出到当前工作目录，便于直接整理到项目里
- 兼容 `CODEX_HOME`、Windows `%USERPROFILE%\.codex`、Unix `~/.codex`

### 环境要求

- Codex Desktop 或兼容的本地 session 目录
- Python 3
- Windows 下建议配合 `$conda-codex-python`

### 仓库结构

```text
.
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── export_session_html.py
```

### 安装方式

#### 方式 1：作为本地 skill 使用

把这个目录放到你的 Codex skills 目录下，例如：

- Windows: `%USERPROFILE%\.codex\skills\local\export-codex-session-html`
- Unix-like: `~/.codex/skills/local/export-codex-session-html`

#### 方式 2：作为分享包导入

如果你的 Codex/ChatGPT skills 界面支持从本地上传，也可以直接把这个 skill 目录作为一个独立 skill 导入。

### 使用示例

#### 导出当前会话

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
& (Join-Path $codexHome "skills\local\conda-codex-python\scripts\run-python.ps1") `
  -ScriptPath (Join-Path $codexHome "skills\local\export-codex-session-html\scripts\export_session_html.py") `
  -WorkingDirectory "C:\path\to\workspace" `
  -ScriptArgs @("--output-dir", ".")
```

#### 导出指定 thread

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
& (Join-Path $codexHome "skills\local\conda-codex-python\scripts\run-python.ps1") `
  -ScriptPath (Join-Path $codexHome "skills\local\export-codex-session-html\scripts\export_session_html.py") `
  -WorkingDirectory "C:\path\to\workspace" `
  -ScriptArgs @("--thread-id", "your-thread-id-here", "--output-dir", ".")
```

### 输出内容

导出的 HTML 默认包含：

- 会话标题
- Thread ID
- 源 session 文件路径
- 导出时间
- 按时间顺序排列的用户与助手消息
- 助手消息 phase 标记，例如 `commentary`、`final_answer`

### 可用参数

- `--thread-id`: 指定要导出的 thread ID
- `--codex-home`: 手动指定 Codex home 目录
- `--output-dir`: 指定输出目录
- `--output-file`: 指定输出文件名
- `--include-bootstrap`: 包含启动上下文
- `--include-developer`: 包含 developer/system 消息

### 注意事项

- 默认只导出聊天消息，不导出 tool call 和 tool output
- 如果用户明确需要“原始完整 transcript”，可以加 `--include-bootstrap` 或继续扩展脚本
- 这个仓库不包含任何用户私有会话数据，只包含 skill 定义和导出脚本

### 许可证

本项目使用 `MIT` 许可证，见 [LICENSE](./LICENSE)。

## English

### What This Is

`export-codex-session-html` is a Codex skill that exports local Codex Desktop session transcripts into readable HTML files.

It reads local JSONL session files from the current user's Codex home, filters out bootstrap noise by default, and formats the actual conversation into an HTML transcript suitable for sharing, archiving, or review.

### Good Use Cases

- Export the current Codex conversation to HTML
- Export another conversation by thread ID
- Archive or share a chat transcript
- Preserve debugging or collaboration history in a readable format

### Features

- Exports the current session by default via `CODEX_THREAD_ID`
- Supports exporting a specific thread with `--thread-id`
- Skips bootstrap context such as AGENTS and environment injection by default
- Generates a safe output filename from the thread title or first real user message
- Writes output to the current working directory
- Supports `CODEX_HOME`, Windows `%USERPROFILE%\.codex`, and Unix `~/.codex`

### Requirements

- Codex Desktop or a compatible local session directory
- Python 3
- On Windows, `$conda-codex-python` is the recommended wrapper

### Repository Layout

```text
.
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── export_session_html.py
```

### Installation

#### Option 1: Use as a local skill

Place this directory under your Codex skills directory, for example:

- Windows: `%USERPROFILE%\.codex\skills\local\export-codex-session-html`
- Unix-like: `~/.codex/skills/local/export-codex-session-html`

#### Option 2: Import as a shared skill package

If your Codex or ChatGPT skills UI supports local upload, you can import this directory directly as a standalone skill.

### Usage Examples

#### Export the current session

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
& (Join-Path $codexHome "skills\local\conda-codex-python\scripts\run-python.ps1") `
  -ScriptPath (Join-Path $codexHome "skills\local\export-codex-session-html\scripts\export_session_html.py") `
  -WorkingDirectory "C:\path\to\workspace" `
  -ScriptArgs @("--output-dir", ".")
```

#### Export a specific thread

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE ".codex" }
& (Join-Path $codexHome "skills\local\conda-codex-python\scripts\run-python.ps1") `
  -ScriptPath (Join-Path $codexHome "skills\local\export-codex-session-html\scripts\export_session_html.py") `
  -WorkingDirectory "C:\path\to\workspace" `
  -ScriptArgs @("--thread-id", "your-thread-id-here", "--output-dir", ".")
```

### Output

The generated HTML includes:

- Session title
- Thread ID
- Source session file path
- Export timestamp
- Chronological user and assistant messages
- Assistant phase badges such as `commentary` and `final_answer`

### CLI Arguments

- `--thread-id`: Export a specific thread ID
- `--codex-home`: Manually override the Codex home directory
- `--output-dir`: Choose the output directory
- `--output-file`: Choose the exact output file path
- `--include-bootstrap`: Include bootstrap context
- `--include-developer`: Include developer and system messages

### Notes

- By default, the exporter includes conversation messages only, not tool calls or tool outputs
- If you need a more raw transcript, use `--include-bootstrap` or extend the script
- This repository contains only the skill definition and exporter script, not any private user session data

### License

This project is licensed under the `MIT` License. See [LICENSE](./LICENSE).
