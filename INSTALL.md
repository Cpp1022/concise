# 安装与启用 concise

concise 的表达规则位于 [`skills/concise/SKILL.md`](skills/concise/SKILL.md)。安装方式取决于你使用的 Agent；安装了技能，并不意味着平台会在每轮回复中自动加载它。

## Codex：默认持续生效

需要 Python 3.11+（Windows 同样需要；macOS / Linux 使用 `python3`）。安装脚本将完整规则追加到 Codex 的开发者指令配置，并创建每轮简短提醒的 hook；缺少依赖时，在修改配置前停止。

**Windows PowerShell**

```powershell
irm https://raw.githubusercontent.com/Cpp1022/concise/main/install.ps1 | iex
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- codex
```

安装完成后新开 Codex 会话，使新配置加载；已有会话不会因安装自动重新加载配置。完整规则随开发者指令进入会话，无需依赖个人启动脚本。

每轮简短提醒需要在 `/hooks` 中检查并信任 concise hook；确认其显示为已信任、已启用。脚本不会绕过 Codex 的 hook 信任机制。

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

## Codex 配置与恢复

默认配置目录是 `~/.codex`；设置了 `CODEX_HOME` 时使用该目录。

- `instructions.md`：保留已有指令，追加 concise 标记块；更新只替换该块。Codex 不会仅凭这个文件名自动加载规则，实际加载由下方开发者指令配置完成。
- `hooks.json`：合并 concise 的 `UserPromptSubmit` hook，保留其他 hook；配置解析失败时停止。
- `config.toml`：在原有 `developer_instructions` 后追加完整 concise 标记块，保留用户原有指令；不修改 `model_instructions_file`，不替换 Codex 内置指令。将 `[features]` 中的 `codex_hooks` 设为 `true`，保留其他设置与注释。需要修改的设置使用内联表、点分键或文件含多行字符串时，脚本会拒绝自动修改，保留原配置并提示。
- `.concise-install/state.json`：记录安装前文件的字节快照、安装后内容及恢复依据；不要手动删除。
- `.concise-install/pending.json`：记录尚未完成的修改；发生可恢复错误时回滚，进程中断后下次运行先检查并恢复。若发现新的用户修改，则停止并保留恢复记录。

若用户的 profile 单独设置了 `developer_instructions`，安装会停止并提示，避免覆盖该设置或误报生效。项目配置、命令行参数及平台额外指令仍可能覆盖全局配置。

重复安装会更新 concise，并保留原始备份及用户新增内容。遇到被修改的 concise 规则块、hook 文件或条目时停止，避免覆盖用户修改。

没有安装记录的旧版内容不会被自动接管或删除；应先备份并核对。旧脚本已经覆盖掉、且没有备份的指令无法自动恢复。

## Codex 卸载

**Windows PowerShell**

```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/Cpp1022/concise/main/install.ps1))) -Action uninstall
```

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/Cpp1022/concise/main/install.sh | sh -s -- uninstall
```

卸载只移除 concise 管理的规则块（含开发者指令中的标记块）、hook 条目和文件，保留用户其他内容；不要直接删除整个 `instructions.md`。

如果其他 hook 可能依赖 `codex_hooks`，或该设置已被用户修改，卸载会保留当前设置及恢复记录并提示；其余情况下恢复原值。发生冲突时保留备份与记录，不强行覆盖。
