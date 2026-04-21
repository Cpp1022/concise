---
name: concise-default
description: Use when the user wants concise mode to be the default for every new chat across Codex CLI, Claude Code, and Cursor. Triggers on "concise default", "default concise", "make concise the default", "concise-default on", "concise-default off", "concise-default status", "concise always on", "开启默认concise", "默认concise", "每次都concise", "/concise-default". Writes ~/.codex/instructions.md, a managed block in ~/.claude/CLAUDE.md, and ~/.cursor/rules/concise.mdc.
---

# Concise Default

Toggle concise mode auto-activation globally. Affects Cursor, Claude Code, and Codex CLI.

## Commands

Run these in shell:

| Command | Effect |
| --- | --- |
| `concise-default on` | Enable with last saved level. First time: `ultra`. |
| `concise-default on lite` | Enable with `lite` level. |
| `concise-default on ultra` | Enable with `ultra` level. |
| `concise-default off` | Disable auto-activation. |
| `concise-default status` | Show current state and level. |

Valid levels: `lite`, `ultra`.

## Behavior

- `on`: every new session starts with concise active; no manual trigger needed.
- `off`: removes generated concise defaults.
- Mid-session exit: `stop concise` or `normal mode`; this does not change the default setting.
- Saved level: `~/.config/concise/config`; persists across on/off cycles.
- Writes:
  - Cursor: `~/.cursor/rules/concise.mdc`
  - Claude Code: `~/.claude/CLAUDE.md`
  - Codex CLI: `~/.codex/instructions.md`