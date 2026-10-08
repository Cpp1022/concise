# concise

concise 是一个主要针对 Agent 中文回复的简洁表达技能：先给结论，减少冗长铺垫、套话、重复内容和无意义黑话，让中文回答更直接、更好读，降低阅读负担。

**concise 提供通用的中文简洁表达规则。** Codex 版安装后默认持续注入，无需每轮提醒；其他支持技能加载的 Agent 可使用 [`skills/concise/SKILL.md`](skills/concise/SKILL.md)，持续生效方式与遵循程度取决于平台。

## 回复篇幅与 token 对比

| 设置 | 最终回复字符 | 旁白条数 | 整轮生成 token |
|---|---:|---:|---:|
| concise | 146 | 0 | 397 |
| Codex 原生简洁高效回复模式 | 1184 | 2 | 2281 |
| 每次提示“请简洁回复” | 435 | 2 | 1083 |

[查看完整回复对比与测试说明](回复对比.md)

用途索引：`README.md` 说明唯一规则源与 Codex 全局默认注入安装；新环境安装、改规则、排查注入失效时读；避免文档和安装入口分叉。

## 文档用途索引

- [`skills/concise/SKILL.md`](skills/concise/SKILL.md)：唯一规则源；改规则前读。
- `install.sh`：Unix/macOS/Linux 安装入口；启用 Codex 全局默认注入时读；避免手工漏写 hook/config。
- `install.ps1`：Windows 安装入口；启用 Codex 全局默认注入时读；避免手工漏写 hook/config。
- `LICENSE`：开源授权条款；分发、引用、改造前读；说明允许的使用边界。

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

## 卸载

```sh
rm -f ~/.codex/instructions.md ~/.codex/hooks/concise-user-prompt-submit.sh
# 同时删除 ~/.codex/hooks.json 里的 concise UserPromptSubmit 条目；不再需要 hook 时删除 ~/.codex/config.toml 的 codex_hooks 行。
```

```powershell
Remove-Item "$env:USERPROFILE\.codex\instructions.md", "$env:USERPROFILE\.codex\hooks\concise-user-prompt-submit.ps1" -ErrorAction SilentlyContinue
# 同时删除 $env:USERPROFILE\.codex\hooks.json 里的 concise UserPromptSubmit 条目；不再需要 hook 时删除 config.toml 的 codex_hooks 行。
```
