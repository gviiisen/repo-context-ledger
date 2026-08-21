# Native Context Bridge

Status: current
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Last reviewed: 2026-08-21

## Purpose and behavior

Repo Context Ledger 将编码 Agent 的原生仓库指令入口连接到 Git 中同一份可审查上下文。它生成薄适配器并提供最小上下文路由、checkpoint 与覆盖检查，使一个 Agent 结束或切换工作后，另一个 Agent 能从仓库记录恢复，而不依赖前者的私有 Memory。

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py` / `build_init_plan`, `init_repo` | 用同一份内存文件计划预览或安装仓库本地运行时，并维护受管 Agent 入口。 |
| `skills/repo-context-ledger/scripts/ledger.py` / `context_search`, `manifest_change_summaries` | 生成有界 `context-plan-v1`，只从 Manifest 读取近期 Change 元数据，不加载其正文。 |
| `skills/repo-context-ledger/scripts/ledger.py` / `build_parser` | 暴露 Manifest、adapter、checkpoint、有界 Context Plan 与增量/全仓检查命令。 |
| `.context-ledger/config.json` | 保存启用的适配器、文档路径、上下文预算、团队策略与质量策略。 |
| `docs/ai/context-packs/` | 保存按功能加载的最小跨 Agent 路线。 |

## Data flow and contracts

- Input: Agent 提供自然语言任务。`context --query` 只从 current Context Pack 中按 feature/title/tracked path 选择一个主 Pack；superseded、archived 或声明 `Superseded by` 的 Pack 不可成为 Required read。配置中的 `max_required_files`、`max_linked_specs` 与 `max_total_characters` 决定初始 Required reads 的硬上限。
- Flow: 运行时输出 `context-plan-v1`：一个主 Pack、预算内关联 spec、Manifest 中有上限的近期 Change ID/标题/功能/日期/摘要/evidence 路径、选择原因与预算使用量。Change 正文不进入 Required reads；`--format json` 额外提供稳定机器字段与本地耗时/计数指标。AGENTS、Claude、Cursor 与 Copilot 入口使用同一有界读取策略，禁止递归读取三类 Ledger 文档，只允许在说明未解决问题后扩大范围。省略 `--repo` 时继续向上发现仓库；`init --dry-run` 与真实 `init` 共用同一内存计划。`verify` 失败只保存脱敏 Failure Capsule，成功只保存 hash 与脱敏结果尾行。
- Persistence / dependencies: 共享知识仅持久化为普通 Git 文件；工作区当前状态继续保存在 Git metadata，派生索引由运行时确定性生成。
- Output: 新 Agent 获得有界 Required reads、冷历史摘要、当前事实入口、验证命令和下一步；检查命令报告适配器漂移、过期上下文或缺少关联记录。所有计划路径保持仓库相对。

## Boundaries and failure modes

- Invariants: `docs/specs/` 是当前事实，`docs/changes/` 是冷时间历史，current Context Pack 是加载路线；初始计划必须包含且只包含一个 current 主 Pack，不能超过配置的文件数或字符预算，近期 Change 摘要不得触发正文读取，superseded/archived Pack 正文不得进入路由；工具专用文件不得成为唯一事实源。dry-run 输出必须来自真实 init 使用的同一计划，并保持仓库与 Git 私有状态字节不变。
- Permissions / concurrency: 运行时只修改受管标记或专用适配器文件，并保留用户自定义内容；团队分支规则继续隔离活动状态和派生索引。
- Failure / recovery: Manifest 可从源文档重建；adapter 可重新同步；覆盖检查失败时必须补充或显式说明本次变更为何不需要稳定 spec。
- Non-goals: 不访问、解密、复制或声称兼容任何 Agent 的私有 Memory 格式，不保证恢复未写入仓库的完整对话，也不使用向量数据库、后台 daemon 或 LLM 生成 Context Plan。

## Verification

运行 `python -m unittest discover -s tests -v` 验证运行时、有界 Context Plan、1,000 条冷历史、100 个无关 Pack、四类 Adapter 和跨 Agent 桥接；PR 阶段运行 `python .context-ledger/ledger.py check --strict --changed-since origin/main`，全仓健康审计继续使用 `check --strict`。

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Bound context loading and delta validation](../changes/2026/08/20260821154209-gviiisen-25df54aeac-bound-context-loading-and-delta-validation.md)
- [Implement init dry-run planning](../changes/2026/08/20260815153145-gviiisen-c108737ed0-implement-init-dry-run-planning.md)
- [Harden Failure Capsule redaction before v0.5.6 release](../changes/2026/08/20260813023156-gviiisen-640b12d3d4-harden-failure-capsule-redaction-before-v0-5-6-r.md)
- [Context Router 失败摘要与仓库根发现](../changes/2026/08/20260813020044-gviiisen-418ac132d0-context-router.md)
- [Implement native context bridge](../changes/2026/08/20260811211310-gviiisen-5a44822643-implement-native-context-bridge.md)
<!-- repo-context-ledger:changes:end -->
