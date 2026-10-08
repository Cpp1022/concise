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

## 安装与使用

concise 使用同一套表达规则，不同 Agent 的安装和生效方式不同。

| 使用的平台 | 安装入口 | 安装后如何生效 |
|---|---|---|
| **Codex** | 使用下方安装脚本 | 配置持续注入，无需每轮提醒 |
| **其他支持技能的 Agent** | 通过技能安装器安装 | 按平台机制自动匹配或手动调用；不保证持续启用 |

### Codex

需要 Python 3.11+。安装脚本保留已有指令，在 concise 标记块中写入规则，并配置持续注入。

**Windows PowerShell**

```powershell
irm https://raw.githubusercontent.com/Cpp1022/concise/main/install.ps1 | iex
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- codex
```

### 其他 Agent

通过技能安装器安装，按所用平台选择：

```bash
npx skills add Cpp1022/concise --skill concise
```

无需运行上述 Codex 安装脚本。安装后的调用与持续生效方式，取决于平台。

[查看各平台安装、启用与卸载说明](INSTALL.md)
