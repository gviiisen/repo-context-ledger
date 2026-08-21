# Stabilize CLI contracts and compatibility matrix

Status: completed
Feature: contract-stability
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260821232648-gviiisen-09ef2502eb
Session ID: 20260821232648-gviiisen-09ef2502eb
Actor: gviiisen
Branch: feat/v0.6.2-contract-stability
Started: 2026-08-21T23:26:48+08:00
Completed: 2026-08-21T23:35:33+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: db89319282707f639addbd92e6e6fd1f8e88444d
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/contract-stability.md
Spec exception: none

## Intent

Stabilize the public CLI and upgrade boundary before modularizing the runtime. Acceptance requires explicit versioned JSON for automation, preserved existing context and Doctor schemas, documented exit/migration rules, a production-free routing evaluation, and supported-platform CI coverage.

## Changed behavior

Before: `context` and `doctor` had JSON schemas, but `status` and `check` required consumers to parse human text; compatibility, migration, required JSON fields, exit classes, and the Python/OS support matrix were not captured as one enforced contract.

After: `status-v1` and `check-v1` provide privacy-bounded automation output while preserving text and exits; golden fixtures protect all public schema names/fields and exits; synthetic cases evaluate routing; compatibility/migration rules and Windows/Ubuntu Python 3.10/3.12 CI are explicit.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::status_report` | Owns structured state inventory. | Added `status-v1` with owned/shared detail, foreign count only, and no machine-local state path. |
| `skills/repo-context-ledger/scripts/ledger.py::captured_command_json` | Owns non-breaking JSON projection. | Added `check-v1` with separated messages/errors and unchanged exit code. |
| `tests/test_contract_stability.py` | Enforces the release contract. | Added schema, privacy, exit, broken-check, and synthetic routing evaluation tests. |
| `.github/workflows/test.yml` | Defines supported CI boundaries. | Expanded Windows/Ubuntu runs across Python 3.10 and 3.12. |

## Boundaries and risks

- Invariant: existing text commands, `context-bundle-v1`, `doctor-v1`, v8 repository configuration, private session permissions, and exit classes remain compatible; JSON contains no absolute repository or workspace-state path.
- Failure / recovery: a golden or routing evaluation failure blocks release until the change is additive or receives a new schema and major-version migration; text remains the human recovery surface.
- Not changed: command semantics, context ranking algorithm, Pack health rules, state migration behavior, documentation layers, and vendor-private Memory boundaries are unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_contract_stability.py`
  - Status: failed
  - Exit code: 1
  - Duration: 0.25s
  - Recorded: 2026-08-21T23:27:49+08:00
  - Output evidence: sha256:a8e453f6973770c4a747eacc99ef1c5993b40f5830d9d196e9af31bbaa3d938d (2683 characters captured; content not persisted; failure=Traceback (most recent call last): | self.assertEqual(expected, result.returncode, result.stdout + result.stderr) | File "<USER_HOME>\AppData\Local\Programs\Python\Python312\Lib\unittest\case.py", line 885, in assertEqual | assertion_func(first, second, msg=msg) | File "<USER_HOME>\AppData\Local\Programs\Python\Python312\Lib\unittest\case.py", line 878, in _baseAssertEqual | raise self.failureException(msg) | AssertionError: 0 != 2 : usage: ledger.py [-h] [--version] [--repo REPO] | ledger.py: error: the following arguments are required: command)
- Command: `python -m unittest discover -s tests -p test_contract_stability.py`
  - Status: passed
  - Exit code: 0
  - Duration: 2.91s
  - Recorded: 2026-08-21T23:30:48+08:00
  - Output evidence: sha256:481d0799e27c1f5cd55ca4fcbbc7b3880f104ce1d2bf1e73898b0de6c5f6cf0f (102 characters captured; content not persisted; last=OK)
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-21T23:31:37+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 195.78s
  - Recorded: 2026-08-21T23:34:53+08:00
  - Output evidence: sha256:e94f76dfc7b5377f67c08111f211f6eb3df42e09cbd23ba46217f543ae6ab86d (13976 characters captured; content not persisted; last=OK)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main`
  - Status: failed
  - Exit code: 2
  - Duration: 2.39s
  - Recorded: 2026-08-21T23:35:02+08:00
  - Output evidence: sha256:30052367809de8ccd3998a2c4e968196e9b006e2b6c3408858d8a589b14471ef (315 characters captured; content not persisted; failure=ERROR: Behavior-changing path has no related Context Pack tracked file: COMPATIBILITY.md | ERROR: Behavior-changing path has no related Context Pack tracked file: MIGRATIONS.md)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 2.23s
  - Recorded: 2026-08-21T23:35:13+08:00
  - Output evidence: sha256:ef2dd05d5605d481006439fcb185ff2c14c5007694486acbc012eebe4adff210 (187 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `COMPATIBILITY.md`, `MIGRATIONS.md`, `README.md`, `README.zh-CN.md`, `skills/repo-context-ledger/SKILL.md`, `docs/specs/contract-stability.md`, and affected Context Packs.

Reason: Publish the supported environments, JSON and exit contracts, additive minor-version policy, major-version boundary, upgrade/rollback procedure, and minimum loading route.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `db89319282707f639addbd92e6e6fd1f8e88444d`
- Current commit: `db89319282707f639addbd92e6e6fd1f8e88444d`
- Changed paths:
  - `.github/workflows/test.yml`
  - `COMPATIBILITY.md`
  - `MIGRATIONS.md`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/contract-stability.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/fixtures/routing-eval-v1.json`
  - `tests/golden/v0.6.2-cli-contract.json`
  - `tests/test_contract_stability.py`
<!-- repo-context-ledger:evidence:end -->
