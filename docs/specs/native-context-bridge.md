# Native Context Bridge

Status: current
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Last reviewed: 2026-08-21

## Purpose and behavior

Repo Context Ledger 将编码 Agent 的原生仓库指令入口连接到同一份可审查上下文。它生成薄适配器并提供有界上下文路由、按需 Resume Capsule、checkpoint 与覆盖检查，使同一用户从一个 Agent 窗口切到另一个窗口时可以继续原 Ledger session，而不依赖前者的私有 Memory；其他用户默认只能读取已经进入 Git 的事实。

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py` / `build_init_plan`, `init_repo` | 用同一份内存文件计划预览或安装仓库本地运行时，并维护受管 Agent 入口。 |
| `skills/repo-context-ledger/scripts/ledger.py` / `context_search`, `route_resume_sessions`, `manifest_change_summaries` | 生成有界 `context-plan-v2`，路由一个可访问私有 session，并只从 Manifest 读取近期 Change 元数据。 |
| `skills/repo-context-ledger/scripts/ledger.py` / `resume_change`, `share_session` | 续接同一 session、轮换 epoch/tool，并执行显式 read-only/fork/transfer 授权。 |
| `skills/repo-context-ledger/scripts/ledger.py` / `build_parser` | 暴露 Manifest、adapter、checkpoint、resume/share、有界 Context Plan 与增量/全仓检查命令。 |
| `.context-ledger/config.json` | 保存启用的适配器、文档路径、上下文预算、团队策略与质量策略。 |
| `docs/ai/context-packs/` | 保存按功能加载的最小跨 Agent 路线。 |

## Data flow and contracts

- Input: Agent 提供自然语言任务关键词和工具 ID。`context --query` 从 current Context Pack 中按 feature/title/tracked path 选择一个主 Pack，并只在当前 principal 可访问的 active/paused session 中寻找唯一候选；配置预算只限制首轮 Required reads。
- Flow: 运行时输出 `context-plan-v2`：主 Pack、预算内 spec、冷 Change 元数据、选择原因、预算、以及可选 Resume Capsule。Capsule 只含 checkpoint 摘要、下一步、有限实现路径、最近验证、Git 位置、Pack、warning、tool 与 epoch，不含完整对话。`resume` 续接同一 session 并要求后续写入携带新 epoch。四类 Agent 入口先读 Required reads，但在调用者、实现、配置、存储、权限、并发、重试、测试或外部 API 影响行为时必须继续展开，不得把预算误作代码阅读上限。
- Persistence / dependencies: 共享知识仅持久化为普通 Git 文件；owner principal、grant、epoch 和 Capsule 来源保存在 worktree Git metadata。Capsule 按需生成，不新增共享 Markdown。派生索引由运行时确定性生成。
- Output: 同 principal 的新 Agent 获得有界导航与同一 session 的续接令牌；其他 principal 默认只得到 foreign-overlap 布尔信号以及正常 Git 路线。检查命令继续报告 adapter 漂移、过期上下文或缺少关联记录。所有计划路径保持仓库相对。

## Boundaries and failure modes

- Invariants: `docs/specs/` 是当前事实，`docs/changes/` 是冷时间历史，current Context Pack 是加载路线；首轮计划只包含一个 current 主 Pack 并遵守预算，但该预算不限制必要代码阅读；Change 摘要不触发正文读取；foreign session 不泄露摘要、路径、验证、epoch 或草稿位置；工具专用文件不得成为唯一事实源。
- Permissions / concurrency: 同一 principal 可以跨 Agent 工具续接；不同 principal 默认不能读取或修改私有 session。显式授权会过期，read-only 不可 resume，fork 不改原任务，transfer 要求先暂停。该策略是应用层逻辑隔离，实际安全仍依赖文件系统与 OS 权限。运行时保留适配器的用户自定义内容。
- Failure / recovery: 多个近似 session 必须显式选择；旧 epoch、过期授权和未授权访问 fail closed；另一 clone 或电脑只从已提交 Pack/spec/Change 恢复。Manifest 可重建，adapter 可重新同步，覆盖检查语义保持不变。
- Non-goals: 不访问、解密、复制或声称兼容任何 Agent 的私有 Memory，不保存完整聊天，不以 Capsule 代替必要代码核验，不同步未完成私有状态，不使用向量数据库、后台 daemon 或 LLM 生成 Context Plan。

## Verification

运行 `python -m unittest discover -s tests -p test_ledger.py` 验证有界 Context Plan v2、同 principal 跨 Agent resume、foreign 隔离、显式授权、1,000 条冷历史、100 个无关 Pack和四类 Adapter；PR 阶段运行 `python .context-ledger/ledger.py check --strict --changed-since origin/main`，全仓健康审计继续使用 `check --strict`。

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Add cross-Agent session resume ownership](../changes/2026/08/20260821171622-gviiisen-67c0a5a3f9-add-cross-agent-session-resume-ownership.md)
- [Bound context loading and delta validation](../changes/2026/08/20260821154209-gviiisen-25df54aeac-bound-context-loading-and-delta-validation.md)
- [Implement init dry-run planning](../changes/2026/08/20260815153145-gviiisen-c108737ed0-implement-init-dry-run-planning.md)
- [Harden Failure Capsule redaction before v0.5.6 release](../changes/2026/08/20260813023156-gviiisen-640b12d3d4-harden-failure-capsule-redaction-before-v0-5-6-r.md)
- [Context Router 失败摘要与仓库根发现](../changes/2026/08/20260813020044-gviiisen-418ac132d0-context-router.md)
- [Implement native context bridge](../changes/2026/08/20260811211310-gviiisen-5a44822643-implement-native-context-bridge.md)
<!-- repo-context-ledger:changes:end -->
