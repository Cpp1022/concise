---
name: concise-default
description: >
  Toggle concise auto-activation for all new sessions across Cursor, Claude Code, Codex CLI.
  Trigger: "concise-default", "concise default on", "concise default off",
  "concise always on", "默认concise", "开启默认concise", "关闭默认concise".
---

# Concise Default

Toggle concise mode auto-activation globally. Affects Cursor + Claude Code + Codex CLI.

## Commands

Run these in shell:

| Command | Effect |
|---------|--------|
| `concise-default on` | Enable with last saved level (first time: ultra) |
| `concise-default on lite` | Enable with lite level |
| `concise-default on ultra` | Enable with ultra level |
| `concise-default off` | Disable auto-activation |
| `concise-default status` | Show current state and level |

Valid levels: `lite`, `ultra`.

## Behavior

- ON: every new session starts with concise active, no manual trigger needed
- Mid-session exit: `stop concise` or `normal mode` (doesn't change default setting)
- Level saved to `~/.config/concise/config`, persists across on/off cycles
- Patches: `~/.cursor/rules/concise.mdc`, `~/.claude/CLAUDE.md`, `~/.codex/instructions.md`
