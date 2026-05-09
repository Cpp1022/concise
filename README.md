# concise

Chinese-first concise mode for Codex CLI / Claude Code / Cursor.

## TL;DR

- Goal: install once, make Codex CLI follow the same wrapper chain used here.
- Levels: only `lite` and `ultra`.
- `concise-default` is optional; Codex CLI primary path is the wrapper.

## Quick Install

```sh
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh
```

Default behavior: installs the Codex CLI wrapper chain.
Optional generated defaults:

```sh
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- --default lite
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- --default ultra
```

## In Chat

```text
/concise
/concise lite
/concise ultra
stop concise
normal mode
```

## Levels

- `lite`: expression compression only
- `ultra`: expression + content compression

No other levels are supported.

## Runtime Model

Source of truth: `concise/SKILL.md` (detailed layer + reinforcement layer).
Injection order: reinforcement first, then detail.

Physical files:

- Reinforcement layer: `concise/REINFORCE.md`
- Detail layer: `concise/DETAIL.md`
- Compatibility source: `concise/SKILL.md`

Global runtime targets:

- Cursor: `~/.cursor/rules/concise-reinforce.mdc` then `~/.cursor/rules/concise-detail.mdc`
- Codex wrapper source: `concise/scripts/codex`
- Claude Code: managed block in `~/.claude/CLAUDE.md`

Codex CLI injection path:

- wrapper: `~/.codex/bin/codex`
- base concise rules: `~/.codex/skills/concise/REINFORCE.md` → `~/.codex/skills/concise/DETAIL.md`
- fallback source: `~/.codex/skills/concise/SKILL.md`
- project merge order inside wrapper: `concise layers` → `AGENTS.md` → `AGENTS.override.md`

## What `concise-default` Writes

- `~/.cursor/rules/concise.mdc`
- `~/.cursor/rules/concise-reinforce.mdc`
- `~/.cursor/rules/concise-detail.mdc`
- `~/.claude/CLAUDE.md` (managed block)
- `~/.codex/instructions.md`
- `~/.codex/instructions.reinforce.md`
- `~/.codex/instructions.detail.md`
- `~/.config/concise/config`

## Commands

```sh
concise-default on ultra
concise-default on lite
concise-default status
concise-default off
```

## Repo Layout

```text
.
|-- concise/
|   |-- SKILL.md
|   |-- REINFORCE.md
|   `-- DETAIL.md
|-- concise-default/
|   |-- SKILL.md
|   `-- scripts/
|-- install.sh
`-- README.md
```

## Notes

- Edit global behavior in `concise/SKILL.md`.
- Do not hand-edit generated target files under `~/.cursor` / `~/.codex`.
- For Codex CLI, keep `~/.codex/bin` ahead of the real Codex binary in `PATH`.

## License

MIT
