#!/usr/bin/env sh
# 用途：安装唯一 concise 规则；新环境启用 Codex 全局默认注入时运行；避免手工漏写 hook/config。

set -e

REPO_RAW="https://raw.githubusercontent.com/Cpp1022/concise/main"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

case "${1:-codex}" in
  codex) ;;
  *) echo "usage: install.sh [codex]" >&2; exit 2 ;;
esac

mkdir -p "$TMP"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd || pwd)
if [ -f "$SCRIPT_DIR/SKILL.md" ]; then
  cp "$SCRIPT_DIR/SKILL.md" "$TMP/SKILL.md"
else
  curl -fsSL "$REPO_RAW/SKILL.md" -o "$TMP/SKILL.md"
fi

codex_dir="$HOME/.codex"
hook_dir="$codex_dir/hooks"
hook_file="$hook_dir/concise-user-prompt-submit.sh"
hooks_json="$codex_dir/hooks.json"
config_toml="$codex_dir/config.toml"

mkdir -p "$hook_dir"
cp "$TMP/SKILL.md" "$codex_dir/instructions.md"

cat > "$hook_file" <<'HOOK'
#!/usr/bin/env sh
printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"concise: 先结论；1-2句；禁计划/禁tool旁白/禁Why-How清单。"}}'
HOOK
chmod +x "$hook_file"

HOOK_COMMAND='"$HOME/.codex/hooks/concise-user-prompt-submit.sh"' HOOKS_JSON="$hooks_json" python3 - <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["HOOKS_JSON"])
command = os.environ["HOOK_COMMAND"]
if path.exists():
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        data = {}
else:
    data = {}

hooks = data.setdefault("hooks", {})
event = hooks.setdefault("UserPromptSubmit", [])
entry = {"hooks": [{"type": "command", "command": command}]}

def has_concise(item):
    return any("concise-user-prompt-submit" in h.get("command", "") for h in item.get("hooks", []))

event[:] = [item for item in event if not has_concise(item)]
event.insert(0, entry)
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
PY

CONFIG_TOML="$config_toml" python3 - <<'PY'
import os
from pathlib import Path

path = Path(os.environ["CONFIG_TOML"])
text = path.read_text() if path.exists() else ""
lines = text.splitlines()
out = []
in_features = False
features_seen = False
codex_seen = False

for line in lines:
    stripped = line.strip()
    if stripped.startswith("[") and stripped.endswith("]"):
        if in_features and not codex_seen:
            out.append("codex_hooks = true")
        in_features = stripped == "[features]"
        if in_features:
            features_seen = True
            codex_seen = False
    if in_features and stripped.startswith("codex_hooks"):
        out.append("codex_hooks = true")
        codex_seen = True
    else:
        out.append(line)

if in_features and not codex_seen:
    out.append("codex_hooks = true")
elif not features_seen:
    if out and out[-1].strip():
        out.append("")
    out.extend(["[features]", "codex_hooks = true"])

path.write_text("\n".join(out).rstrip() + "\n")
PY

printf 'installed: %s\n' "$codex_dir/instructions.md"
printf 'installed: %s\n' "$hook_file"
printf 'updated: %s\n' "$hooks_json"
printf 'updated: %s\n' "$config_toml"
