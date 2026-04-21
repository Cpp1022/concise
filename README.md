# concise

> A Chinese-first `SKILL.md` for AI coding agents.
> 让 Claude Code / Codex CLI / Cursor 用中文回复更短更密，不丢技术判断。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![platforms](https://img.shields.io/badge/platforms-Codex%20CLI%20%7C%20Claude%20Code%20%7C%20Cursor-green)

## 30-second install

```sh
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh
# or: enable "every new chat starts concise" in addition to installing the skill
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- --default ultra
```

In chat:

```text
/concise          # enable ultra (default) for this chat
/concise lite     # expression compression only
/concise ultra    # expression + content compression
stop concise      # back to normal
```

## Why concise?

- **Chinese-first**: tuned for Chinese technical writing; `ultra` cuts 60-80% of non-code tokens in Chinese, 20-30% in English.
- **Preserves precision**: code blocks, error output, command parameters, commit messages, and PR bodies stay verbatim.
- **Auto-relax**: backs off compression for safety warnings, multi-step procedures, parameter-heavy explanations, and ambiguous cases.
- **Cross-agent**: one `SKILL.md`, three install targets — Codex CLI, Claude Code, Cursor.

## FAQ

**Q: How is this different from a "be brief" system prompt?**
A: "Be brief" compresses wording but keeps the same output structure (intro / sections / recap). concise strips the structure too, and separates expression compression from content compression, so precision doesn't drop with filler.

**Q: Will this make the agent think less?**
A: No. The skill only controls output style, not tool use or reasoning depth. TDD, debugging, and brainstorming workflows auto-relax when they need to expand.

**Q: Does it conflict with my own Cursor rules?**
A: No. concise lives at the response-style layer; your project rules live at the code-style / architecture layer. Both can be on at the same time.

**Q: Can I enable it only for specific chats?**
A: Yes. Install only `concise` (not `concise-default`), then use `/concise` in the chats where you want it.

Suggested GitHub topics:

```text
agent-skills
skill-md
codex
codex-cli
claude-code
cursor-rules
ai-coding-agent
concise-mode
developer-productivity
```

## Which should I use?

- Use `concise` when you want the current chat to become concise.
- Use `concise-default` when you want every new chat to start concise.

`concise` controls response style. `concise-default` is a setup helper that installs that style into new-session instructions.

## Platform support

| Platform | Status | Notes |
| --- | --- | --- |
| Codex CLI | Supported | Native `SKILL.md` install target. `concise-default` writes `~/.codex/instructions.md`. |
| Claude Code | Supported as target | `concise-default` writes a managed block in `~/.claude/CLAUDE.md`. The repo includes a Claude Code plugin manifest. |
| Cursor | Supported as rules target | `concise-default` writes `~/.cursor/rules/concise.mdc`. Cursor uses Rules, not native `SKILL.md`. |
| OpenCode | SKILL.md-compatible, not yet a target | OpenCode can load `SKILL.md` from supported skill paths, but `concise-default` does not yet write OpenCode defaults. |
| GitHub Copilot / VS Code | SKILL.md-compatible, not yet a target | Copilot skills use `.github/skills/` or `~/.copilot/skills/`; `concise-default` does not yet write Copilot defaults. |

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

### Other agent locations

These locations install the `SKILL.md` files for discovery. The `concise-default` command still needs the wrapper from `concise-default/scripts/` on `PATH` if you want shell toggles.

Claude Code:

```sh
mkdir -p ~/.claude/skills
cp -r concise ~/.claude/skills/concise
cp -r concise-default ~/.claude/skills/concise-default
```

OpenCode:

```sh
mkdir -p ~/.config/opencode/skills
cp -r concise ~/.config/opencode/skills/concise
cp -r concise-default ~/.config/opencode/skills/concise-default
```

GitHub Copilot / VS Code:

```sh
mkdir -p ~/.copilot/skills
cp -r concise ~/.copilot/skills/concise
cp -r concise-default ~/.copilot/skills/concise-default
```

Project-level Copilot skills can also live under `.github/skills/`.

Cursor does not load `SKILL.md` directly. Use `concise-default on` to generate `~/.cursor/rules/concise.mdc`.

### Claude Code plugin

This repository includes `.claude-plugin/plugin.json`, so it can be used as a Claude Code plugin source or listed from a Claude Code plugin marketplace. For a marketplace listing, point the plugin source at this GitHub repository.

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

## Distribution

This repo is structured for skill directories and marketplaces that accept `SKILL.md`-based agent skills.

Initial publishing targets:

- SkillsMD
- Skillzwave
- SKILLS.pub
- Bogen

After collecting usage feedback:

- OpenAI Skills Catalog
- LLMSkills
- Agent Skills Finder
- Cursor rules directories and awesome lists
- GitHub Copilot / VS Code awesome lists

When submitting, link to this GitHub repository as the source of truth. Marketplace pages should describe `Codex CLI` as the primary supported platform, with `Claude Code` and `Cursor Rules` as generated default targets.

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
|-- .claude-plugin/
|   `-- plugin.json
|-- concise/
|   `-- SKILL.md
|-- concise-default/
|   |-- SKILL.md
|   `-- scripts/
|       |-- concise-default.py
|       |-- concise-default.cmd
|       `-- concise-default.sh
|-- README.md
|-- LICENSE
`-- .gitignore
```

## License

MIT
