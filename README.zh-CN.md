# Repo Context Ledger

[English](README.md) | [简体中文](README.zh-CN.md)

一个开放的 Agent Skill。AI 完成代码新增或修复后，它会同步维护项目上下文、功能说明、变更交接记录以及各级 README 摘要。

用户只需正常描述开发需求，文档生命周期由 AI 自主完成。

## 为什么需要它

不同的 AI 编程窗口通常无法自动继承此前积累的上下文。新的 Agent 不得不重新阅读大量代码，功能逻辑、关键边界和历史决策也容易在会话之间丢失。

Repo Context Ledger 为每个 AI 会话提供一份精简、持久的项目地图：

- 某项功能位于哪些代码位置；
- 代码调用链和处理流程如何工作；
- 哪些接口契约与边界情况必须保持稳定；
- 本次修改了什么、为什么修改、如何验证；
- 哪些项目级和模块级 README 摘要需要同步更新。

## v0.3.0 新增能力

- 分支/worktree 状态隔离：每个 Git 分支和工作树都有独立的当前任务与暂停栈，而且这些状态不会进入提交。
- 交接记录不会撞名：文件名和元数据同时包含时间、Git 用户与唯一标识。
- 团队冲突检查：`team-check` 会在 PR 前发现同一代码路径、同一功能、过期 Context Pack 基线和误改生成索引等问题。
- 更易合并的派生文档：功能分支不再修改共享月度索引和 README 摘要；合并后由默认分支统一确定性重建。
- 自动迁移 v2：原来的共享 `.active-handoff` 和上下文状态会安全迁移成 v3 私有工作区状态。

## 它会维护什么

- `docs/ai/`：供新 AI 会话快速了解整个项目的精简说明。
- `docs/ai/context-packs/`：按功能保存最小上下文、加载顺序、边界、测试和文件指纹。
- `docs/specs/`：当前有效的功能行为、代码地图、接口契约和边界。
- `docs/changes/`：按 `年/月/变更.md` 归档的新增与修复记录，每月都有独立的小型索引。
- 分支/worktree 私有状态：当前交接与暂停任务存放在 Git 元数据中，不会被提交。
- 根目录及模块目录中的 `README.md`：只刷新受控摘要区块，不改写人工内容。
- `AGENTS.md`、`CLAUDE.md` 和 Cursor 规则：让不同 AI 工具都能自主执行同一套流程的持久指令。

## 兼容性

核心 Skill 遵循开放的 Agent Skills `SKILL.md` 格式，面向 Codex、Claude Code、Cursor 以及其他支持 Agent Skills 的工具。

初始化后的项目还会包含普通指令文件，因此即使某个工具不能原生发现 Skill，也能遵循相同工作流。不同产品的原生发现方式和安装目录可能有所区别。

## 安装

克隆本仓库或下载 Release，然后把 `skills/repo-context-ledger` 目录安装到所使用的 AI 工具中。

### Codex

可以直接告诉 Codex：

> 使用 `$skill-installer`，从 `https://github.com/gviiisen/repo-context-ledger` 安装 `skills/repo-context-ledger` Skill。

如果只想在某个项目中使用，也可以复制或链接到：

```text
.agents/skills/repo-context-ledger/
```

### Claude Code

把 `skills/repo-context-ledger` 复制或链接到个人级或项目级 Skill 目录：

```text
~/.claude/skills/repo-context-ledger/
.claude/skills/repo-context-ledger/
```

### Cursor

在 Cursor 的 Skills/Rules 设置中导入本 GitHub 仓库，或把 Skill 复制到：

```text
~/.agents/skills/repo-context-ledger/
.agents/skills/repo-context-ledger/
```

## 使用教程

### 1. 每个项目只初始化一次

用 AI 编程工具打开目标项目，然后告诉它：

> 使用 repo-context-ledger 初始化这个项目。

Agent 会创建文档结构、私有工作区状态和持久的 AI 指令，同时保留项目中已有的文档内容。

### 2. 像平时一样提出开发需求

后续直接提出正常需求即可，例如：

> 修复提现监控接口，并验证修改后的行为。

你**不需要**手动执行 `ctx begin`，也不需要给交接记录命名或记忆生命周期命令。Agent 应该自主完成：

1. 获取与本次需求有关的项目和功能上下文；
2. 在开始修改前创建变更交接；
3. 修改代码并运行测试；
4. 记录涉及的代码链路、决策、边界和验证结果；
5. 更新长期有效的功能说明和 Context Pack；
6. 刷新相关模块 README 和根目录 README 摘要；
7. 完成交接并校验整个 Ledger。

如果当前处于功能分支，共享月度索引和 README 摘要区块会暂时保持不变，等合并后再统一生成。

### 3. 使用自然语言切换任务

像平时一样告诉 Agent：

> 先暂停提现监控修复，切到登录超时问题。

Agent 会记录当前进度和下一步，暂停当前交接，加载登录功能的 Context Pack，然后开始新任务。之后只需说：

> 继续刚才的提现监控任务。

Agent 会恢复交接，检查仓库提交和被跟踪文件是否已经变化，并且只重新加载相关上下文。`pause`、`focus`、`pack`、`resume` 都是 Agent 内部维护命令，用户不需要执行。

### 4. 与同事协作

每位开发者或 AI 使用自己的 Git 分支或 worktree。当前任务和暂停栈会自动隔离；handoff、稳定功能说明与 Context Pack 则照常进入 Git，供团队审查和合并。

创建或更新 PR 前，Agent 应先更新目标基础分支，然后运行：

```text
python .context-ledger/ledger.py team-check --base origin/main
```

如果其他分支修改了同一文件或同一功能，需要先与同事协调并解决重叠。PR 合并后，Agent 会在配置的默认分支上执行一次：

```text
python .context-ledger/ledger.py sync --derived
```

它会根据已经合并的源文档重建月度索引和 README 受控摘要，避免多个 PR 反复冲突在生成文件上。

这些仍然是 Agent 自主管理的生命周期命令。用户只需说“提交 PR 前检查这个分支”或“合并后同步 Ledger”，无需记住命令。若默认策略不符合团队流程，可以在 `.context-ledger/config.json` 中修改 `team.default_branch`，或把 `team.derived_updates` 设为 `always`。

### 5. 在新的 AI 窗口中继续工作

只需要告诉新 Agent 想修改哪个功能或接口。它可以先读取精简索引和对应功能说明，不必为了背景上下文重新扫描一大片代码。

### 6. 查看生成结果

一次修改完成后，变更记录大致如下：

```text
docs/
├── ai/
│   └── context-packs/
│       └── withdrawal-monitoring.md
├── specs/
└── changes/
    └── 2026/
        └── 08/
            ├── README.md
            └── 20260811123045-alice-a1b2c3d4e5-fix-withdrawal-monitoring.md
```

实际月份根据完成日期自动生成。按月归档可以避免项目长期使用后单个文档变得过大。

## 安全性与职责边界

- 初始化可重复执行，不会反复破坏结构。
- 已有文档和 README 人工内容会被保留。
- 只有带明确标记的自动生成区块会被替换。
- 写入前会验证所有配置路径仍位于目标仓库内部。
- 交接文件采用防冲突创建方式，不会覆盖既有历史。
- Git 分支和 worktree 拥有独立的当前/暂停任务状态；旧版共享活动指针会在升级时迁移并删除。
- 功能分支默认不改共享派生文档，`team-check` 会在评审前报告潜在团队冲突。
- 当前任务不能被静默替换；切换功能前必须保存可恢复状态并暂停。
- Context Pack 使用 SHA-256 文件指纹发现被删除或发生变化的代码。
- 受管理文件使用原子替换；修改命令使用短时仓库锁，避免并发写入。
- 运行时只依赖 Python 3.10+ 标准库，不需要 API Key。
- 功能语义仍由 Agent 负责总结；脚本负责保证目录结构、生命周期状态和链接的一致性。

## 参与开发

运行测试：

```text
python -m unittest discover -s tests -v
```

使用 OpenAI Skill Creator 校验器检查 Skill：

```text
python <skill-creator>/scripts/quick_validate.py skills/repo-context-ledger
```

## 许可证

[MIT](LICENSE)
