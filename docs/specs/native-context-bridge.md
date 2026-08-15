# Native Context Bridge

Status: current
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Last reviewed: 2026-08-15

## Purpose and behavior

Repo Context Ledger 将编码 Agent 的原生仓库指令入口连接到 Git 中同一份可审查上下文。它生成薄适配器并提供最小上下文路由、checkpoint 与覆盖检查，使一个 Agent 结束或切换工作后，另一个 Agent 能从仓库记录恢复，而不依赖前者的私有 Memory。

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py` / `build_init_plan`, `init_repo` | 用同一份内存文件计划预览或安装仓库本地运行时，并维护受管 Agent 入口。 |
| `skills/repo-context-ledger/scripts/ledger.py` / `build_parser` | 暴露 Manifest、adapter、checkpoint 与覆盖检查命令。 |
| `.context-ledger/config.json` | 保存启用的适配器、文档路径、团队策略与质量策略。 |
| `docs/ai/context-packs/` | 保存按功能加载的最小跨 Agent 路线。 |

## Data flow and contracts

- Input: Agent 根据自然语言任务确定 feature。`context --query` 读取 live Context Pack 元数据，按 feature/title/tracked path 选择一个主 Pack 及其关联 spec，并说明选择原因。
- Flow: 原生 Agent 入口指向仓库规则；省略 `--repo` 时从当前目录向上寻找 `.context-ledger/config.json` 并在嵌套 Git 边界停下。`init --dry-run` 与真实 `init` 共用同一个内存文件计划，前者只输出 create/update/delete/migration/module 摘要且不获取写锁或写入状态。完成或切换时将已验证状态保存为 checkpoint/handoff。`verify` 失败只持久化脱敏后的 Failure Capsule；脱敏同时覆盖命令显示与输出摘要中常见的 `key=value`、`key: value`、JSON 和空格分隔凭据形式。成功只保留 hash 与经同样脱敏的最后一行结果。
- Persistence / dependencies: 共享知识仅持久化为普通 Git 文件；工作区当前状态继续保存在 Git metadata，派生索引由运行时确定性生成。
- Output: 新 Agent 获得最小加载路径、当前事实、验证命令和下一步；检查命令报告适配器漂移、过期上下文或缺少关联记录。

## Boundaries and failure modes

- Invariants: `docs/specs/` 是当前事实，`docs/changes/` 是时间历史，Context Pack 是加载路线；工具专用文件不得成为唯一事实源。dry-run 输出必须来自真实 init 使用的同一计划，并保持仓库与 Git 私有状态字节不变。
- Permissions / concurrency: 运行时只修改受管标记或专用适配器文件，并保留用户自定义内容；团队分支规则继续隔离活动状态和派生索引。
- Failure / recovery: Manifest 可从源文档重建；adapter 可重新同步；覆盖检查失败时必须补充或显式说明本次变更为何不需要稳定 spec。
- Non-goals: 不访问、解密、复制或声称兼容任何 Agent 的私有 Memory 格式，也不保证恢复未写入仓库的完整对话。

## Verification

运行 `python -m unittest discover -s tests -v` 验证运行时和跨 Agent 桥接；运行 `python .context-ledger/ledger.py check --strict` 验证本仓库的稳定文档、链接和证据。

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Implement init dry-run planning](../changes/2026/08/20260815153145-gviiisen-c108737ed0-implement-init-dry-run-planning.md)
- [Harden Failure Capsule redaction before v0.5.6 release](../changes/2026/08/20260813023156-gviiisen-640b12d3d4-harden-failure-capsule-redaction-before-v0-5-6-r.md)
- [Context Router 失败摘要与仓库根发现](../changes/2026/08/20260813020044-gviiisen-418ac132d0-context-router.md)
- [Implement native context bridge](../changes/2026/08/20260811211310-gviiisen-5a44822643-implement-native-context-bridge.md)
<!-- repo-context-ledger:changes:end -->
