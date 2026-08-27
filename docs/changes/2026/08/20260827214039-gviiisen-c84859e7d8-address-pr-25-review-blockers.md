# Address PR 25 review blockers

Status: completed
Feature: coverage-integrity
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Scope: repository
Handoff ID: 20260827214039-gviiisen-c84859e7d8
Session ID: 20260827214039-gviiisen-c84859e7d8
Actor: gviiisen
Branch: fix/v1.0.1-workflow-boundaries
Started: 2026-08-27T21:40:39+08:00
Completed: 2026-08-27T22:01:31+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 4800d58e9bde70c8f0b55a9afe0f6e7df90480d2
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/coverage-integrity.md
Spec exception: none

## Intent

核验并修复 PR #25 复审指出的合并阻断：让 rename Coverage 理解 base→current Pack 迁移，避免“一行修改”把高风险代码任务降级为小修，并确保功能分支不携带派生索引且 CI 能自动执行 Ledger PR 门禁。验收结果是正确迁移 Pack 的 rename 可以通过，缺失迁移仍失败，PR 分支的 team/Coverage gate 可由 GitHub Actions 复验。

## Changed behavior

Before: Coverage 把 rename 旧、新路径扁平化后只查询当前 Pack 映射，因此正确把 Pack 从旧路径迁移到新路径仍会因旧路径无 current Pack 而失败；`one-line`/`只改一行` 可以独立触发 `small-fix`；PR CI 不执行 Ledger team/Coverage gate，且本分支带有从 `main` 完成 session 时生成的三个派生索引。

After: Coverage 保留 rename transition，从 merge base 读取旧路径 Pack 所有权，从当前工作区读取新路径同 feature Pack 所有权，并要求 source/current Pack 进入本次变更；one-line 只有同时命中低风险文档/注释/文案/示例目标才辅助选择 `small-fix`；PR 新增独立 `ledger-gates`，三个派生索引恢复为 `origin/main` 内容并延后到合并后生成。

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::tracked_context_packs_at_ref` | 从指定 Git ref 读取 current Pack 的 tracked path 与 feature 身份。 | 新增 fail-closed 的 base Pack 映射，供 rename transition 校验旧路径所有权。 |
| `src/repo_context_ledger/runtime.py.tmpl::coverage_validation_errors` | 将 Git 变化、handoff、spec 与 Pack 对齐。 | 保留 rename transition，分别校验 base/source 与 current/destination Pack，并拒绝 feature 不一致或未刷新的迁移。 |
| `src/repo_context_ledger/workflow.pyfrag::build_workflow_plan` | 根据请求信号选择 workflow。 | 将 one-line 从独立强信号降为只对明确低风险文本目标生效的辅助信号。 |
| `.github/workflows/test.yml::jobs.ledger-gates` | 执行 PR 集成门禁。 | 使用完整 Git 历史运行 runtime build、team-check、changed-scope Coverage 与 diff 检查。 |
| `tests/test_ledger.py::test_coverage_accepts_a_rename_when_the_same_feature_pack_moves_with_it` | 通过公开 CLI 验证 rename 的完整文档迁移流程。 | 新增从旧实现、旧 Pack 到新实现、同 feature Pack 的端到端成功用例。 |

## Boundaries and risks

- Invariant: 普通实现路径仍必须由 current Pack 精确覆盖；rename evidence 仍同时包含旧、新路径；copy 来源不算行为实现变更；显式 workflow intent 与 `workflow-plan-v1` 结构保持兼容。
- Failure / recovery: base ref、Pack Git 对象或 UTF-8 内容不可读取时 Coverage fail closed；旧路径无 base Pack、新路径无 current Pack、feature 不一致或相关 Pack 未刷新时返回确定性错误，不会假定迁移完成。
- Not changed: 没有修改公开 CLI/JSON schema/exit class，没有让 Ledger 自动合并代码或派生索引，也没有让 macOS 改为每个普通 push 都运行。

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 293.66s
  - Recorded: 2026-08-27T21:59:43+08:00
  - Output evidence: sha256:76fdca0969f3637d4730626533e5d085500d5a709eba4c3543918ac93c57cecb (25921 characters captured; content not persisted; last=OK (skipped=4))
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.09s
  - Recorded: 2026-08-27T21:59:50+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `ARCHITECTURE.md`, `COMPATIBILITY.md`, `docs/specs/coverage-integrity.md`, `docs/specs/workflow-planning.md`, `docs/specs/contract-stability.md`, `docs/specs/runtime-architecture.md` 及对应 Context Packs。

Reason: rename Pack 迁移、自动 workflow 分类与 PR CI 门禁都是稳定的行为边界，需要让新窗口和外部 Agent 获得当前事实，而不是依赖本次 review 文本。

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `4800d58e9bde70c8f0b55a9afe0f6e7df90480d2`
- Current commit: `4800d58e9bde70c8f0b55a9afe0f6e7df90480d2`
- Changed paths:
  - `.github/workflows/test.yml`
  - `ARCHITECTURE.md`
  - `COMPATIBILITY.md`
  - `docs/ai/context-manifest.json`
  - `docs/ai/context-packs/compact-local-config-workflow.md`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/continuation-quality.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/ai/context-packs/verification-presets.md`
  - `docs/ai/context-packs/workflow-planning.md`
  - `docs/changes/2026/08/README.md`
  - `docs/changes/README.md`
  - `docs/specs/contract-stability.md`
  - `docs/specs/coverage-integrity.md`
  - `docs/specs/runtime-architecture.md`
  - `docs/specs/workflow-planning.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `src/repo_context_ledger/workflow.pyfrag`
  - `tests/fixtures/workflow-plan-eval-v1.json`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
