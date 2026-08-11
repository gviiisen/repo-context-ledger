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

## v0.2.0 新增能力

- 自然语言上下文切换：暂停一个任务、切到另一项功能，以后再恢复，不丢失进度。
- Context Pack：在 `docs/ai/context-packs/` 中保存按功能划分的精简加载指南。
- 暂停任务栈：可以保留多个未完成交接，恢复最近任务或指定任务。
- 过期检测：通过被跟踪文件的指纹判断 Context Pack 是否已经落后于代码。
- 安全恢复：保留基础提交、未提交文件、已完成工作和下一项具体操作。

## 它会维护什么

- `docs/ai/`：供新 AI 会话快速了解整个项目的精简说明。
- `docs/ai/context-packs/`：按功能保存最小上下文、加载顺序、边界、测试和文件指纹。
- `docs/specs/`：当前有效的功能行为、代码地图、接口契约和边界。
- `docs/changes/`：按 `年/月/变更.md` 归档的新增与修复记录，每月都有独立的小型索引。
- `docs/changes/.active-handoff`：正在处理的变更交接指针。
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

Agent 会创建文档结构、上下文状态和持久的 AI 指令，同时保留项目中已有的文档内容。

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

### 3. 使用自然语言切换任务

像平时一样告诉 Agent：

> 先暂停提现监控修复，切到登录超时问题。

Agent 会记录当前进度和下一步，暂停当前交接，加载登录功能的 Context Pack，然后开始新任务。之后只需说：

> 继续刚才的提现监控任务。

Agent 会恢复交接，检查仓库提交和被跟踪文件是否已经变化，并且只重新加载相关上下文。`pause`、`focus`、`pack`、`resume` 都是 Agent 内部维护命令，用户不需要执行。

### 4. 在新的 AI 窗口中继续工作

只需要告诉新 Agent 想修改哪个功能或接口。它可以先读取精简索引和对应功能说明，不必为了背景上下文重新扫描一大片代码。

### 5. 查看生成结果

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
            └── fix-withdrawal-monitoring.md
```

实际月份根据完成日期自动生成。按月归档可以避免项目长期使用后单个文档变得过大。

## 安全性与职责边界

- 初始化可重复执行，不会反复破坏结构。
- 已有文档和 README 人工内容会被保留。
- 只有带明确标记的自动生成区块会被替换。
- 写入前会验证所有配置路径仍位于目标仓库内部。
- 交接文件采用防冲突创建方式，不会覆盖既有历史。
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
