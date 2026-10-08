# 安装与启用 concise

concise 的表达规则位于 [`skills/concise/SKILL.md`](skills/concise/SKILL.md)。安装方式取决于你使用的 Agent；安装了技能，并不意味着平台会在每轮回复中自动加载它。

## Codex：默认持续生效

安装脚本负责写入规则及配置持续注入，无需手工设置 hook。

**Windows PowerShell**

```powershell
irm https://raw.githubusercontent.com/Cpp1022/concise/main/install.ps1 | iex
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- codex
```

这是 Codex 的平台适配方式，不是其他 Agent 使用 concise 的前提。

## 其他 Agent：通过技能功能加载

| 平台 | 安装命令 |
|---|---|
| Claude Code | `npx skills add Cpp1022/concise --skill concise -a claude-code` |
| Cursor | `npx skills add Cpp1022/concise --skill concise -a cursor` |
| Gemini CLI | `npx skills add Cpp1022/concise --skill concise -a gemini-cli` |
| OpenCode | `npx skills add Cpp1022/concise --skill concise -a opencode` |

以上命令默认安装到当前项目；添加 `-g` 可安装到用户全局范围。

安装后只包含技能文件，不会执行 Codex 安装脚本或修改 Codex 配置。无需创建 `.codex` 下的配置文件。

使用时明确要求 Agent“使用 concise 技能”；是否自动匹配、是否需要再次调用，取决于平台。

## Codex 配置细节

Codex 必须同时具备：`~/.codex/instructions.md` 规则全文；`~/.codex/hooks.json` 注册 `UserPromptSubmit` context hook，命令指向 concise hook；`~/.codex/config.toml` 含 `[features] codex_hooks = true`。

## Codex 卸载

```sh
rm -f ~/.codex/instructions.md ~/.codex/hooks/concise-user-prompt-submit.sh
# 同时删除 ~/.codex/hooks.json 里的 concise UserPromptSubmit 条目；不再需要 hook 时删除 ~/.codex/config.toml 的 codex_hooks 行。
```

```powershell
Remove-Item "$env:USERPROFILE\.codex\instructions.md", "$env:USERPROFILE\.codex\hooks\concise-user-prompt-submit.ps1" -ErrorAction SilentlyContinue
# 同时删除 $env:USERPROFILE\.codex\hooks.json 里的 concise UserPromptSubmit 条目；不再需要 hook 时删除 config.toml 的 codex_hooks 行。
```
