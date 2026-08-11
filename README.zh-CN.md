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

## v0.4.1 新增能力

- 成熟仓库兼容：已有的 `YYYY-MM/...` 变更树会统一归到月份根目录，不再在每个日期或功能目录生成索引。
- 复用并保留已有的 `YYYY-MM/index.md` 月索引；运行时不会改写其中的人工维护内容。
- 同一月份同时存在旧式与新式目录时，共用一个月份入口，并优先复用已有的人工月索引。
- 安全清理旧索引：只有运行时能根据当前同级记录逐字重建的 `README.md` 才会被删除；来源不确定或经过人工编辑的文件继续保留。
- worktree 边界识别：模块扫描在嵌套 Git 仓库和 worktree 处停止，避免重复模块与错误 README 更新。
- 修正历史计数：月份 `index.md` 作为索引处理，不再被计为普通 change。

## v0.4.0 新增能力

- 证据优先记录：新 handoff、spec 和 Context Pack 使用向后兼容的 `evidence-v1` 质量档案。
- 真实验证记录：`verify` 亲自执行检查，记录命令、状态、退出码、耗时和输出哈希，但不把完整输出写入仓库。
- Git 变更证据：`evidence` 读取实际变更路径，避免 AI 凭记忆记录。
- 语言策略：支持 `auto`、`en` 和 `zh-CN`，源码标识与命令保持原文。
- 可配置详细程度：支持 `concise`、`standard` 和 `detailed`，Context Pack 具有大小上限。
- 按用途使用不同形式：handoff 记录 Before/After 证据，spec 记录当前事实，Context Pack 保持最小加载路线。
- 旧记录安全兼容：除非明确升级，已有记录的语言、形式、文件名和内容都不会变化。

## 它会维护什么

- `docs/ai/`：供新 AI 会话快速了解整个项目的精简说明。
- `docs/ai/context-packs/`：按功能保存最小上下文、加载顺序、边界、测试和文件指纹。
- `docs/specs/`：当前有效的功能行为、代码地图、接口契约和边界。
- `docs/changes/`：按 `年/月/变更.md` 归档的新增与修复记录，每月都有独立的小型索引。
- 分支/worktree 私有状态：当前交接与暂停任务存放在 Git 元数据中，不会被提交。
- 根目录及模块目录中的 `README.md`：只刷新受控摘要区块，不改写人工内容。
- `AGENTS.md`、`CLAUDE.md` 和 Cursor 规则：让不同 AI 工具都能自主执行同一套流程的持久指令。
- `.context-ledger/writing-quality.md`：供所有 AI 工具读取的证据、语言和记录形式标准。

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
3. 修改代码，并通过验证记录器执行所有声称完成的检查；
4. 从 Git 获取实际变更路径，记录 Before/After 行为、边界和证据；
5. 更新长期有效的功能说明和 Context Pack；
6. 刷新相关模块 README 和根目录 README 摘要；
7. 完成交接并校验整个 Ledger。

如果当前处于功能分支，共享月度索引和 README 摘要区块会暂时保持不变，等合并后再统一生成。

### 记录语言与形式

默认质量策略为：

```json
{
  "language": "auto",
  "detail": "standard",
  "max_context_pack_lines": 180
}
```

使用 `auto` 时，Agent 优先遵循项目附近文档的主要语言；如果没有既定习惯，则使用用户的语言。文件路径、函数名、接口字段、命令和错误文本保持源码原文。handoff、稳定 spec 和 Context Pack 会采用不同的 Markdown 结构，因为它们解决的问题不同；升级时不会重新格式化旧文档。

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
- `evidence-v1` 记录会拒绝未确定语言、残留占位符、空泛陈述、缺少具体路径、不完整的 Before/After 以及未经真实执行的验证结果。
- 验证完整输出只展示给当前 Agent，仓库仅保存哈希和元数据；常见的密码/token 命令参数会自动遮蔽。
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
