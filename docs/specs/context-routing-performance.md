# Context Routing Performance

Status: current
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Last reviewed: 2026-08-21

## Purpose and behavior

Context Routing Performance 负责在大型仓库中快速生成有界 Context Bundle。它通过 Git metadata 下的可丢弃私有缓存复用 Context Pack 解析结果与 tracked-file 指纹，通过反向索引缩小候选 Pack，并可用显式 PR baseline 将当前 merge-base delta 纳入路由。缓存和索引只负责导航，Git 中的 Pack、spec、completed Change、代码与实际验证仍是事实来源。

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::load_live_context_packs` | 从私有缓存或当前 Pack 文件加载可路由元数据，并核验 tracked-file 指纹。 |
| `skills/repo-context-ledger/scripts/ledger.py::build_context_reverse_index` | 将 feature、title、purpose 与 tracked path 规范化为 Pack 候选反向索引。 |
| `skills/repo-context-ledger/scripts/ledger.py::context_baseline` | 解析显式 baseline ref、merge base 与当前 delta，不读取源码正文。 |
| `skills/repo-context-ledger/scripts/ledger.py::context_search` | 输出一个有预算、仓库相对且可跨 Agent 使用的 `context-bundle-v1`。 |
| `skills/repo-context-ledger/scripts/ledger.py::build_resume_capsule` | 按主 Pack 范围过滤旧 evidence 噪声，并报告省略数量。 |
| `benchmarks/context_router_benchmark.py` | 用完全合成的 59-Pack 临时仓库测量 cold/warm 路由，不导入真实项目资料。 |

## Data flow and contracts

- Input: 自然语言 query、可选 Agent tool、可选 baseline ref、current Context Pack、当前 principal 可访问的 active/paused session，以及 Context Manifest 中有限的 completed Change 元数据。
- Flow: 运行时先读取或重建 Git metadata 中的私有缓存；Pack 文件变化会重新解析，tracked file 的 stat 或 Git text mode 变化会重新计算 digest。反向索引给出候选 Pack；owned session feature、精确 tracked path 和 baseline overlap 可以提高候选优先级。最终只选择一个主 Pack，并在配置预算内加入关联 spec、Change 摘要与 Resume Capsule。
- Persistence / dependencies: 缓存只能位于 `git rev-parse --git-path repo-context-ledger/cache/...` 返回的位置；不得写入工作树、Manifest 或 completed Change。缓存内容不得包含源码正文、Change 正文、验证日志或聊天记录。缓存缺失、损坏、旧 schema、不可写或并发覆盖时必须回退到当前文件并保持正确结果。
- Output: `context-bundle-v1` 包含选择依据、Required reads、可选 Resume Capsule、baseline 状态、扩展规则、预算与本地性能/cache 指标。所有公开路径都必须是仓库相对路径；Required reads 只是首轮路线，不限制后续代码调查。

## Boundaries and failure modes

- Invariants: cache disabled/cold/warm 必须选择同一主 Pack并给出同一 Required reads；tracked file、Pack 状态、Pack 内容或 Git text mode 改变时不能复用过期结果；无安全索引命中时必须确定性回退，不得猜测。baseline ref 无法解析时 Bundle 要明确标为 unresolved，不能假装已获得 PR 范围。
- Permissions / concurrency: cache 只保存当前 Git checkout 已可读取的 Git 跟踪导航元数据，不扩大 session principal 权限。并发路由只通过原子替换写 cache；最后一个完整写入可以覆盖较早 cache，但下一次请求仍以当前 Pack/file stat 与 Git text mode 重新判定失效。cache 命中不允许读取 foreign private draft。
- Failure / recovery: cache 文件缺失、损坏、旧 schema、不可写或在并发中被替换时，当前请求回退到 live Pack 与 tracked file 校验，并把 cache 状态或 baseline 失败写入 Bundle warning。恢复方式是下一次请求自动重建；不能要求用户手工修订 cache，也不能因 cache 失败降低指纹门禁。
- Privacy: 公共测试和 benchmark 只允许合成 feature、路径、源码与 session。真实性能验证只能对外保留匿名聚合数字，不能写入仓库名、remote、branch、commit、query、任务标题、session ID、代码路径、日志或 Capsule 正文。
- Evidence filtering: 有主 Pack 时只优先保留 exact tracked path 或同一紧邻代码目录的 evidence；无关旧路径不进入 Capsule，只报告省略数量。过滤不能声明代码边界已经完整，Agent 仍须按扩展规则核验实际调用链和 diff。
- Non-goals: 本功能不缓存模型 Memory，不保存聊天记录，不读取其他用户的私有 session，不自动提交未完成任务，不用缓存替代 Git 校验，也不限制 Agent 为解决行为不确定性继续读代码。

## Verification

单元测试覆盖 cache cold/warm 等价性、Pack 与 tracked-file 失效、损坏缓存恢复、反向索引回退、baseline resolved/unresolved、evidence 噪声过滤、仓库相对输出与 59-Pack 合成规模。`benchmarks/context_router_benchmark.py` 单独输出 cold/warm 聚合结果；Windows 与 Ubuntu CI 运行完整测试套件。

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Accelerate context routing with private cache and PR bundles](../changes/2026/08/20260821191911-gviiisen-901f527dbd-accelerate-context-routing-with-private-cache-an.md)
<!-- repo-context-ledger:changes:end -->
