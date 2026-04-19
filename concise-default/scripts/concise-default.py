from __future__ import annotations

import re
import shutil
import sys
import json
from pathlib import Path


HOME = Path.home()
CONFIG_FILE = HOME / ".config" / "concise" / "config"
SKILL_SOURCE = HOME / ".codex" / "skills" / "concise" / "SKILL.md"
CURSOR_RULE = HOME / ".cursor" / "rules" / "concise.mdc"
CLAUDE_MD = HOME / ".claude" / "CLAUDE.md"
CODEX_INSTRUCTIONS = HOME / ".codex" / "instructions.md"
CODEX_SESSIONS = HOME / ".codex" / "sessions"
MARKER_START = "# >>> concise-default >>>"
MARKER_END = "# <<< concise-default <<<"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def get_level() -> str:
    if CONFIG_FILE.exists():
        level = CONFIG_FILE.read_text(encoding="utf-8").strip()
        if level in {"lite", "ultra"}:
            return level
    return "ultra"


def save_level(level: str) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(level + "\n", encoding="utf-8", newline="\n")


def read_skill_body() -> str:
    if not SKILL_SOURCE.exists():
        raise SystemExit(f"Error: source not found: {SKILL_SOURCE}")
    text = read_text(SKILL_SOURCE)
    parts = text.split("---", 2)
    return parts[2].lstrip("\r\n") if len(parts) >= 3 else text


def patch_level(body: str, level: str) -> str:
    body = re.sub(r"默认：\*\*(lite|ultra)\*\*", f"默认：**{level}**", body)
    body = re.sub(r"默认:\s*\*\*(lite|ultra)\*\*", f"默认：**{level}**", body)
    return body


def gen_cursor_content(level: str) -> str:
    body = patch_level(read_skill_body(), level)
    return "\n".join(
        [
            "---",
            f'description: "Concise mode ({level})"',
            "alwaysApply: true",
            "---",
            body.rstrip(),
            "",
        ]
    )


def gen_plain_content(level: str) -> str:
    return patch_level(read_skill_body(), level).rstrip() + "\n"


def first_signal_line(path: Path) -> str | None:
    if not path.exists():
        return None
    for line in read_text(path).splitlines():
        stripped = line.strip()
        if stripped and stripped not in {MARKER_START, MARKER_END}:
            return stripped
    return None


def latest_session_file(sessions_dir: Path) -> Path | None:
    if not sessions_dir.exists():
        return None
    files = [p for p in sessions_dir.rglob("*.jsonl") if p.is_file()]
    return max(files, key=lambda p: (p.stat().st_mtime_ns, str(p))) if files else None


def codex_app_on_from_last_session(sessions_dir: Path, instructions_path: Path) -> bool:
    signal = first_signal_line(instructions_path)
    latest = latest_session_file(sessions_dir)
    if not signal or latest is None:
        return False
    try:
        with latest.open("r", encoding="utf-8-sig") as fh:
            first_line = fh.readline()
        if not first_line:
            return False
        record = json.loads(first_line)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    text = record.get("payload", {}).get("base_instructions", {}).get("text", "")
    return signal in text


def remove_marked_block(path: Path) -> None:
    if not path.exists():
        return
    text = read_text(path)
    pattern = re.compile(
        rf"\n*{re.escape(MARKER_START)}\n.*?\n{re.escape(MARKER_END)}\n*",
        re.DOTALL,
    )
    updated = re.sub(pattern, "\n", text).strip()
    if updated:
        write_text(path, updated + "\n")
    elif path.exists():
        path.unlink()


def inject_marked_block(path: Path, content: str) -> None:
    existing = read_text(path).rstrip() if path.exists() else ""
    block = f"{MARKER_START}\n{content.rstrip()}\n{MARKER_END}"
    if MARKER_START in existing:
        return
    if existing:
        write_text(path, existing + "\n\n" + block + "\n")
    else:
        write_text(path, block + "\n")


def cmd_on(level: str | None) -> int:
    chosen = level or get_level()
    if chosen not in {"lite", "ultra"}:
        raise SystemExit(f"Error: level must be lite or ultra (got: {chosen})")
    save_level(chosen)
    write_text(CURSOR_RULE, gen_cursor_content(chosen))
    remove_marked_block(CLAUDE_MD)
    inject_marked_block(CLAUDE_MD, gen_plain_content(chosen))
    write_text(CODEX_INSTRUCTIONS, gen_plain_content(chosen))
    print(f"  OK Cursor: {CURSOR_RULE}")
    print(f"  OK Claude Code: {CLAUDE_MD}")
    print(f"  OK Codex CLI: {CODEX_INSTRUCTIONS}")
    print()
    print(f"concise default ON (level: {chosen}). Source: {SKILL_SOURCE}")
    return 0


def cmd_off() -> int:
    if CURSOR_RULE.exists():
        CURSOR_RULE.unlink()
    remove_marked_block(CLAUDE_MD)
    if CODEX_INSTRUCTIONS.exists():
        CODEX_INSTRUCTIONS.unlink()
    print("  OK Cursor: removed")
    print("  OK Claude Code: removed")
    print("  OK Codex CLI: removed")
    print()
    print("concise default OFF.")
    return 0


def cmd_status() -> int:
    level = get_level()
    print(f"concise-default status (saved level: {level}):")
    print(f"  Source: {SKILL_SOURCE}")
    print(f"  Cursor: {'ON' if CURSOR_RULE.exists() else 'OFF'}")
    claude_on = CLAUDE_MD.exists() and MARKER_START in read_text(CLAUDE_MD)
    print(f"  Claude Code: {'ON' if claude_on else 'OFF'}")
    print(f"  Codex CLI: {'ON' if CODEX_INSTRUCTIONS.exists() else 'OFF'}")
    print(
        f"  Codex App: {'ON' if codex_app_on_from_last_session(CODEX_SESSIONS, CODEX_INSTRUCTIONS) else 'OFF'}"
    )
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: concise-default <on|off|status> [level]")
        return 1
    cmd = argv[1]
    if cmd == "on":
        return cmd_on(argv[2] if len(argv) > 2 else None)
    if cmd == "off":
        return cmd_off()
    if cmd == "status":
        return cmd_status()
    print("Usage: concise-default <on|off|status> [level]")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
