# Close contract and privacy review gaps

Status: completed
Feature: contract-stability
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260821235319-gviiisen-450163105c
Session ID: 20260821235319-gviiisen-450163105c
Actor: gviiisen
Branch: feat/v0.7.0-runtime-architecture
Started: 2026-08-21T23:53:19+08:00
Completed: 2026-08-22T00:12:56+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: f71e59fd47dfa3a39d192d3bee2c7990d365320b
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/contract-stability.md
Spec exception: none

## Intent

Close the blocking privacy, JSON-contract, evaluation, and source-architecture gaps found during the v0.6.1/v0.6.2/v0.7.0 review. Acceptance requires foreign private session fields to remain invisible to Doctor, every requested JSON mode to return its versioned envelope on expected failures, stable error/schema compatibility tests, a representative routing evaluation, and deterministic generation from separately ordered low-coupling fragments.

## Changed behavior

Before: Doctor traversed every private session and could name a foreign session when diagnosing an orphan. `status --format json` and `check --format json` could fall back to plain stderr for expected `LedgerError` failures, invalid Doctor bounds were silently clamped, future schemas were accepted, the routing fixture tested only straightforward top-one selection, and the build injected one combined contracts fragment.

After: Doctor inspects only sessions owned by the current principal and rejects out-of-range detail bounds. Context, status, Doctor, and check JSON contracts publish stable required fields and machine error codes for expected outcomes, including no-match and unsupported future schemas. Golden baselines cover dry-run write safety, legacy state normalization, and normalized text; the routing evaluator reports top-one accuracy, ambiguity/fallback, stale/superseded selection, required-read characters, and latency. The standalone runtime is built deterministically from ordered constants, errors, and models fragments while retaining one zero-dependency generated artifact.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::doctor_state_findings` | Enforces the private-state diagnostic boundary. | Filters session diagnostics through owner/legacy-owner access before reading paths or reporting fields. |
| `src/repo_context_ledger/runtime.py.tmpl::context_search` | Produces `context-bundle-v1`. | Returns a stable no-match JSON envelope and required contract fields. |
| `src/repo_context_ledger/runtime.py.tmpl::captured_command_json` | Projects command results into versioned JSON. | Captures expected `LedgerError` failures and emits stable error codes without falling back to plain stderr. |
| `src/repo_context_ledger/runtime.py.tmpl::show_status` | Produces `status-v1`. | Keeps initialization/configuration failures inside the status schema and rejects unsupported future configuration schemas. |
| `src/repo_context_ledger/constants.pyfrag` | Owns low-coupling public constants. | Separates versions, schemas, exit classes, and stable error-code constants from the runtime body. |
| `src/repo_context_ledger/errors.pyfrag` | Owns expected workflow failures. | Gives `LedgerError` a stable machine code while preserving existing messages. |
| `src/repo_context_ledger/models.pyfrag` | Owns typed result contracts. | Extends `CommandResult` with `error_code` without adding runtime dependencies. |
| `scripts/build_runtime.py::render_runtime` | Produces both standalone runtime artifacts. | Injects the three ordered fragments deterministically and continues detecting output drift. |
| `scripts/evaluate_routing.py::evaluate` | Measures the synthetic routing contract. | Reports accuracy, ambiguity/fallback, lifecycle selection, required-read characters, and latency without production data. |

## Boundaries and risks

- Invariant: Human text commands and exit classes `0`, `1`, and `2` remain compatible; generated Skill and dogfood runtimes remain byte-identical, standalone, and standard-library-only.
- Failure / recovery: Unknown future schemas fail closed with `UNSUPPORTED_SCHEMA`; expected JSON failures remain parseable, while malformed CLI syntax still follows argparse's exit-2 contract. Repair canonical fragments/template and rebuild rather than editing a generated runtime.
- Not changed: Doctor remains advisory and read-only, Pack overlap remains a warning rather than automatic superseding, private state remains clone/worktree local, and no production repository data enters fixtures.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 216.25s
  - Recorded: 2026-08-22T00:11:28+08:00
  - Output evidence: sha256:470c431bce980d8b7ed4a79ffac4e9cd5a2f62a1a9c5325c09cb6c72cdb860cb (15625 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-22T00:12:07+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: failed
  - Exit code: 1
  - Duration: 0.06s
  - Recorded: 2026-08-22T00:12:08+08:00
  - Output evidence: sha256:1b0c67ad174307c1a7129187803407ed0656069d32f388ccbde2e87ded52f64b (694 characters captured; content not persisted; failure=Traceback (most recent call last): | UnicodeDecodeError: 'gbk' codec can't decode byte 0x92 in position 2499: illegal multibyte sequence)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-22T00:12:14+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 3.61s
  - Recorded: 2026-08-22T00:12:34+08:00
  - Output evidence: sha256:0fd041f379008a5b54e8359391a78c50bbce6c9391d73585087d8fccc1e83f39 (187 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `ARCHITECTURE.md`, `COMPATIBILITY.md`, `README.md`, `README.zh-CN.md`, `docs/specs/contract-stability.md`, `docs/specs/pack-health-doctor.md`, `docs/specs/runtime-architecture.md`, and the affected Context Packs.

Reason: Document the stable error/schema boundary, platform matrix, privacy rule, routing evaluation, and ordered canonical-source architecture used by future contributors and Agents.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `f71e59fd47dfa3a39d192d3bee2c7990d365320b`
- Current commit: `f71e59fd47dfa3a39d192d3bee2c7990d365320b`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/contract-stability.md`
  - `docs/specs/pack-health-doctor.md`
  - `docs/specs/runtime-architecture.md`
  - `scripts/build_runtime.py`
  - `scripts/evaluate_routing.py`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/contracts.pyfrag`
  - `src/repo_context_ledger/errors.pyfrag`
  - `src/repo_context_ledger/models.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
<!-- repo-context-ledger:evidence:end -->
