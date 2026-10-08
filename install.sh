#!/usr/bin/env sh
# Install or uninstall the Codex adapter; the skill itself remains platform-neutral.
set -eu
case "${1:-codex}" in codex|uninstall) action="${1:-codex}" ;; *) echo 'usage: install.sh [codex|uninstall]' >&2; exit 2 ;; esac
command -v python3 >/dev/null 2>&1 || { echo 'concise requires Python 3.11+; no Codex configuration was changed.' >&2; exit 1; }
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)' || { echo 'concise requires Python 3.11+; no Codex configuration was changed.' >&2; exit 1; }
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || pwd)
if [ -f "$0" ] && [ -f "$SCRIPT_DIR/install.py" ] && { [ "$action" = uninstall ] || [ -f "$SCRIPT_DIR/skills/concise/SKILL.md" ]; }; then
  exec python3 "$SCRIPT_DIR/install.py" "$action"
fi
command -v curl >/dev/null 2>&1 || { echo 'curl is required to download concise.' >&2; exit 1; }
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
BASE='https://raw.githubusercontent.com/Cpp1022/concise/main'
curl -fsSL "$BASE/install.py" -o "$TMP/install.py"
if [ "$action" = codex ]; then
  curl -fsSL "$BASE/skills/concise/SKILL.md" -o "$TMP/SKILL.md"
  python3 "$TMP/install.py" codex --skill-file "$TMP/SKILL.md"
else
  python3 "$TMP/install.py" uninstall
fi
