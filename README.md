# concise

Chinese expression compression skill for Codex-style agents.

This skill makes agent responses shorter and denser while preserving technical accuracy and decision quality. It is designed for Chinese output and supports two levels: `lite` and `ultra`.

## What It Is

`concise` is a skill file, not a CLI tool or library.

Use it when you want an agent to:
- use fewer tokens
- reduce filler and repetition
- keep conclusions first
- stay compact in Chinese technical writing
- avoid repeated conclusions, filler, and unasked-for expansion

## Install

Copy this repository's `SKILL.md` into your local Codex skills directory.

### Windows

```powershell
mkdir $env:USERPROFILE\.codex\skills\concise -Force
copy SKILL.md $env:USERPROFILE\.codex\skills\concise\SKILL.md
```

Optional default-on command:

```powershell
mkdir $env:USERPROFILE\.codex\bin -Force
copy bin\concise-default.py $env:USERPROFILE\.codex\bin\concise-default.py
copy bin\concise-default.cmd $env:USERPROFILE\.codex\bin\concise-default.cmd

mkdir $env:USERPROFILE\.codex\skills\concise-default -Force
copy skills\concise-default\SKILL.md $env:USERPROFILE\.codex\skills\concise-default\SKILL.md
```

Then add `~/.codex/bin` to your `PATH`, or run the wrapper by full path.

### Unix-like

```sh
mkdir -p ~/.codex/skills/concise
cp SKILL.md ~/.codex/skills/concise/SKILL.md
```

Optional default-on command:

```sh
mkdir -p ~/.codex/bin ~/.codex/skills/concise-default
cp bin/concise-default.py ~/.codex/bin/concise-default.py
cp bin/concise-default.sh ~/.codex/bin/concise-default
chmod +x ~/.codex/bin/concise-default
cp skills/concise-default/SKILL.md ~/.codex/skills/concise-default/SKILL.md
```

## Trigger

Common triggers:
- `/concise`
- `/concise lite`
- `/concise ultra`
- `concise mode`
- `use concise`
- `be brief`
- `less tokens`

Default level: `ultra`.

The mode persists across turns until the user says:

- `stop concise`
- `normal mode`

## Default-On Command

`concise-default` makes new agent sessions start in concise mode.

```sh
concise-default on ultra
concise-default status
concise-default off
```

Valid levels: `lite`, `ultra`.

What it writes:

- Cursor: `~/.cursor/rules/concise.mdc`
- Claude Code: marked block in `~/.claude/CLAUDE.md`
- Codex CLI: `~/.codex/instructions.md`
- Saved level: `~/.config/concise/config`

Codex detail: `concise-default on` writes the full concise skill body into `~/.codex/instructions.md`. New Codex sessions splice that file into `base_instructions`. It does not change the current conversation retroactively.

`concise-default status` separates two Codex states:

- `Codex CLI: ON`: `~/.codex/instructions.md` exists.
- `Codex App: ON`: the most recent Codex session appears to include that instruction text.

## Levels

- `lite`: expression compression only
- `ultra`: expression compression + content filtering

`ultra` keeps only incremental information, leads with the conclusion, avoids restating the user's request, and expands only when the user asks for analysis, details, causes, or boundaries.

## Boundaries

The skill intentionally relaxes compression when clarity matters more:

- safety warnings
- irreversible operations
- multi-step instructions where order matters
- parameter-heavy or branch-heavy explanations
- repeated follow-up questions
- explicit requests for analysis or edge cases

Code blocks, commit messages, and PR bodies stay normal unless the user asks to compress them.

## Test

```sh
python -m unittest discover -s tests -v
```

## Example

User:

```text
Explain why this React component re-renders.
```

Normal:

```text
This component is probably re-rendering because a new object reference is being created on each render, which causes React to treat the prop as changed.
```

Concise `ultra`:

```text
inline obj prop -> new ref -> re-render. Wrap with useMemo.
```

## Repo Layout

```text
.
|-- SKILL.md
|-- bin/
|-- skills/
|-- tests/
|-- README.md
|-- LICENSE
`-- .gitignore
```

## License

MIT


