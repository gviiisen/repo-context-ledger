# Accelerate context routing with private cache and PR bundles

Status: completed
Feature: context-routing-performance
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Handoff ID: 20260821191911-gviiisen-901f527dbd
Session ID: 20260821191911-gviiisen-901f527dbd
Actor: gviiisen
Branch: feat/v0.6.0-context-performance
Started: 2026-08-21T19:19:11+08:00
Completed: 2026-08-21T19:57:44+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 7655bcccc6bb3b07aab23fdd86f16c048178535b
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/context-routing-performance.md
Spec exception: none

## Intent

为大型生产仓库减少 `context --query` 的重复 Pack 解析、tracked-file 指纹计算和无方向文档读取，同时保持路由边界可验证。验收结果是：输出稳定的有界 Context Bundle、支持显式 PR baseline、私有缓存失效时不改变正确选择、旧 evidence 噪声不再按路径进入 Capsule，并且真实性能记录只保留匿名聚合值。

## Changed behavior

Before: `load_live_context_packs` 在每次路由中读取全部 current Pack 正文，并为所有 tracked file 逐项计算指纹；旧实现没有 PR baseline，也会把一个 session 中最多 16 个实现 evidence 路径直接放进 Capsule。匿名 59-Pack 观测的路由约为 10.55 秒，首轮 Required reads 为 1 个文件，历史 Capsule 为 2,706 字符且包含无关旧 evidence 噪声。

After: `context-bundle-v1` 使用 Git metadata 下的可丢弃 cache 复用 Pack 元数据与 digest，批量解析 Git text mode，并通过反向索引加最多 5 个全量元数据安全候选，只对候选执行昂贵指纹核验。`--baseline <ref>` 加入 merge-base delta；Capsule 按主 Pack 路径亲和度保留 evidence 并只报告省略数量。相同匿名 59-Pack 环境中，候选运行时冷路由为 1,364.505 ms、热路由为 912.673 ms，首轮仍只读取 1 个文件；公开 benchmark 只生成合成仓库。

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::ContextRouterCache` | 管理路由所需的私有 Pack/digest cache。 | 新增 Git metadata 定位、schema/tool 失效、Pack stat 校验、批量 text mode、digest 复用、损坏重建和原子写入。 |
| `skills/repo-context-ledger/scripts/ledger.py::build_context_reverse_index`, `candidate_context_packs` | 从自然语言和仓库路径选择需要指纹核验的 Pack。 | 新增选择性 token 候选、exact feature/title/path、owned session、PR delta 加权，并保留最多 5 个全 Pack 元数据排序安全候选。 |
| `skills/repo-context-ledger/scripts/ledger.py::context_baseline`, `context_search` | 构造跨 Agent 路由输出。 | 新增 merge-base baseline、`context-bundle-v1`、cache/index 指标、仓库相对路径 warning 与候选指纹惰性核验。 |
| `skills/repo-context-ledger/scripts/ledger.py::build_resume_capsule` | 从私有 checkpoint 生成有界 Resume Capsule。 | 按主 Pack exact/紧邻目录过滤旧 evidence，记录 `omitted_evidence_paths`，不输出被省略路径名称。 |
| `benchmarks/context_router_benchmark.py` | 提供可复现性能夹具。 | 创建 59 个合成 Pack、唯一假源码与假 checkpoint，测量 cold/warm route 并拒绝绝对临时根泄露。 |
| `tests/test_ledger.py` | 验证运行时行为与迁移边界。 | 增加 cache 命中/损坏/失效、baseline resolved/unresolved、evidence 过滤、59 个唯一路径 Pack 候选上限和 Bundle schema 场景。 |
| `.context-ledger/ledger.py` | 仓库本地运行时副本。 | 与 Skill canonical runtime 机械同步到 v0.6.0。 |

## Boundaries and risks

- Invariant: cache、反向索引和 baseline 只提供导航；Git 中的 Pack/spec/Change、当前代码和实际验证继续优先。Required reads 只限制首轮文档加载，不限制 Agent 阅读所有影响行为的调用者、实现、配置、持久化、权限、并发、重试、测试与外部 API。
- Failure / recovery: cache 缺失、损坏、旧 schema 或不可写时回退实时解析；Pack、tracked file stat 或 Git text mode 变化会重新计算；baseline ref 无法解析时 Bundle 明确返回 `unresolved` warning；这些情况都不能伪装成 ready。
- Not changed: principal 所有权、foreign session 隔离、Git 中 completed 文档共享、私有未完成状态不随 clone 传播、session/finish/Coverage 门禁和 feature 分支不更新共享派生索引的规则保持不变。

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python benchmarks/context_router_benchmark.py`
  - Status: passed
  - Exit code: 0
  - Duration: 6.05s
  - Recorded: 2026-08-21T19:51:11+08:00
  - Output evidence: sha256:ef79f0a78ae4b20356572617b40e8fd842be6f4d0b10cb7524369cba3912b7b0 (386 characters captured; content not persisted; last=})
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-21T19:51:17+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python -m unittest discover -s tests -p test_ledger.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 196.47s
  - Recorded: 2026-08-21T19:54:41+08:00
  - Output evidence: sha256:7ab2a78985883e39a1fa1e7d48d953e5a55be5a935c5b968e9f645bc50d58a6d (11967 characters captured; content not persisted; last=OK)
- Command: `python .context-ledger/ledger.py adapters check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.14s
  - Recorded: 2026-08-21T19:54:55+08:00
  - Output evidence: sha256:9eab9a5a937791f0f7f83f779889ec7ce552e860d827df0cf9411b8db2d296ac (163 characters captured; content not persisted; last=copilot: current (.github/copilot-instructions.md))
- Command: `git diff --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.05s
  - Recorded: 2026-08-21T19:54:56+08:00
  - Output evidence: sha256:b80f14a5ff6409b024892d67cadbe42209e3c77cc2fde4413bdc4e214a73f2c2 (2137 characters captured; content not persisted; last=warning: in the working copy of 'tests/test_ledger.py', LF will be replaced by CRLF the next time Git touches it)
- Command: `python -m py_compile skills/repo-context-ledger/scripts/ledger.py .context-ledger/ledger.py benchmarks/context_router_benchmark.py`
  - Status: passed
  - Exit code: 0
  - Duration: 0.26s
  - Recorded: 2026-08-21T19:54:57+08:00
  - Output evidence: No output.
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since main`
  - Status: failed
  - Exit code: 2
  - Duration: 2.05s
  - Recorded: 2026-08-21T19:57:00+08:00
  - Output evidence: sha256:aa6d2203fef67cddea55f30a209fa2afe701fc7ca37cdb06d0be2ec25d116cf8 (477 characters captured; content not persisted; failure=ERROR: docs/specs/context-routing-performance.md: Stable spec boundaries require a substantive Permissions / concurrency: value. | ERROR: docs/specs/context-routing-performance.md: Stable spec boundaries require a substantive Failure / recovery: value. | ERROR: Behavior-changing path has no related Context Pack tracked file: benchmarks/README.md)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since main`
  - Status: passed
  - Exit code: 0
  - Duration: 1.84s
  - Recorded: 2026-08-21T19:57:29+08:00
  - Output evidence: sha256:02990ddbdc3400414df03b86ef24ce3528bf599789dea0e43a6697266433adb1 (180 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
- Command: `python .context-ledger/ledger.py team-check --base main`
  - Status: passed
  - Exit code: 0
  - Duration: 1.38s
  - Recorded: 2026-08-21T19:57:38+08:00
  - Output evidence: sha256:c2cc732b7c3da5171f0eedad393df27e564c10c8c4b85a78b8e2a6ef2e3a7cbc (186 characters captured; content not persisted; last=Team collaboration check passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `benchmarks/README.md`, `docs/specs/context-routing-performance.md`, `docs/specs/native-context-bridge.md`, `docs/specs/task-session-integrity.md`, `docs/ai/context-packs/context-routing-performance.md`, `docs/ai/context-packs/native-context-bridge.md`, `docs/ai/context-packs/task-session-integrity.md`, `docs/ai/context-packs/coverage-integrity.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/document-model.md`, `skills/repo-context-ledger/references/production-workflow.md`, `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/repo-context-ledger.mdc`, `.github/copilot-instructions.md`.

Reason: 记录 v0.6.0 的 Bundle/cache/baseline 当前契约、匿名性能证据、跨 Agent 最短读取流程、Capsule evidence 边界与生成入口策略。

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `7655bcccc6bb3b07aab23fdd86f16c048178535b`
- Current commit: `7655bcccc6bb3b07aab23fdd86f16c048178535b`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `.cursor/rules/repo-context-ledger.mdc`
  - `.github/copilot-instructions.md`
  - `AGENTS.md`
  - `CLAUDE.md`
  - `README.md`
  - `README.zh-CN.md`
  - `benchmarks/README.md`
  - `benchmarks/context_router_benchmark.py`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/context-routing-performance.md`
  - `docs/specs/native-context-bridge.md`
  - `docs/specs/task-session-integrity.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/document-model.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
