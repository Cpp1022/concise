# concise

Chinese concise-response skill suite for Codex-style agents.

## Which should I use?

- Use `concise` when you want the current chat to become concise.
- Use `concise-default` when you want every new chat to start concise.

`concise` controls response style. `concise-default` is a setup helper that installs that style into new-session instructions.

## Install

### 1. Install the `concise` skill

Windows:

```powershell
mkdir $env:USERPROFILE\.codex\skills\concise -Force
copy concise\SKILL.md $env:USERPROFILE\.codex\skills\concise\SKILL.md
```

Unix-like:

```sh
mkdir -p ~/.codex/skills/concise
cp concise/SKILL.md ~/.codex/skills/concise/SKILL.md
```

### 2. Optional: install `concise-default`

Install this only if you want a command that turns concise mode on for every new chat.

Windows:

```powershell
mkdir $env:USERPROFILE\.codex\skills\concise-default -Force
copy concise-default\SKILL.md $env:USERPROFILE\.codex\skills\concise-default\SKILL.md

mkdir $env:USERPROFILE\.codex\bin -Force
copy concise-default\scripts\concise-default.py $env:USERPROFILE\.codex\bin\concise-default.py
copy concise-default\scripts\concise-default.cmd $env:USERPROFILE\.codex\bin\concise-default.cmd
```

Unix-like:

```sh
mkdir -p ~/.codex/skills/concise-default ~/.codex/bin
cp concise-default/SKILL.md ~/.codex/skills/concise-default/SKILL.md
cp concise-default/scripts/concise-default.py ~/.codex/bin/concise-default.py
cp concise-default/scripts/concise-default.sh ~/.codex/bin/concise-default
chmod +x ~/.codex/bin/concise-default
```

Add `~/.codex/bin` to `PATH`, or run the wrapper by full path.

## Usage

### Current chat

Use these in chat:

```text
/concise
/concise lite
/concise ultra
stop concise
normal mode
```

Levels:

- `lite`: expression compression only
- `ultra`: expression compression + content filtering

Default: `ultra`.

### New chats by default

Use these in shell:

```sh
concise-default on ultra
concise-default status
concise-default off
```

Valid levels: `lite`, `ultra`.

## What `concise` does

It makes agent responses shorter and denser while preserving technical accuracy and decision quality.

Use it when you want an agent to:

- use fewer tokens
- reduce filler and repetition
- keep conclusions first
- stay compact in Chinese technical writing
- avoid repeated conclusions and unasked-for expansion

`ultra` keeps only incremental information, leads with the conclusion, avoids restating the user's request, and expands only when the user asks for analysis, details, causes, or boundaries.

## What `concise-default` writes

- Cursor: `~/.cursor/rules/concise.mdc`
- Claude Code: marked block in `~/.claude/CLAUDE.md`
- Codex CLI: `~/.codex/instructions.md`
- Saved level: `~/.config/concise/config`

Codex detail: `concise-default on` writes the full `concise` skill body into `~/.codex/instructions.md`. New Codex sessions splice that file into `base_instructions`. It does not change the current conversation retroactively.

`concise-default status` separates two Codex states:

- `Codex CLI: ON`: `~/.codex/instructions.md` exists.
- `Codex App: ON`: the most recent Codex session appears to include that instruction text.

## Boundaries

The skill intentionally relaxes compression when clarity matters more:

- safety warnings
- irreversible operations
- multi-step instructions where order matters
- parameter-heavy or branch-heavy explanations
- repeated follow-up questions
- explicit requests for analysis or edge cases

Code blocks, commit messages, and PR bodies stay normal unless the user asks to compress them.

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

## Repo layout

```text
.
|-- concise/
|   `-- SKILL.md
|-- concise-default/
|   |-- SKILL.md
|   `-- scripts/
|       |-- concise-default.py
|       |-- concise-default.cmd
|       `-- concise-default.sh
|-- README.md
|-- CHANGELOG.md
|-- CONTRIBUTING.md
|-- SECURITY.md
|-- LICENSE
`-- .gitignore
```

## License

MIT