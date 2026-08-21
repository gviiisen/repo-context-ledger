# Build Pack health diagnostics and lifecycle governance

Status: completed
Feature: pack-health-doctor
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260821230730-gviiisen-4c00275b82
Session ID: 20260821230730-gviiisen-4c00275b82
Actor: gviiisen
Branch: feat/v0.6.1-pack-health-doctor
Started: 2026-08-21T23:07:30+08:00
Completed: 2026-08-21T23:26:03+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: b5086a53c21962593ada4a0b96903faf10a7e54c
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/pack-health-doctor.md
Spec exception: none

## Intent

Add a bounded, read-only health command that turns Pack freshness and lifecycle debt into one actionable report. The accepted result is a stable text/JSON command that diagnoses large repositories without changing their files or inferring semantic Pack replacement from shared code paths.

## Changed behavior

Before: repository-wide strict checks emitted individual stale errors and separate adapter, Manifest, state, and link checks; there was no single health report, bounded detail contract, or explicit Pack lineage diagnosis.

After: `doctor` emits `doctor-v1` or a text projection with grouped Pack findings, stable severities/codes, capped details, repair suggestions, configuration/runtime/adapter/Manifest/state/link/derived checks, and explicit non-mutating lifecycle rules.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::doctor_repo` | Owns the health report and CLI exit contract. | Added read-only aggregation, rendering, root redaction, and error-only failure exit behavior. |
| `skills/repo-context-ledger/scripts/ledger.py::doctor_pack_findings` | Owns Pack freshness and lifecycle diagnosis. | Added grouping for stale/missing paths, duplicate features, intentional overlap warnings, and explicit lineage validation. |
| `tests/test_contract_and_doctor.py` | Protects compatibility and Doctor behavior. | Added v0.6.0 golden baseline plus read-only, privacy, bounded output, link, state, overlap, and lineage cases. |

## Boundaries and risks

- Invariant: Doctor reads live repository state, exposes only repository-relative bounded detail, and never mutates files, fingerprints, sessions, Pack status, lineage, or derived indexes.
- Failure / recovery: invalid configuration and private state become redacted structured errors; repairable debt remains exit-success so users can schedule it without confusing it with a broken deterministic contract.
- Not changed: `context-bundle-v1`, existing lifecycle commands, full and changed-scope checks, router cache authority, Git collaboration, and the three-layer Pack/spec/Change model remain unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_contract_and_doctor.py`
  - Status: failed
  - Exit code: 1
  - Duration: 5.66s
  - Recorded: 2026-08-21T23:11:23+08:00
  - Output evidence: sha256:1c9bc053095a4f253890db6b0a87f1618f398444bbf6a86b11c0e54f3c22b341 (5111 characters captured; content not persisted; failure=AssertionError: 0 != 2 : usage: ledger.py [-h] [--version] [--repo REPO] | ledger.py: error: argument command: invalid choice: 'doctor' (choose from 'init', 'start', 'context', 'pack', 'focus', 'checkpoint', 'pause', 'resume', 'share', 'finish', 'evidence', 'verify', 'sync', 'manifest', 'adapters', 'check', 'team-check', 'status') | FAIL: <redacted-token> (test_contract_and_doctor.ContractAndDoctorTests.<redacted-token>) | Traceback (most recent call last): | self.assertEqual(expected, result.returncode, result.stdout + result.stderr) | AssertionError: 0 != 2 : usage: ledger.py [-h] [--version] [--repo REPO] | ledger.py: error: argument command: invalid choice: 'doctor' (choose from 'init', 'start', 'context', 'pack', 'focus', 'checkpoint', 'pause', 'resume', 'share', 'finish', 'evidence',…)
- Command: `python -m unittest discover -s tests -p test_contract_and_doctor.py`
  - Status: passed
  - Exit code: 0
  - Duration: 10.91s
  - Recorded: 2026-08-21T23:17:02+08:00
  - Output evidence: sha256:6a74533ed35bc91d7f7997d35b063c500f2bed50577b40432111edeb06f4fd6f (106 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -v`
  - Status: failed
  - Exit code: 1
  - Duration: 202.56s
  - Recorded: 2026-08-21T23:20:33+08:00
  - Output evidence: sha256:58939c9190e980b84e99fab2b859bac6d1095abc093b9eb638abe4cb358c87ce (13779 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... Injected post-publication failure. | Published record validation failed; the private draft and session were preserved for recovery. | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertEqual("0.6.0", manifest["tool_version"]) | AssertionError: '0.6.0' != '0.6.1' | FAILED (failures=1))
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: failed
  - Exit code: 1
  - Duration: 0.12s
  - Recorded: 2026-08-21T23:20:55+08:00
  - Output evidence: sha256:9219ea1c79fd2886e4ffe053f165b8c440ca2553ab0aff6d9ee0acbccdf59495 (694 characters captured; content not persisted; failure=Traceback (most recent call last): | UnicodeDecodeError: 'gbk' codec can't decode byte 0x92 in position 2270: illegal multibyte sequence)
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.05s
  - Recorded: 2026-08-21T23:21:01+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 199.98s
  - Recorded: 2026-08-21T23:25:09+08:00
  - Output evidence: sha256:6478f514f5e5d9bc2fd67ec46d590d305939173ec15043bf9cee6a119f0bf6f8 (13220 characters captured; content not persisted; last=OK)
- Command: `python .context-ledger/ledger.py doctor --format json`
  - Status: passed
  - Exit code: 0
  - Duration: 1.58s
  - Recorded: 2026-08-21T23:25:22+08:00
  - Output evidence: sha256:ec36b3df5290c425978a9dc3707ddca0a31134503f00528bb6067a9538a012ca (3260 characters captured; content not persisted; last=})
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main`
  - Status: failed
  - Exit code: 2
  - Duration: 2.06s
  - Recorded: 2026-08-21T23:25:25+08:00
  - Output evidence: sha256:b23a40835f02cf5a8453bf333a32066203d90a95f5ae9a69759df2364a9333a4 (1003 characters captured; content not persisted; failure=ERROR: docs/specs/pack-health-doctor.md: Stable spec data flow requires a substantive Input: value. | ERROR: docs/specs/pack-health-doctor.md: Stable spec data flow requires a substantive Flow: value. | ERROR: docs/specs/pack-health-doctor.md: Stable spec data flow requires a substantive Persistence / dependencies: value. | ERROR: docs/specs/pack-health-doctor.md: Stable spec data flow requires a substantive Output: value. | ERROR: docs/specs/pack-health-doctor.md: Stable spec boundaries require a substantive Invariants: value. | ERROR: docs/specs/pack-health-doctor.md: Stable spec boundaries require a substantive Permissions / concurrency: value. | ERROR: docs/specs/pack-health-doctor.md: Stable spec boundaries require a substantive Failure / recovery: value. | ERROR: docs/specs/pack-heal…)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 2.03s
  - Recorded: 2026-08-21T23:25:57+08:00
  - Output evidence: sha256:2f844b528239f9e3c0ea74441ceeeff813bb7588f9d69d6cffe365105850df6c (187 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/document-model.md`, `skills/repo-context-ledger/references/production-workflow.md`, `docs/specs/pack-health-doctor.md`, and affected Context Packs.

Reason: Document the command contract, non-mutating lifecycle boundary, large-repository usage, repair semantics, and minimum loading route.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `b5086a53c21962593ada4a0b96903faf10a7e54c`
- Current commit: `b5086a53c21962593ada4a0b96903faf10a7e54c`
- Changed paths:
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/pack-health-doctor.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/document-model.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/golden/v0.6.0-contract.json`
  - `tests/test_contract_and_doctor.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
