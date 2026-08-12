# 修正 Coverage 分类与 Context Pack 关联

Status: completed
Feature: coverage-integrity
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Handoff ID: 20260812002950-gviiisen-495d91c753
Actor: gviiisen
Branch: main
Started: 2026-08-12T00:29:50+08:00
Completed: 2026-08-12T00:38:19+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/coverage-integrity.md
Spec exception: none

## Intent

修正 `check --coverage` 把测试、CI、配置等路径一律当成生产实现，以及修改任意 Context Pack 即可通过门禁的问题。验收结果是路径分类可配置且经过校验，每个生产路径必须由实际跟踪它并在本次变更中刷新的 Context Pack 覆盖，同时已有 v5 仓库保持兼容。

## Changed behavior

Before: `is_implementation_path` 只排除少量固定目录，测试与 CI 等路径会触发完整行为记录；Coverage 只检查是否存在任意 changed Pack，因此无关 Pack 也能满足门禁。

After: `coverage_path_kind` 按受管路径及可配置 glob 区分生产实现、测试、CI、配置、生成与忽略路径；`coverage_validation_errors` 对每个生产路径校验精确 tracked-file 关联，并拒绝未刷新或完全无关的 Pack。

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py` / `normalize_coverage_globs` | Coverage 配置入口。 | 增加六类 glob 的默认值、类型检查、仓库相对路径检查、去重与向后兼容默认值。 |
| `skills/repo-context-ledger/scripts/ledger.py::coverage_path_kind` | Git 路径分类。 | 修正隐藏目录前缀规范化，并按 ignore、generated、test、CI、config、implementation 的顺序确定类别。 |
| `skills/repo-context-ledger/scripts/ledger.py::tracked_context_packs` | 路径与 Pack 关联索引。 | 从 Context Pack 指纹块建立精确 tracked-file 到 Pack 的确定性映射。 |
| `skills/repo-context-ledger/scripts/ledger.py::coverage_validation_errors` | Coverage 门禁。 | 逐个生产路径报告无关联 Pack 或相关 Pack 未修改，不再接受任意 changed Pack。 |
| `tests/test_ledger.py::LedgerFlowTests` | 运行时回归测试。 | 新增路径分类、test/CI-only 放行、非法 glob、无关 Pack 绕过和相关 Pack 刷新场景，并将 Manifest 版本断言更新到 `0.5.1`。 |

## Boundaries and risks

- Invariant: handoff evidence 与稳定 spec/明确例外仍是生产行为变更的必需记录；Context Pack 关联只使用 Git 中可验证的精确 tracked file。
- Failure / recovery: 非法或越界 glob 会拒绝加载配置；分类不符合项目布局时可修改 `.context-ledger/config.json` 后重跑 `init` 或检查，缺少 Pack 时应创建或刷新实际相关 Pack。
- Not changed: 未加入 Light Mode、LLM 语义门禁或多文件运行时分发；本任务建立在已有未提交的 v0.5.0 Native Context Bridge 工作树上，原有 bridge 文件与历史记录均被保留。

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_ledger.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 78.38s
  - Recorded: 2026-08-12T00:35:32+08:00
  - Output evidence: sha256:2f47e79bff02b944774d4269aa888a342c28b1ae7a0e9bebb09779565ccc2c79 (5648 characters captured; content not persisted)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`、`README.zh-CN.md`、`skills/repo-context-ledger/SKILL.md`、`skills/repo-context-ledger/references/document-model.md`、`docs/specs/coverage-integrity.md`、`docs/ai/context-packs/coverage-integrity.md`、`docs/ai/context-packs/native-context-bridge.md`。

Reason: 记录 v0.5.1 的用户配置、相关 Pack Coverage 契约、迁移边界、代码入口及跨 Agent 最小加载路线。

## Open questions

None. 后续 Light Mode、证据与 diff 的结构化对齐及 symbol 级关联不属于本版本。

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98`
- Current commit: `da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98`
- Changed paths:
  - `.context-ledger/config.json`
  - `.context-ledger/ledger.py`
  - `.context-ledger/templates/context-pack-template.md`
  - `.context-ledger/templates/handoff-template.md`
  - `.context-ledger/templates/project-context-template.md`
  - `.context-ledger/templates/spec-template.md`
  - `.context-ledger/writing-quality.md`
  - `.cursor/rules/repo-context-ledger.mdc`
  - `.github/copilot-instructions.md`
  - `AGENTS.md`
  - `CLAUDE.md`
  - `README.md`
  - `README.zh-CN.md`
  - `docs/ai/context-manifest.json`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/project-context.md`
  - `docs/changes/2026/08/20260811211310-gviiisen-5a44822643-implement-native-context-bridge.md`
  - `docs/changes/2026/08/20260812002950-gviiisen-495d91c753-coverage-context-pack.md`
  - `docs/changes/2026/08/README.md`
  - `docs/changes/README.md`
  - `docs/specs/README.md`
  - `docs/specs/coverage-integrity.md`
  - `docs/specs/native-context-bridge.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/agents/openai.yaml`
  - `skills/repo-context-ledger/assets/handoff-template.md`
  - `skills/repo-context-ledger/references/document-model.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
