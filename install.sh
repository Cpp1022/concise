#!/usr/bin/env sh
# concise installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh
#   curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- --default ultra
#
# Installs the `concise` skill into every supported agent location.
# Optional: --default <lite|ultra> also installs the `concise-default` wrapper
# and turns concise on for all new sessions.

set -e

REPO_RAW="https://raw.githubusercontent.com/Cpp1022/concise/main"
TMP="$(mktemp -d)"
DEFAULT_LEVEL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --default)
      shift
      DEFAULT_LEVEL="${1:-ultra}"
      ;;
    --default=*)
      DEFAULT_LEVEL="${1#--default=}"
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 2
      ;;
  esac
  shift
done

fetch() {
  out="$1"; src="$2"
  mkdir -p "$(dirname "$out")"
  curl -fsSL "$REPO_RAW/$src" -o "$out"
}

echo "==> downloading skill sources"
fetch "$TMP/concise/SKILL.md"                              "concise/SKILL.md"
fetch "$TMP/concise-default/SKILL.md"                      "concise-default/SKILL.md"
fetch "$TMP/concise-default/scripts/concise-default.py"    "concise-default/scripts/concise-default.py"
fetch "$TMP/concise-default/scripts/concise-default.sh"    "concise-default/scripts/concise-default.sh"

install_skill() {
  skill="$1"; dst="$2"
  mkdir -p "$dst"
  cp "$TMP/$skill/SKILL.md" "$dst/SKILL.md"
  printf "    installed: %s\n" "$dst/SKILL.md"
}

echo "==> installing concise skill"
install_skill concise "$HOME/.codex/skills/concise"
[ -d "$HOME/.claude" ]          && install_skill concise "$HOME/.claude/skills/concise"              || true
[ -d "$HOME/.config/opencode" ] && install_skill concise "$HOME/.config/opencode/skills/concise"     || true
[ -d "$HOME/.copilot" ]         && install_skill concise "$HOME/.copilot/skills/concise"             || true

if [ -n "$DEFAULT_LEVEL" ]; then
  echo "==> installing concise-default and enabling level=$DEFAULT_LEVEL"
  mkdir -p "$HOME/.codex/skills/concise-default" "$HOME/.codex/bin"
  cp "$TMP/concise-default/SKILL.md"                      "$HOME/.codex/skills/concise-default/SKILL.md"
  cp "$TMP/concise-default/scripts/concise-default.py"    "$HOME/.codex/bin/concise-default.py"
  cp "$TMP/concise-default/scripts/concise-default.sh"    "$HOME/.codex/bin/concise-default"
  chmod +x "$HOME/.codex/bin/concise-default"
  "$HOME/.codex/bin/concise-default" on "$DEFAULT_LEVEL" || true
fi

rm -rf "$TMP"

cat <<'EOF'

done.

next:
  - new chats in Codex / Claude Code / Cursor can now load the `concise` skill
  - in-chat:   /concise  |  /concise lite  |  /concise ultra  |  stop concise
  - default on every new chat:
      ~/.codex/bin/concise-default on ultra        (if installed via --default)
  - uninstall:
      rm -rf ~/.codex/skills/concise ~/.claude/skills/concise ~/.cursor/rules/concise.mdc

docs: https://github.com/Cpp1022/concise
EOF
