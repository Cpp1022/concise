---
name: concise-default
description: >
  Toggle concise auto-activation for new agent sessions. Supports status/on/off
  for Codex CLI, Codex app session observation, Cursor, and Claude Code.
  Trigger: "concise-default", "concise default on", "concise default off",
  "concise default status", "concise always on", "默认 concise", "开启默认 concise", "关闭默认 concise".
---

# Concise Default

Toggle concise mode auto-activation globally. This is a shell-backed setup skill, not a conversational style toggle.

## Commands

Run these in shell via the wrapper installed from this repository.

| Command | Effect |
|---------|--------|
| `concise-default on` | Enable with last saved level, first time: `ultra` |
| `concise-default on lite` | Enable with `lite` level |
| `concise-default on ultra` | Enable with `ultra` level |
| `concise-default off` | Disable auto-activation |
| `concise-default status` | Show current state and saved level |

`full` is not supported. Valid levels: `lite`, `ultra`.

## Execution Contract

When the user sends `concise-default on|off|status` or a direct variant:

- Execute the shell command first. Never only acknowledge in text.
- Use the local wrapper when available:
  - Windows: `~/.codex/bin/concise-default.cmd`
  - Unix: `~/.codex/bin/concise-default` or `~/.codex/bin/concise-default.sh`
- Base the reply on exit code and stdout/stderr. Do not infer success.
- If execution changes state for testing, restore the previous state before final reply.
- If shell execution is blocked, say `未执行：<reason>` and stop.

## Minimal Replies

| Observed result | Reply |
|-----------------|-------|
| exit `0` and output contains `concise default ON` | `ON: <level>` |
| exit `0` and output contains `concise default OFF` | `OFF` |
| exit `0` status output, all targets ON | `ON: all` |
| exit `0` status output, mixed ON/OFF | `PARTIAL: <off targets>` |
| exit `0` status output, all targets OFF | `OFF: all` |
| exit nonzero with `Error:` | `ERROR: <short error>` |
| command not found / wrapper missing | `未执行：command not found` |

Target names are printed by the command: `Cursor`, `Claude Code`, `Codex CLI`, `Codex App`.

## Behavior

- `on`: new sessions start with concise active, no manual trigger needed.
- `off`: removes generated default-instruction files/blocks.
- Mid-session exit still uses `stop concise` or `normal mode`; this does not change the saved default.
- Saved level: `~/.config/concise/config`.
- Generated targets:
  - Cursor: `~/.cursor/rules/concise.mdc`
  - Claude Code: marked block in `~/.claude/CLAUDE.md`
  - Codex CLI: `~/.codex/instructions.md`

## Codex Context Splicing

Codex does not read a live toggle during a conversation. New sessions include the contents of `~/.codex/instructions.md` in their base instructions.

So:

- `Codex CLI: ON` means `~/.codex/instructions.md` exists.
- `Codex App: ON` means the most recent Codex session JSONL appears to include the first signal line from `instructions.md` in `base_instructions`.
- `Codex App: OFF` can mean either disabled, not yet started in a new session, or no readable recent session file.