# concise

concise 是一个主要针对 Agent 中文回复的简洁表达技能：先给结论，减少冗长铺垫、套话、重复内容和无意义黑话，让中文回答更直接、更好读，降低阅读负担。

## 回复篇幅与 token 对比

| 设置 | 最终回复字符 | 旁白条数 | 整轮生成 token |
|---|---:|---:|---:|
| concise | 146 | 0 | 397 |
| Codex 原生简洁高效回复模式 | 1184 | 2 | 2281 |
| 每次提示“请简洁回复” | 435 | 2 | 1083 |

## 装了 concise，Agent 的中文回复会有什么不同？

同一个问题，对比使用 concise、开启 Codex 原生简洁高效回复模式，以及每次提示“请简洁回复”三种方式的回答。

- **concise**：加载 concise 技能原文规则，不额外启用原生回复风格或添加简洁提示。
- **Codex 原生简洁高效回复模式**：设置 `personality="pragmatic"`，不加载 concise，也不添加简洁提示。
- **每次提示“请简洁回复”**：不加载 concise，不启用原生回复风格，在提问前加“请简洁回复，先说结论，少说废话。”

**用户请求**

> 我想用开源工具记录每天的待办和完成情况，看到这个项目：https://github.com/super-productivity/super-productivity 。它适合我吗？使用前需要注意什么？

### concise 的回答

适合，尤其是你希望同时管理每日待办、完成记录、时间统计和工作摘要；它支持子任务、日程、看板、专注模式，并且开源、无需账号、默认不收集数据。使用前注意功能较多可能偏重；网页版存在限制，多设备同步需选 SuperSync、Dropbox 或 WebDAV，正式使用前应确认数据存储位置并测试备份与恢复。


<details>
<summary>Codex 原生简洁高效回复模式：完整回复</summary>

总体判断：**适合试用，但更偏“任务规划＋时间追踪”，不是纯粹的每日打卡本。**

它与你的需求比较匹配的地方：

- 可按项目、标签和子任务整理待办，并用 Planner 和时间轴安排当天任务。[README](https://github.com/super-productivity/super-productivity/blob/0bb6d44d0e581c077972ef50c0f5bb2b3284b2a2/README.md)
- 支持 timeboxing、实际用时追踪、工时表和工作总结，适合回顾“今天完成了什么、花了多久”。[README](https://github.com/super-productivity/super-productivity/blob/0bb6d44d0e581c077972ef50c0f5bb2b3284b2a2/README.md)
- 有个人指标、看板、番茄钟等功能；Windows、macOS、Linux、手机和浏览器均可用。
- MIT 开源，无需注册；官方声称不收集数据，数据存放位置由用户决定。[README](https://github.com/super-productivity/super-productivity/blob/0bb6d44d0e581c077972ef50c0f5bb2b3284b2a2/README.md)

以下情况尤其适合：

- 你希望把每日待办、日程和计时放在一个工具里。
- 你会按项目或标签回顾工作。
- 你重视本地数据、开源和自主选择同步方式。
- 以后可能需要从 GitHub、Jira、Trello、日历等导入任务。

以下情况可能不太合适：

- 你只想要极简的“今天三件事，完成后打勾”。它的功能较多，维护项目、标签和时间记录可能反而增加负担。
- 你需要正式的日报、不可篡改的完成日志或长期统计报表。README 提到了工时表、工作总结和个人指标，**但没有明确说明已完成任务的长期保留方式、日报格式、查询范围或审计能力**。
- 你需要多人分派、审批或团队协作。README 主要描述个人规划和外部系统集成，没有承诺原生团队协作能力。

使用前建议注意：

1. **先验证“完成记录”是否符合你的定义。**  
   用一周模拟真实流程，检查跨天任务、已完成任务查询、每日汇总以及导出结果。不要仅凭“work summaries”就假定它能生成你想要的长期日报。

2. **提前决定数据和同步方案。**  
   官方支持 SuperSync、Dropbox 和 WebDAV；其中 README 只明确称 SuperSync 是端到端加密并可自托管，没有对另外两种方式作同样保证。[README](https://github.com/super-productivity/super-productivity/blob/0bb6d44d0e581c077972ef50c0f5bb2b3284b2a2/README.md)  
   在多设备使用前，应测试备份、恢复和同步冲突，而不只是确认“能够同步”。

3. **隐私声明不等于所有外部集成都不传数据。**  
   应用本身声称不收集数据，但启用云同步、日历、Jira、GitHub 等服务后，仍会受到相应第三方的数据政策和授权范围影响。

4. **Web 版与桌面版并不完全等价。**  
   README 明确提示 Web 版存在限制，但快照没有列出具体差异。[README](https://github.com/super-productivity/super-productivity/blob/0bb6d44d0e581c077972ef50c0f5bb2b3284b2a2/README.md) 如果你依赖附件、系统集成、通知或离线使用，应在选择版本前核对差异。

5. **先保持工作流简单。**  
   初期只使用“每日计划、完成勾选、计时/总结”，暂时关闭复杂集成和过细的标签体系。使用一两周后，再判断个人指标、看板和同步是否真正有价值。

我的建议是：**值得作为候选工具试用**。如果你的核心目标是“规划当天任务，并在晚上结合用时回顾完成情况”，它很合适；如果你真正需要的是结构化日记或可靠的历史日报档案，则应先确认其完成记录和导出能力，再决定是否长期投入。以上判断仅依据本地的官方 README 快照，没有安装或修改任何内容。

**工具旁白原文**

我会只读查看 `sources` 里的官方 README 快照，重点核对它对“每日待办、完成记录”的支持、数据存储/同步方式和使用限制，然后给你一个适用性判断。不会安装或改动文件。

README 的定位很明确：它不只是清单，而是把日程规划、计时、总结和专注工具放在一起。对你的场景总体匹配，但“完成情况”若指长期、可追溯的每日打卡台账，README 本身没有明确承诺，我会把这一点作为主要试用验证项。

</details>

<details>
<summary>每次提示“请简洁回复”：完整回复</summary>

**结论：适合，但偏“重型”。** 如果你希望把每日待办、时间安排、专注计时和完成总结放在一起，它很匹配；如果只想简单打勾记流水账，可能功能过多。

适合你的理由：

- 支持任务、子任务、项目、标签和每日计划。
- 可记录耗时，并生成工时表、工作总结。
- 支持看板、日程、番茄钟和个人指标。
- 免费开源、跨平台，无需注册；官方称不收集数据。
- 支持 WebDAV、Dropbox、端到端加密的 SuperSync。

使用前注意：

- **先确定数据存储与同步方案**，并实际测试备份和恢复。
- Web 版有功能限制，完整使用通常优先考虑桌面版。
- Jira、GitHub 等集成可自动导入任务、创建工作日志，授权时应遵循最小权限。
- “不收集数据”和端到端加密是项目方声明，不等同于独立安全审计。
- README 没详细说明完成记录的长期检索、统计粒度和导出格式；建议先验证它能否满足你的“每日复盘”习惯。

依据：[官方 README 快照](https://github.com/super-productivity/super-productivity/blob/0bb6d44d0e581c077972ef50c0f5bb2b3284b2a2/README.md)。总体建议是先轻量试用一周，只启用任务、每日计划和时间记录，暂时不要接入外部服务。

**工具旁白原文**

结论会以官方 README 快照为准；我先定位并阅读 `sources` 中对应文件，只做只读检查。

文件枚举还在运行，我继续等结果；不会访问网络或改动文件。

</details>

三组使用相同的[项目 README](https://github.com/super-productivity/super-productivity/blob/0bb6d44d0e581c077972ef50c0f5bb2b3284b2a2/README.md)、gpt-5.6-sol 模型和 high 推理强度，各独立运行一次；实际任务另要求先查阅 README 快照，只讨论、不安装或修改内容。字符去掉链接地址及空白，保留 Markdown 标记；整轮生成 token 包含推理和工具调用，不等于正文 token。此示例未计入此前的多次测试平均数据。

用途索引：`README.md` 说明唯一规则源与 Codex 全局默认注入安装；新环境安装、改规则、排查注入失效时读；避免文档和安装入口分叉。

## 文档用途索引

- `SKILL.md`：唯一规则源；改规则前读；必须与 `~/.codex/instructions.md` 一致。
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
