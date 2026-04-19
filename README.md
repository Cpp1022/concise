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

Copy this repository's `SKILL.md` into your local Codex skills directory:

```text
~/.codex/skills/concise/SKILL.md
```

On Windows, that is typically:

```text
C:\Users\<you>\.codex\skills\concise\SKILL.md
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
|-- README.md
|-- LICENSE
`-- .gitignore
```

## License

MIT


