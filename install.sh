#!/usr/bin/env sh
# concise installer
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh
#   curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- --default lite
#
# Installs the `concise` skill into every supported agent location.
# Default behavior: installs the Codex CLI wrapper that injects concise + AGENTS.md on every run.
# Optional: --default <lite|ultra> also installs `concise-default` for generated defaults on Cursor / Claude Code / Codex App.

set -e

REPO_RAW="https://raw.githubusercontent.com/Cpp1022/concise/main"
TMP="$(mktemp -d)"
DEFAULT_LEVEL=""

while [ $# -gt 0 ]; do
  case "$1" in
    --default)
      if [ $# -ge 2 ] && [ "${2#--}" = "$2" ]; then
        DEFAULT_LEVEL="$2"
        shift 2
      else
        DEFAULT_LEVEL="ultra"
        shift
      fi
      continue
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
fetch "$TMP/concise/REINFORCE.md"                          "concise/REINFORCE.md"
fetch "$TMP/concise/DETAIL.md"                             "concise/DETAIL.md"
fetch "$TMP/concise/scripts/codex"                         "concise/scripts/codex"
fetch "$TMP/concise-default/SKILL.md"                      "concise-default/SKILL.md"
fetch "$TMP/concise-default/scripts/concise-default.py"    "concise-default/scripts/concise-default.py"
fetch "$TMP/concise-default/scripts/concise-default.sh"    "concise-default/scripts/concise-default.sh"

install_skill() {
  skill="$1"; dst="$2"
  mkdir -p "$dst"
  cp -R "$TMP/$skill/." "$dst/"
  printf "    installed: %s\n" "$dst/"
}

echo "==> installing concise skill"
install_skill concise "$HOME/.codex/skills/concise"
mkdir -p "$HOME/.codex/bin"
cp "$TMP/concise/scripts/codex"                            "$HOME/.codex/bin/codex"
chmod +x "$HOME/.codex/bin/codex"
[ -d "$HOME/.claude" ]          && install_skill concise "$HOME/.claude/skills/concise"              || true
[ -d "$HOME/.config/opencode" ] && install_skill concise "$HOME/.config/opencode/skills/concise"     || true
[ -d "$HOME/.copilot" ]         && install_skill concise "$HOME/.copilot/skills/concise"             || true

if [ -n "$DEFAULT_LEVEL" ]; then
  echo "==> installing concise-default and enabling generated defaults level=$DEFAULT_LEVEL"
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
  - Codex CLI now uses wrapper chain:
      concise skill -> AGENTS.md -> AGENTS.override.md
  - in-chat:   /concise  |  /concise lite  |  /concise ultra  |  stop concise
  - optional generated defaults:
      ~/.codex/bin/concise-default on ultra
  - uninstall:
      rm -f ~/.codex/bin/codex
      rm -rf ~/.codex/skills/concise ~/.codex/skills/concise-default ~/.claude/skills/concise

docs: https://github.com/Cpp1022/concise
EOF
