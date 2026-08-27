# Repo Context Ledger：跨 Agent 的 AI 编程上下文接力

[English](README.md) | [简体中文](README.zh-CN.md)

[![skills.sh](https://skills.sh/b/gviiisen/repo-context-ledger)](https://skills.sh/gviiisen/repo-context-ledger)

> 从 Codex 换到 Cursor 或 Claude，只说功能关键词，就能沿着正确代码和功能边界继续开发。

Repo Context Ledger 是一个面向 AI 编程的仓库上下文管理与上下文切换 Skill。它在 Codex、Claude、Cursor、GitHub Copilot、Grok 等编码 Agent 之间桥接经过验证的仓库上下文，并在代码新增或修复后同步维护功能说明、变更交接记录以及各级 README 摘要。

它适用于 AI 编程上下文管理、跨窗口续接、跨 Agent 上下文切换与任务交接，不需要在新会话中重新描述全部背景。

如果你正在寻找 AI 上下文管理、Codex 上下文管理、Codex 上下文、Cursor 上下文、Cursor 上下文切换、Claude 上下文管理，或者希望换一个 AI 窗口后继续开发，这个 Skill 会引导新的 Agent 快速找到相关代码、功能边界和经过验证的变更记录。

使用通用的 Agent Skills CLI 即可安装：

```bash
npx skills@latest add gviiisen/repo-context-ledger --skill repo-context-ledger
```

用户只需正常描述开发需求，文档生命周期由 AI 自主完成。

在执行任何生命周期命令前，Agent 可以先通过只读 Workflow Plan 判断这是了解功能、小修复、普通变更还是续接任务。它复用有界上下文路由、解释判断理由；意图不明确时先请求澄清，不会猜测并创建 session。

## 为什么需要它

不同的 AI 编程窗口通常无法自动继承此前积累的上下文。新的 Agent 不得不重新阅读大量代码，功能逻辑、关键边界和历史决策也容易在会话之间丢失。

Repo Context Ledger 为每个 AI 会话提供一份精简、持久的项目地图：

- 某项功能位于哪些代码位置；
- 代码调用链和处理流程如何工作；
- 哪些接口契约与边界情况必须保持稳定；
- 本次修改了什么、为什么修改、如何验证；
- 哪些项目级和模块级 README 摘要需要同步更新。

## 它会维护什么

- `docs/ai/`：供新 AI 会话快速了解整个项目的精简说明。
- `docs/ai/context-manifest.json`：供 Agent 机器读取的功能上下文路由表。
- `docs/ai/context-packs/`：按功能保存最小上下文、加载顺序、边界、测试和文件指纹。
- `docs/specs/`：当前有效的功能行为、代码地图、接口契约和边界。
- `docs/changes/`：按 `年/月/变更.md` 归档的新增与修复记录，每月都有独立的小型索引。
- 分支/worktree 私有状态：相互独立的 active/paused 草稿存放在 Git 元数据中，不会被提交；只有 completed change 才进入正式历史。
- 根目录及模块目录中的 `README.md`：只刷新受控摘要区块，不改写人工内容。
- `AGENTS.md`、`CLAUDE.md`、Cursor Rule 和 `.github/copilot-instructions.md`：把各家 Agent 指向同一 Ledger 的薄适配器。
- `.context-ledger/writing-quality.md`：供所有 AI 工具读取的证据、语言和记录形式标准。

## 兼容性

核心 Skill 遵循开放的 Agent Skills `SKILL.md` 格式，面向 Codex、Claude Code、Cursor、GitHub Copilot、Grok，以及其他支持 Agent Skills 或仓库指令文件的工具。

初始化后的项目还会包含普通指令文件，因此即使某个工具不能原生发现 Skill，也能遵循相同工作流。不同产品的原生发现方式和安装目录可能有所区别。

支持的 Python/平台与 CLI schema 保证见 [COMPATIBILITY.md](COMPATIBILITY.md)，升级规则见 [MIGRATIONS.md](MIGRATIONS.md)。

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

### GitHub Copilot

可以通过兼容 Agent Skills 的客户端安装，也可以让初始化后生成的 `.github/copilot-instructions.md` 把 Copilot 引导到 Ledger。运行时只维护标记区块，保留已有 Copilot 人工说明。

## 常见使用场景

安装并为项目完成一次初始化后，继续像平时一样用自然语言告诉 AI 要做什么即可，不需要用户自己执行 Ledger 生命周期命令。

| 场景 | 你可以直接说 | Agent 会做什么 |
| --- | --- | --- |
| 了解已有功能 | `说明一下提现审核是怎么实现的，边界在哪里。` | 路由到最相关的 Context Pack 和 spec，再按需要核验代码；只读了解不会创建任务 session。 |
| 新增或修复功能 | `修复提现通知重复发送的问题。` | 建立私有任务 session，加载有界上下文，继续展开受影响代码和测试，验证完成后发布一条 completed Change。 |
| 换一个新窗口继续 | `继续公告接口限频。` | 找到属于你的 active/paused session，生成 Resume Capsule，并继续原来的 Ledger session，不必重新描述全部背景。 |
| 从一种 AI 工具切到另一种 | 在 Codex 做到一半，打开 Cursor 后说：`继续公告接口限频。` | 使用同一套厂商无关的 Git 上下文和属于该 principal 的私有 session，同时重新核验代码与过期警告。 |
| 临时切换任务 | `先暂停这里，去修登录超时，之后我还要回来继续。` | 为当前任务保存 checkpoint，再建立独立私有 session；两个任务的 handoff 草稿不会互相覆盖。 |
| 把任务交给同事 | `把这个已暂停任务移交给 principal p-…`，或要求创建只读/fork 授权。 | 创建明确且会过期的授权。没有授权时，其他 principal 只能使用已提交的 Pack、spec 和 Change，不能读取或修改你的私有草稿。 |

路由结果只是起点，不是阅读代码的上限。只要调用者、实现、配置、持久化、权限、并发、重试、测试或外部边界可能影响目标行为，Agent 仍必须继续展开阅读和核验。

## 使用教程

### 1. 每个项目只初始化一次

用 AI 编程工具打开目标项目，然后告诉它：

> 使用 repo-context-ledger 初始化这个项目。

Agent 会先用 `init --dry-run` 预览精确操作清单，再用真实 `init` 执行同一份计划。它会创建文档结构、私有工作区状态和持久的 AI 指令，同时保留项目中已有的文档内容。

如需手动预览，可以运行：

```text
python path/to/ledger.py --repo path/to/repository init --dry-run
```

输出是简洁计划而不是完整 diff；预览不会创建锁、仓库文件或私有 session 状态文件。

### 2. 像平时一样提出开发需求

后续直接提出正常需求即可，例如：

> 修复提现监控接口，并验证修改后的行为。

你**不需要**手动执行 `ctx begin`，也不需要给交接记录命名或记忆生命周期命令。Agent 应该自主完成：

1. 为本次请求生成只读的 `workflow-plan-v1` 判断；
2. 在所选工作流需要时获取相关项目和功能上下文；
3. 仅在小修复或普通行为变更时创建私有 handoff；
4. 修改代码，并通过验证记录器执行所有声称完成的检查；
5. 从 Git 获取实际变更路径，记录 Before/After 行为、边界和证据；
6. 更新长期有效的功能说明和 Context Pack；
7. 刷新相关模块 README 和根目录 README 摘要；
8. 完成交接，并校验 Ledger 结构及 Git diff 文档覆盖。

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

初始上下文读取使用独立的生产安全预算：

```json
{
  "context": {
    "max_required_files": 3,
    "max_linked_specs": 2,
    "max_change_summaries": 3,
    "max_total_characters": 30000,
    "show_close_candidates": 0
  }
}
```

completed Change 正文不进入初始读取范围。只有经过实际测量确认需要时才应扩大预算，不应靠提高预算掩盖过大的 Pack。

Coverage 路径分类在 `.context-ledger/config.json` 中单独配置：

```json
{
  "coverage": {
    "implementation_globs": ["**"],
    "test_globs": ["tests/**", "**/*.test.*", "**/*.spec.*"],
    "ci_globs": [".github/**", ".gitlab-ci.yml"],
    "config_globs": ["pyproject.toml", "package.json"],
    "generated_globs": ["dist/**", "build/**"],
    "ignore_globs": []
  }
}
```

运行时会先应用忽略、生成文件、测试、CI 与配置规则，最后才使用生产实现兜底规则。项目可以用自己的 glob 替换默认值。发生变化的生产路径只有被某个已更新 Context Pack 精确跟踪时才算覆盖；修改无关 Pack 不会被接受。

项目维护者还可以在 `.context-ledger/config.json` 中定义审核过的验证预设。Agent 只选择预设名称，运行时直接执行保存好的参数数组，不再临时拼 PowerShell 引号，也不用从说明文字里重建长命令：

```json
{
  "verification": {
    "presets": {
      "unit": {
        "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
        "cwd": ".",
        "timeout": 300,
        "sensitive": false,
        "platforms": ["windows", "linux", "darwin"]
      },
      "windows-smoke": {
        "argv": ["powershell.exe", "-NoProfile", "-File", "scripts/smoke.ps1"],
        "platforms": ["windows"]
      }
    }
  }
}
```

需要执行时显式运行 `python .context-ledger/ledger.py verify --preset unit`。首次运行以及 preset 内容变更后的首次运行会先停止并打印精确 digest；审核 Git 中的 preset 后，再带 `--trust-digest sha256:...` 重试。信任按本机 principal 隔离，不进入 Git。预设不会在 `init`、上下文路由或 `finish` 时自动运行，也不能携带环境变量或密钥。PowerShell `-Command`、`cmd.exe`、`bash -c` 等 shell 字符串形式会被拒绝。完整约束见 [verification-presets.md](skills/repo-context-ledger/references/verification-presets.md)。

### 3. 在另一个 Agent 中继续，或者自然切换任务

如果只是换到另一个 Agent 或窗口继续同一个任务，当前 Agent 会先保存 checkpoint，包括已完成工作、Git 变更路径和下一步；任务仍保持 active，用户不用执行任何 checkpoint 命令。

像平时一样告诉 Agent：

> 先暂停提现监控修复，切到登录超时问题。

真正切换到另一项任务时，Agent 会先保存 checkpoint，再暂停当前交接，加载登录功能的 Context Pack，然后开始新任务。之后只需说：

> 继续公告抓取限频。

新窗口会用关键词路由到同一 principal 自己的一个私有任务，按需生成有界 Resume Capsule，并用新的 epoch 继续原 Ledger session。它先从 Pack、checkpoint、evidence 路径和验证结果获得方向，再按正确性需要继续阅读调用者、实现、配置、存储、权限、并发、重试、测试和外部边界。Capsule 减少的是无方向重复搜索，不是让 Agent 少读必要代码。所有生命周期命令仍由 Agent 自主执行。

其他 principal 默认看不到也不能接管私有 Capsule。同事通过 Git 中已提交的代码、Pack、spec 与 completed Change 了解并继续工作；只有显式且会过期的 read-only、fork 或 transfer 授权才会共享未完成任务。新 clone 或另一台电脑不会自动带走私有 session 状态。

### 4. 与同事协作

每位开发者使用合适的 Git 分支或 worktree。Codex、Cursor、Claude、Copilot 与 Grok 可以共用这个人的 principal，不同开发者则使用不同 principal。active/paused 任务状态保持私有；completed handoff、稳定 spec、Context Pack 与代码继续通过 Git 审查和合并。

创建或更新 PR 前，Agent 应先更新目标基础分支，然后运行：

```text
python .context-ledger/ledger.py team-check --base origin/main
python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main
```

如果其他分支修改了同一文件或同一功能，需要先与同事协调并解决重叠。PR 合并后，Agent 会在配置的默认分支上执行一次：

```text
python .context-ledger/ledger.py sync --derived
```

它会根据已经合并的源文档重建月度索引和 README 受控摘要，避免多个 PR 反复冲突在生成文件上。

这些仍然是 Agent 自主管理的生命周期命令。用户只需说“提交 PR 前检查这个分支”或“合并后同步 Ledger”，无需记住命令。若默认策略不符合团队流程，可以在 `.context-ledger/config.json` 中修改 `team.default_branch`，或把 `team.derived_updates` 设为 `always`。

### 5. 在新的 AI 窗口中继续工作

只需要告诉新 Agent 想修改哪个功能或接口。原生适配器会先把它指向共享 Context Manifest，再加载对应 Context Pack 和稳定 spec，不必重新扫描大段代码，也不需要读取上一种工具的私有 Memory。

### 6. 查看生成结果

一次修改完成后，变更记录大致如下：

```text
docs/
├── ai/
│   ├── context-manifest.json
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
- `AGENTS.md`、`CLAUDE.md` 与 GitHub Copilot 指令中受管标记之外的人工内容会被保留。
- 只有带明确标记的自动生成区块会被替换。
- 写入前会验证所有配置路径仍位于目标仓库内部。
- 交接文件采用防冲突创建方式，不会覆盖既有历史。
- Git 分支和 worktree 拥有独立的当前/暂停任务状态；旧版共享活动指针会在升级时迁移并删除。
- 功能分支默认不改共享派生文档，`team-check` 会在评审前报告潜在团队冲突。
- 当前任务不能被静默替换；切换功能前必须保存可恢复状态并暂停。
- Context Pack 使用 SHA-256 文件指纹发现被删除或发生变化的代码。
- Context Manifest 从 Context Pack、spec 和 handoff 派生，并在默认分支检查是否漂移。
- 可选 Git diff 覆盖门禁会发现没有写入 handoff 证据、稳定 spec 或 Context Pack 的行为代码。
- 不会把任何工具的私有 Memory 导入为仓库权威事实。
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

运行时贡献者只编辑 `src/repo_context_ledger/runtime.py.tmpl` 与构建片段，然后运行：

```text
python scripts/build_runtime.py
python scripts/build_runtime.py --check
```

源码与生成物边界见 [ARCHITECTURE.md](ARCHITECTURE.md)。

## v1.0.1 新增能力

- 自动规划现在只有在请求明确属于错别字、拼写、仅改注释或只改一行时才选择 `small-fix`。“一个”“single”等数量词不再代表工作简单；涉及安全、并发、事务、迁移、数据库、协议、支付或公开接口时始终按普通修改处理。
- Workflow Plan 会把显式传入的 `--tool` 继续带入建议的 `start`、`resume` 或 context 命令，使跨 Agent 续接记录保留真实工具来源。
- Git evidence 与 Coverage 会同时保留 rename 的旧路径和新路径。把生产实现移动到测试或生成目录时，旧的实现边界不会再从质量门禁中消失；copy 的来源路径仍只作为来源信息，不算作被修改的实现。
- POSIX 上新建的 Git 文档与配置默认使用 `0644`，私有 session、状态、缓存和 preset trust 使用 `0600`；已有目标权限及复制运行时的模式仍会保留。

## v1.0.0 新增能力

- 可编辑运行时现在按经过测试的边界拆分为常量、错误、结果模型、仓库锁、核心 Git 访问和 Workflow Planning。确定性构建仍只生成一个零依赖 `ledger.py`，安装和 `init` 不会增加 Python package 依赖。
- `schemas/` 正式提供 6 份 Draft 2020-12 协议声明：`workflow-plan-v1`、`context-bundle-v1`、`resume-capsule-v2`、`doctor-v1`、`status-v1` 和 `check-v1`。
- 协议测试会执行真实 CLI，并递归核对成功、无匹配与错误响应。1.x 兼容承诺固定必需字段、语义和退出类别，同时允许增加可选扩展。
- 模块化继续采用渐进方式；生命周期、路由、健康检查和渲染仍留在模板中，等形成聚焦测试边界后再拆，避免一次性重写整个运行时。

## v0.9.0 新增能力

- `plan --query` 新增只读的 `workflow-plan-v1` 入口，明确区分 `readonly`、`small-fix`、`ordinary-change` 与 `resume`；输出理由、置信度、是否需要确认，以及不会被自动执行的结构化下一步参数数组。
- 显式 intent 的结果完全确定；自动判断只使用有界的中英文请求信号和当前 principal 自己的 Resume Capsule。意图不明确时返回 `clarify`，不会擅自创建或续接 session。
- `context --format json` 以向后兼容方式附带同一份 Workflow Plan；`start` 会拒绝 `readonly` 和 `resume`，避免只读决策层意外修改任务状态。
- 新增不含生产提示词和仓库数据的中英文合成评测集与 golden 契约，固定规划行为和机器接口。
- 主 `SKILL.md` 从约 22,000 字符压缩到 12,000 字符以内，详细的生产、验证和写作规则改为按需读取 reference。

## v0.8.2 新增能力

- 仓库写锁现在记录版本、PID、开始时间、命令和随机 ownership nonce；只有文件身份与 nonce 都仍然匹配时，持有者才会删除锁，不会误删另一个写进程后来创建的替代锁。
- `doctor` 可以区分 live writer、stale process、未知 owner、旧版/损坏 metadata，以及 symlink 或非普通文件等不安全锁路径。诊断严格只读，绝不自动删锁。
- Windows 使用只读进程句柄查询存活状态，不模拟 signal；Unix 使用 signal 0。诊断只返回有上限的锁 metadata，不暴露仓库绝对路径。
- Git 跟踪的 verification preset 在首次执行和每次配置变化后都必须由当前本机 principal 按精确 digest 授信。不匹配时使用 `PRESET_TRUST_REQUIRED` fail closed；信任记录位于 Git metadata 下，不会传给另一用户。
- 新增 [SECURITY.md](SECURITY.md) 与 [THREAT_MODEL.md](THREAT_MODEL.md)，明确安全报告、资产、信任边界、已考虑威胁、恢复原则和非目标。

## v0.8.1 新增能力

- Git 路径采集改用以 NUL 分隔的原始字节输出。空格、Unicode、引号、反斜杠、制表符、换行符以及 rename 的目标路径都能无损进入 evidence 与 changed-scope 检查，不再依赖 shell 风格解析。
- 一旦目录已经确认是 Git worktree，必须读取 Git 状态的 evidence、coverage、finish 与 `check --changed-since` 会在 Git 读取失败时 fail closed；真正的非 Git 目录仍保留原有本地 fallback。
- Git 失败在 JSON 中使用稳定的 `GIT_COMMAND_FAILED` 错误码，并只输出有上限且已脱敏的诊断，不会再把损坏的 index 或不可解析的 ref 当成“没有改动”。
- 在 Unix 类系统上，运行时与受管文件的原子替换会保留现有目标文件的权限位；所有平台仍保持原有的崩溃安全替换语义。
- 新增聚焦的仓库可靠性测试，覆盖复杂 Git 文件名、Unicode rename、损坏 index 时的 fail-closed 行为与可执行权限保留，且不包含生产路径或生产资料。

## v0.8.0 新增能力

- Resume Capsule v2 继续使用向后兼容的 `context-bundle-v1` 外层，并把私有续接路线整理为目标、当前状态、下一动作、显式代码锚点、必须保持的契约、已验证事实、未决问题、Required reads 与默认不加载内容。
- Context Pack 可以维护有上限的人工 `Aliases`，记录中文、英文或团队日常真正会说的功能关键词。`pack --alias` 在刷新指纹时保留这些短语；运行时不会自动翻译，也不会猜测任务状态。
- Pack 代码地图中的 `file.go::Symbol` 成为一级路由锚点。精确别名和符号既能选择 Pack，也能选择当前 principal 自己的 active/paused session，全程不读取源码正文或其他用户的私有草稿。
- 新增完全合成的续接评测集，覆盖 owned session Top-1 命中、中英文别名、路径/符号锚点、歧义阻断、foreign overlap 隐私、Capsule 字符预算和首轮指导，不保存生产仓库名称、路径、日志或任务内容。
- 自动推断任务进度、diff 和符号明确留到后续。Capsule v2 只重组显式 checkpoint、evidence、verification、Git 位置以及 Git 中的 Pack/spec 事实；Agent 仍必须核验所有影响行为的代码边界。

## v0.7.3 新增能力

- 仓库可以保存经过审核的验证预设，用结构化 `argv`、工作目录、超时、敏感标记和平台信息代替 Agent 临时拼接命令字符串。
- `verify --preset <name>` 使用 `shell=False` 直接执行参数数组，并把预设名称和仓库相对工作目录写入验证证据。
- 配置层会拒绝危险的 shell 字符串包装：PowerShell 预设必须使用 `-File`，不能使用 `-Command`、编码命令、`cmd.exe` 或 shell `-c`。
- 预设只能显式执行；初始化、上下文路由和 finish 都不会自动运行，预设也不能内嵌环境变量或密钥。原有 `verify -- <program> <args...>` 直接参数形式继续兼容。

## v0.7.2 新增能力

- 对代码位置和行为边界已经明确的小修复，默认走最短流程：开始任务、修改代码、并行执行互不依赖的检查、完成记录。除非任务变得不确定或存在其他 session 需要明确路径，否则不再做宽泛上下文路由，也不单独执行 evidence 命令。
- 多个独立 `verify` 进程可以并发执行，只在把结果追加到各自私有记录时短暂等待。共用数据库、端口、生成目录或可变测试夹具的检查仍保持串行。
- `finish` 会在仓库写锁外准备 evidence 并完成校验，最后只用一个很短的 compare-and-swap 阶段重新确认 session、私有草稿、spec、Pack 和发布目标，再原子发布；派生索引在释放锁后生成。
- 新增可选全局参数 `--timings`，只向 stderr 输出当前命令的私有阶段耗时；不会持久化，也不包含仓库路径。
- 新增可重复运行的纯合成收尾基准。当前三轮样例中，端到端中位耗时从 3.56 秒降到 2.31 秒，`finish` 持锁中位时间约 20 毫秒；实际结果会随机器和验证命令变化。

## v0.7.1 新增能力

- 小型、受 Git 跟踪且仅影响本机/worktree 的配置改动改走紧凑流程：`start --kind local-config`、`verify --sensitive`、`finish --path ...`。
- 紧凑 finish 只接受分类为配置的路径，收集当前任务的明确 Git evidence、自动生成语义 handoff、标记 `Scope: worktree-local` 并自动应用 stable spec 例外；不再要求手改 Markdown 或单独运行 `evidence`。
- 敏感验证仍真实执行命令，但命令参数和捕获输出既不显示也不持久化；记录只保留状态、退出码、耗时和时间，且紧凑 finish 要求最后一次检查必须是通过的敏感验证。
- 生成的 Agent 规则会在这条窄路径上跳过 `context`/`focus`，要求直接传可执行程序参数而不是嵌套 PowerShell 引号；普通行为改动仍保留完整生命周期。
- `doctor` 会提示未受管的 `.active-handoff` 或旧 handoff-template 指令与私有任务 session 并存，但绝不会自动删除旧说明。

## v0.7.0 新增能力

- 新增一条确定性构建链，由 `src/repo_context_ledger/runtime.py.tmpl` 与有序构建片段统一生成两份 standalone runtime。
- 版本/schema/退出码常量、`LedgerError` 与类型化命令结果契约现在分别进入有序的 `constants.pyfrag`、`errors.pyfrag` 和 `models.pyfrag`；后续仍可渐进拆分，而不改变安装后的零依赖单文件。
- `scripts/build_runtime.py --check` 只检测漂移、不写文件；正常构建使用原子替换与 LF 规范化。测试会比较两次全新构建的字节，并编译生成的 standalone Python。
- Windows/Ubuntu CI 在完整测试前先检查生成物漂移；运行时架构测试进入新的聚焦文件，不再继续扩大旧单体测试文件。
- 初始化后的项目仍只获得一份 `.context-ledger/ledger.py`，用户无需安装 Python package；v0.6.2 已固定的 CLI/JSON 契约保持不变。

## v0.6.2 新增能力

- `status --format json` 与 `check --format json` 新增稳定的 `status-v1`、`check-v1` 自动化契约；原有文本输出与退出行为继续保留。
- `context-bundle-v1` 与 `doctor-v1` 保持不变。golden fixture 固定 schema 名、必需字段、v8 仓库配置、v0.6.1 之前已有命令集合，以及 `0`、`1`、`2` 三类退出码。
- 新增带版本且完全合成的路由评测集，核验精确 feature、title 与 tracked path 选择，不导入生产仓库资料。
- Windows 与 Ubuntu CI 同时运行最低支持的 Python 3.10 和 Python 3.12。
- 兼容与迁移文档明确 minor 版本加法规则、schema 破坏性变更的 major 版本规则、私有状态边界、standalone runtime 升级与回滚预期。

## v0.6.1 新增能力

- `doctor` 提供有上限、严格只读的仓库健康报告，支持适合人工阅读的文本与带版本的 `doctor-v1` JSON。
- 健康检查统一覆盖运行时/配置、原生 Agent 适配器、Context Manifest、私有任务状态、Context Pack 新鲜度与生命周期、本地文档链接，以及功能分支上的派生文件安全。
- stale 与缺失路径按 Pack 聚合，并通过 `--max-items` 限制详情；成熟仓库不会再为同一次修复决策输出数百条重复信息。
- 重复的 current feature ID 与断裂的显式谱系属于错误；多个 Pack 共享跟踪文件只产生警告，运行时绝不会根据文件重叠自动 supersede。
- finding 区分 `pass`、`warning`、`repairable` 与 `error`，给出确定性的建议动作，但不会修改文件、session、指纹、Pack 状态或谱系。

## v0.6.0 新增能力

- `context --query` 现在输出 `context-bundle-v1`。它仍然只选择一个主 Pack 和有预算的 Required reads，同时加入可选 PR baseline、路由 warning、cache/index 指标，以及按主 Pack 限定的 Resume Capsule；不会加载源码正文或 Change 正文。
- Git metadata 下新增可丢弃私有缓存，复用已解析的 Pack 元数据和 tracked-file digest。Pack 变化、tracked file 的 stat 或 Git text mode 变化、缓存缺失/损坏以及工具 schema 变化都会安全失效或重建；缓存不进入 Git，也不成为事实权威。
- 反向索引只缩小昂贵的指纹核验候选；运行时仍会低成本扫描全部 Pack 元数据作为正确性安全网。owned session feature、完整 title、tracked path 和 PR delta 精确重叠不会被候选缩减排除。
- `context --baseline <ref>` 解析 merge base，用 PR delta 提升相关 Pack，并只返回有上限的仓库相对相关路径。ref 无法解析时会明确 warning，不会伪装成已获得 baseline。
- Resume Capsule 会按主 Pack 对 evidence 排序。无关旧路径不再按名称进入 Capsule，只报告省略数量；Agent 仍必须核验当前 diff 和所有影响行为的代码边界。
- 公开的[性能基线](benchmarks/README.md)只记录匿名聚合值。一次 59-Pack 观测中，路由从约 10.55 秒改善到冷缓存 1.365 秒、热缓存 0.913 秒，首轮 Required reads 仍为 1 个文件。可复现 benchmark 只使用合成 Pack、代码和 checkpoint。

## v0.5.10 新增能力

- 新开的 Codex、Cursor、Claude、Copilot 或 Grok 窗口可以只用任务关键词，路由到当前 principal 自己的一个 active/paused Ledger session。`context-plan-v2` 会按需从私有状态生成有界 Resume Capsule，不保存完整聊天记录，也不会不断新增 Capsule Markdown 文件。
- `resume --query "<关键词>" --tool <agent>` 继续原有 Ledger session，不创建替代 session。每次接管都会递增 continuation epoch；后续生命周期写入必须携带 `--epoch <n>`，旧窗口不能静默覆盖新 checkpoint。
- 私有 session 增加了与 Agent 工具无关的匿名 principal 所有权。其他 principal 默认只能得到“存在范围重叠”的最少信号，不能读取 Capsule，也不能 resume、pause、checkpoint、verify、finish 或使该任务失效。
- 显式且会过期的授权支持 `read-only`、`fork` 和“先暂停再 `transfer`”。fork 会为接收者创建新的私有子 session，原任务保持不变；transfer 只在接收者接受后才转移所有权。
- Required reads 只是首轮导航，不是代码调查上限。只要调用者、实现、配置、持久化、权限、并发、重试、测试或外部边界可能影响目标行为，生成的 Agent 规则就要求继续展开阅读和核验。
- Git 中已完成的 Pack、spec、change 仍按原方式共享；未完成私有状态继续留在 worktree Git metadata，不会自动跟随另一台电脑或新 clone。

## v0.5.9 新增能力

- `context --query` 现在输出有硬预算的 `context-plan-v1`：固定一个主 Pack，只加入文件数/字符数预算内的关联 spec，并明确列出 Required reads。
- `context --format json` 提供跨 Agent 稳定契约，包括仓库相对路径、选择置信度、预算使用量以及本机耗时/文件数指标。
- 已完成 Change 保持冷历史。计划可以从 Context Manifest 返回有上限的 ID、标题、功能、日期、摘要与 evidence 路径，但不会把 Change 正文放进 Required reads。
- 四类生成 Agent 入口都禁止递归读取 `docs/ai`、`docs/specs` 和 `docs/changes`；Agent 必须先读 Required reads、保持已完成 Change 正文为冷数据，并在扩大上下文前说明尚未解决的问题。
- `check --strict --changed-since <base-ref>` 校验 merge-base delta 及其直接关联的 current Pack/spec；无关旧债务不阻塞当前 PR，但源码变化导致关联 Pack stale 时仍会失败。Coverage 只采信 evidence 与本次实现路径相交的私有 session。
- 原有全仓 `check --strict [--coverage]` 语义不变，继续用于定时健康审计和受控 Release 集成。

## v0.5.8 新增能力

- Context Pack 指纹可在 Windows 与 Unix checkout 之间稳定复用：UTF-8 文本的逻辑内容相同，无论使用 LF 还是 CRLF 都得到相同摘要。
- Git 属性仍然优先。标记为 `-text`、包含 NUL 或无法按 UTF-8 解码的文件继续逐字节校验，二进制改动不会被换行规范化掩盖。
- 已有基于 LF 的 `sha256:` 指纹继续兼容；真正的文本内容变化仍会让相关 Pack stale。
- 持久化的验证命令、成功结果末行、Failure Capsule 和 not-run 原因会把仓库、Codex、临时目录与用户目录替换为 `<REPO_ROOT>`、`<CODEX_HOME>`、`<TEMP_DIR>` 和 `<USER_HOME>`。
- 脱敏同时识别普通 Windows 路径、正斜杠路径和 JSON 双反斜杠路径；当前可见历史记录中的 5 处本机绝对路径也已纠正，但不重写 Git 历史。

## v0.5.7 新增能力

- `init --dry-run` 与真实 `init` 构建完全相同的初始化计划；它会列出将创建的文件、将更新的受管区块、将删除的生成文件、待执行迁移、识别出的模块和汇总，但不写入仓库文件或私有工作区状态。
- 预览与执行共用一份内存文件计划，避免“预览说一套，真正初始化写另一套”。
- dry-run 不获取仓库写锁；即使检查旧版工作区状态迁移，也保持只读。
- 预览和执行继续遵守相同的保护规则：保留人工文档、成熟 change 历史、自定义文档路径、嵌套 Git 边界和已有 session 草稿。

> 版本说明：v0.5.5 曾为这项工作预留，但没有正式发布；完成后的功能随 v0.5.7 发布，不存在已发布版本或功能缺失。

## v0.5.6 新增能力

- `context --query` 改为 Context Pack 路由器：只路由 current Pack，排除 superseded/archived Pack，降低指纹过期 Pack 的优先级，并返回一个主 Pack、关联 spec 和选择原因。
- 省略 `--repo` 时从当前目录向上寻找 `.context-ledger/config.json`，遇到嵌套 Git 仓库边界即停止。显式 `--repo` 仍然优先。
- `verify` 失败只记录脱敏后的 Failure Capsule；成功仍只保留 hash 和最后一行结果，不持久化原始日志。
- Handoff 的 Code paths 可以写 `file.go::Symbol`，用路径部分与 Git evidence 对齐。
- 单 session 自动 evidence 会跳过 generated/managed 路径；实现文件过多时拒绝整树吞入。
- Skill 把最短路径放在前面：只读用 `context`/`focus`，小修复走 `start → verify → finish`，完整 evidence/spec/Pack 流程留给中大改动。

## v0.5.4 新增能力

- 并行 session 的 evidence 改为显式路径集合：存在其他任务 session 时，`evidence --session <id>` 必须重复传入 `--path <path>`，拒绝把整个共享 worktree 的 dirty paths 塞进当前草稿。
- `finish` 改为 session-scoped gate，只校验所选草稿、其已记录路径、明确 spec 以及相关 Context Pack 指纹。
- 其他 session 产生的 dirty paths 与 stale Context Pack 不再阻塞当前 session；当前任务自己的 stale Pack 仍然 fail closed。
- 全仓 `check --strict --coverage` 保留为集成/PR 阶段门禁，不再作为每个 session 完成时的隐式依赖。
- 生成的 Agent 规则进一步禁止因为外部 dirty、stale Pack 或全仓检查失败而主动联系其他任务。

## v0.5.3 新增能力

- active/paused handoff 改为 worktree Git 元数据中的私有 session draft；`start`、`checkpoint`、`evidence`、`verify` 不再把未完成记录写进 `docs/changes/`。
- `finish` 预留唯一历史路径，验证草稿后原子发布一份 completed change；仓库检查通过后只删除当前 session 的私有草稿。
- 发布中断可幂等恢复：重试时识别同一 Session ID 的 completed record，不重复生成历史文件。
- v0.5.2 已登记的 active/paused 记录迁移到 v7 私有草稿；completed 与旧式历史原文保持不变。
- Ledger 的并发职责明确限定为账本隔离：不复制、不锁定、不认领、不合并、也不协调源码文件；代码冲突继续交给宿主 Agent 与 Git。

## v0.5.2 新增能力

- 以任务会话替代单一 active handoff 指针：同一 worktree 可以同时保存多个互不覆盖的 active/paused handoff。
- 所有生命周期命令支持 `--session <id>`；存在多个候选会话时，省略会话 ID 会直接拒绝，不会猜测、暂停或完成别的任务。
- `verify` 只在绑定目标和写回结果时短暂持锁，外部测试命令运行期间不再占用仓库写锁。
- 生成的 Agent 指令明确禁止未经用户授权的跨任务消息、委派、引导和中断；共享 worktree 不等于获得协调权限。
- v2-v5 的 active/paused 状态会迁移到 v6 task session，历史 change 原文不被重写。

## v0.5.1 新增能力

- Coverage 路径分类会区分生产实现、测试、CI、配置、生成文件、Ledger 受管文件以及项目自定义忽略路径。
- `.context-ledger/config.json` 中的仓库相对 glob 会经过校验并由 `init` 持久化；已有 v5 仓库不配置也能使用默认值。
- Context Pack 覆盖改为真实关联：每个发生变化的生产路径都必须由某个 Context Pack 跟踪，而且对应 Pack 必须刷新。
- 修改无关 Context Pack 不再能让 `check --coverage` 通过。
- Coverage 失败会指出未覆盖的生产路径，以及没有更新的关联 Pack。
- 根目录翻译版 README 与配置中的模块 README 会被视为受管文档，而不是生产实现。

## v0.5.0 新增能力

- Native Context Bridge：`AGENTS.md`、`CLAUDE.md`、Cursor Rule 与 GitHub Copilot Instructions 都指向同一份 Git 事实源。
- Context Manifest：`docs/ai/context-manifest.json` 确定性记录功能对应的 Context Pack、稳定 spec、关键代码路径与近期 change。
- 跨 Agent checkpoint：当前任务无需暂停即可保存已验证进度和下一步，让同一 worktree 中的另一个 Agent 继续工作。
- Adapter 生命周期：`adapters sync/check/status` 在保留用户原文的同时发现缺失或漂移的 Agent 入口。
- Git diff 覆盖门禁：`check --coverage` 会报告缺少 handoff 证据、稳定 spec/明确例外或 Context Pack 更新的行为代码。
- 私有 Memory 边界：Codex、Cursor、Claude、Copilot Memory 只作为各自缓存；只有通过代码验证的事实才能进入共享 Ledger。
- Schema v5 升级保留已有记录、自定义文档路径、成熟历史目录和 README 人工内容。

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

## 许可证

[MIT](LICENSE)
