# Context Router 失败摘要与仓库根发现

Status: completed
Feature: native-context-bridge
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Handoff ID: 20260813020044-gviiisen-418ac132d0
Session ID: 20260813020044-gviiisen-418ac132d0
Actor: gviiisen
Branch: main
Started: 2026-08-13T02:00:44+08:00
Completed: 2026-08-13T02:15:44+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 16b83b3771dd6b29073a6d015bf5c6e5f3a7e2fe
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/native-context-bridge.md
Spec exception: none

## Intent

让换编辑器后续工时，第一个命令就能找到对的 Context Pack，失败验证能带走脱敏原因，并且不必在子目录里手写 `--repo`。验收：`context --query` 返回一个主 Pack 及选择原因；失败 `verify` 不含原始 secret/URL；省略 `--repo` 能从子目录找到仓库根。

## Changed behavior

Before: `context --query` 对 `docs/ai` 和 `docs/specs` 做词频打分，长文档会压过真正的 Pack。省略 `--repo` 时把当前目录当成仓库根。`verify` 失败只留 hash。Code paths 必须再写一遍纯文件路径。Skill 把 11 步完整流程放在最前面。

After: `context --query` 读取 live Pack，按 feature/title/tracked path 选择一个主 Pack 和关联 spec，superseded 与过期指纹被降权。省略 `--repo` 向上寻找 `.context-ledger/config.json`，遇到嵌套 Git 边界停止。失败验证写入脱敏 Failure Capsule；成功仍只留 hash 和最后一行。`file.go::Symbol` 用路径部分对齐 evidence。自动 evidence 跳过 generated/managed，实现文件过多则拒绝整树吞入。Skill 先给出只读/小修/并行/中大改四条最短路径。

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::context_search` | 给下一窗口选择 Context Pack。 | 改为 live Pack 路由器，不再全文词频排序。 |
| `skills/repo-context-ledger/scripts/ledger.py::discover_repo` | 解析仓库根。 | 省略 `--repo` 时向上发现 config，显式 `--repo` 仍优先。 |
| `skills/repo-context-ledger/scripts/ledger.py::verification_output_summary` | 记录验证输出。 | 失败写入脱敏 capsule；命令参数中的 secret 从输出中剔除。 |
| `skills/repo-context-ledger/scripts/ledger.py::cited_code_path` | 解析 Code paths 引用。 | `file.go::Symbol` 只取路径再与 evidence 对齐。 |
| `skills/repo-context-ledger/SKILL.md` | Agent 工作流说明。 | 最短路径前置，完整 11 步不再是默认入口。 |

## Boundaries and risks

- Invariant: 共享文件仍可属于多个 current Pack；只有 `status: superseded` 或 `Superseded by` 会降低排名。不引入第四层文档，Ledger 不管代码锁和 worktree。
- Failure / recovery: 找不到 Pack 时 `context` 返回 1 并提示创建 Pack。自动 evidence 过大时 fail closed，要求 `--path`。验证摘要脱敏失败时宁可多红acted，也不写原始日志。
- Not changed: 未做 `init --dry-run`、`pack --from-session`、强制 Tool 元数据，也未禁止文件重叠的 Pack。

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_ledger.py`
  - Status: passed
  - Exit code: 0
  - Duration: 103.31s
  - Recorded: 2026-08-13T02:14:36+08:00
  - Output evidence: sha256:0909497054d54288c5bb71f87ca933f68010b11acc2075001bab6144371ca51c (280 characters captured; content not persisted; last=OK)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `docs/specs/native-context-bridge.md`、`docs/ai/context-packs/native-context-bridge.md`、`skills/repo-context-ledger/SKILL.md`、`skills/repo-context-ledger/references/document-model.md`、`README.md`、`README.zh-CN.md`。

Reason: 记录 Context Router、仓库根发现、Failure Capsule 和 Skill 最短路径的当前行为，避免下一窗口仍按词频搜索和 11 步流程执行。

## Open questions

未做 `init --dry-run`、`pack --from-session` 和强制 Tool 元数据。Pack 谱系的显式 `Supersedes` 写入规则仍待 v0.6.0。

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `16b83b3771dd6b29073a6d015bf5c6e5f3a7e2fe`
- Current commit: `16b83b3771dd6b29073a6d015bf5c6e5f3a7e2fe`
- Changed paths:
  - `README.md`
  - `README.zh-CN.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/specs/native-context-bridge.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/document-model.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
