# Complete outer JSON error boundary

Status: completed
Feature: contract-stability
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260822001817-gviiisen-3767cb15f0
Session ID: 20260822001817-gviiisen-3767cb15f0
Actor: gviiisen
Branch: feat/v0.7.0-runtime-architecture
Started: 2026-08-22T00:18:17+08:00
Completed: 2026-08-22T00:23:37+08:00
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

Close the remaining v0.6.2 review blockers at the outermost CLI and evaluation boundaries. Every JSON-capable command must remain parseable from argument validation and repository discovery through command execution; future schemas must use one stable error code; the routing corpus must exercise shared production ranking; macOS must run nightly; and the v0.6.0 migration baseline must verify persisted behavior.

## Changed behavior

Before: JSON requests could fall back to argparse/plain stderr before command dispatch, future-schema errors were classified differently by command, routing evaluation duplicated lifecycle/ranking logic and trusted numeric fixture sizes, macOS ran weekly, and migration coverage normalized only an in-memory object.

After: a shared outer JSON boundary emits `context-bundle-v1`, `doctor-v1`, `status-v1`, or `check-v1` for expected parse/repository/configuration failures with stable error codes. All commands return `UNSUPPORTED_SCHEMA` for future configuration/state. Production and evaluation share routability and ranking helpers; the corpus asserts ambiguity, fallback, stale and superseded behavior while measuring generated Pack text size and latency. macOS runs nightly, and a checked-in legacy fixture is dry-run preserved then persistently migrated by real `init`.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::emit_requested_json_error` | Owns the pre-dispatch automation error boundary. | Emits each command's versioned schema for argument, repository, and configuration failures without plain stderr fallback. |
| `src/repo_context_ledger/runtime.py.tmpl::rank_context_pack_candidates` | Owns the production metadata/baseline/session ranking boundary. | Extracts shared deterministic ranking used by live context routing and the synthetic evaluator. |
| `src/repo_context_ledger/runtime.py.tmpl::routable_context_pack` | Owns Pack lifecycle eligibility. | Gives production loading and evaluation one current/non-superseded rule. |
| `scripts/evaluate_routing.py::evaluate` | Produces the routing quality report. | Uses production helpers, derives read characters from representative Pack text, and fails expectations for ambiguity/fallback/stale/superseded cases. |
| `tests/test_baseline_contract.py` | Protects the pre-change compatibility baseline. | Runs dry-run and real persisted migration from a checked-in legacy state fixture. |
| `.github/workflows/test.yml` | Defines the supported platform matrix. | Changes the macOS scheduled validation from weekly to nightly while keeping release/manual coverage. |

## Boundaries and risks

- Invariant: Existing schema names, required fields, human text behavior, and exit classes remain compatible; foreign private fields and machine-local paths remain absent from JSON output.
- Failure / recovery: Expected invalid input and unsupported schema failures return exit 2 with a stable machine code. Malformed automation requests can inspect the schema error and repair input without scraping stderr.
- Not changed: Routing still treats required reads as an initial direction rather than a cap on code inspection; Doctor remains read-only; Pack superseding remains explicit; fixtures contain no production data.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_contract_stability.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 9.66s
  - Recorded: 2026-08-22T00:18:59+08:00
  - Output evidence: sha256:1993dd63f4ae8e3ce1f606c9b423c5f52bfa14cf83bd221fe1000a7bb14adea5 (1360 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_doctor.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 13.83s
  - Recorded: 2026-08-22T00:19:14+08:00
  - Output evidence: sha256:1c388816e1dd7e923980dd3884edb71e2e181fb6ebd60a15289ecffd40c8eb88 (1335 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-22T00:19:15+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -m unittest discover -s tests -p test_baseline_contract.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 2.95s
  - Recorded: 2026-08-22T00:23:16+08:00
  - Output evidence: sha256:2253319b7120385ada89255290bf93e523e946ea26266e0e5b8691fb0c88392d (586 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_contract_stability.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 8.19s
  - Recorded: 2026-08-22T00:23:25+08:00
  - Output evidence: sha256:8b56df4e3c73817942c3214b9930203695ea938ba00e4dbbceff415377333973 (1360 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_routing_evaluation.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 0.16s
  - Recorded: 2026-08-22T00:23:26+08:00
  - Output evidence: sha256:a7ca22d608d8d5e8010b8ba5d6154758d3c017a121da5e197e0cf7ac11206a40 (287 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-22T00:23:26+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 3.53s
  - Recorded: 2026-08-22T00:23:35+08:00
  - Output evidence: sha256:82a2cf92f1edc1d00a8196526ffcdd8f0a6b5a9c5ea29a3f1bfb1560170e651e (187 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `COMPATIBILITY.md`, `docs/specs/contract-stability.md`, and the affected Context Packs.

Reason: Preserve the public error, platform, migration, and evaluation contracts for automation and future maintainers.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `f71e59fd47dfa3a39d192d3bee2c7990d365320b`
- Current commit: `f71e59fd47dfa3a39d192d3bee2c7990d365320b`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `.github/workflows/test.yml`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/contract-stability.md`
  - `scripts/evaluate_routing.py`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/fixtures/v0.6.0-legacy-context-state.json`
  - `tests/test_baseline_contract.py`
  - `tests/test_contract_stability.py`
  - `tests/test_doctor.py`
  - `tests/test_routing_evaluation.py`
<!-- repo-context-ledger:evidence:end -->
