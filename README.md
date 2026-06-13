# concise

用途索引：`README.md` 说明唯一规则源与 Codex 全局默认注入安装；新环境安装、改规则、排查注入失效时读；避免文档和安装入口分叉。

## 文档用途索引

- `SKILL.md`：唯一规则源；改规则前读；必须与 `~/.codex/instructions.md` 一致。
- `install.sh`：Unix/macOS/Linux 安装入口；启用 Codex 全局默认注入时读；避免手工漏写 hook/config。
- `install.ps1`：Windows 安装入口；启用 Codex 全局默认注入时读；避免手工漏写 hook/config。
- `LICENSE`：开源授权条款；分发、引用、改造前读；说明允许的使用边界。

## 规则治理

只保留 `SKILL.md` 一个入口；不维护 `concise-default`，不提供等级分档入口。

## Codex 全局默认注入

Codex 必须同时具备：`~/.codex/instructions.md` 规则全文；`~/.codex/hooks.json` 注册 `UserPromptSubmit` context hook，命令指向 concise hook；`~/.codex/config.toml` 含 `[features] codex_hooks = true`。

## 安装

```sh
# Unix/macOS/Linux
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- codex
```

```powershell
# Windows PowerShell
irm https://raw.githubusercontent.com/Cpp1022/concise/main/install.ps1 | iex
```

## 本地同步

```sh
cp ~/.codex/instructions.md SKILL.md
cmp SKILL.md ~/.codex/instructions.md
```

## 卸载

```sh
rm -f ~/.codex/instructions.md ~/.codex/hooks/concise-user-prompt-submit.sh
# 同时删除 ~/.codex/hooks.json 里的 concise UserPromptSubmit 条目；不再需要 hook 时删除 ~/.codex/config.toml 的 codex_hooks 行。
```

```powershell
Remove-Item "$env:USERPROFILE\.codex\instructions.md", "$env:USERPROFILE\.codex\hooks\concise-user-prompt-submit.ps1" -ErrorAction SilentlyContinue
# 同时删除 $env:USERPROFILE\.codex\hooks.json 里的 concise UserPromptSubmit 条目；不再需要 hook 时删除 config.toml 的 codex_hooks 行。
```
