# Harden raw JSON command detection

Status: completed
Feature: contract-stability
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260822002738-gviiisen-9d24fbee4b
Session ID: 20260822002738-gviiisen-9d24fbee4b
Actor: gviiisen
Branch: feat/v0.7.0-runtime-architecture
Started: 2026-08-22T00:27:38+08:00
Completed: 2026-08-22T00:29:00+08:00
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

Make raw JSON-command detection unambiguous and freeze every published error-code constant in tests. Acceptance requires repository argument values that resemble commands and both `--format json`/`--format=json` spellings to select the actual subcommand schema.

## Changed behavior

Before: the pre-dispatch error detector scanned all raw argument tokens, so a repository named `context` could misclassify a later `status` request, `--format=json` was not detected, and golden error values were checked only for uppercase shape.

After: raw parsing skips the value of global `--repo` options, selects the first actual subcommand, accepts both argparse option spellings, and reads `--query=value`. Golden tests compare every public error code directly to runtime constants and representative emitted payloads.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::requested_json_command` | Selects the schema before normal parsing/repository discovery completes. | Parses the actual subcommand without treating option values as commands and recognizes both JSON format spellings. |
| `src/repo_context_ledger/runtime.py.tmpl::argument_value` | Recovers bounded fields for pre-dispatch error envelopes. | Supports both separated and equals-form arguments. |
| `tests/test_contract_stability.py` | Freezes the public automation contract. | Covers deceptive repository names, equals-form options, exact runtime error constants, and emitted no-match/Doctor codes. |

## Boundaries and risks

- Invariant: Expected JSON failures remain parseable in the requested command schema with exit code 2 and without machine-local paths.
- Failure / recovery: Invalid input still identifies a stable machine error; callers can correct arguments without scraping argparse stderr.
- Not changed: Successful command routing, text output, repository discovery semantics, and schema field meanings are unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_contract_stability.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 10.31s
  - Recorded: 2026-08-22T00:28:20+08:00
  - Output evidence: sha256:0c81967daeebece88b72952754862fed7fb8fca816ebb38de31c67f195710abe (1533 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-22T00:28:20+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 3.81s
  - Recorded: 2026-08-22T00:28:50+08:00
  - Output evidence: sha256:c53c8350dd290ae17ef310a93d3473e4267adf8a8a5d639b74debe1bf663338a (187 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `docs/ai/context-packs/contract-stability.md` and other Context Packs that track the generated standalone runtime.

Reason: The public contract documentation already specifies the behavior; this change closes the implementation/test gap without changing that contract.

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
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_contract_stability.py`
<!-- repo-context-ledger:evidence:end -->
