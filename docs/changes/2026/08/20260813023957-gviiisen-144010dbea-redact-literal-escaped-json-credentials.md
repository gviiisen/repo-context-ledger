# Redact literal escaped JSON credentials

Status: completed
Feature: native-context-bridge
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260813023957-gviiisen-144010dbea
Session ID: 20260813023957-gviiisen-144010dbea
Actor: gviiisen
Branch: agent/release-v0.5.6
Started: 2026-08-13T02:39:57+08:00
Completed: 2026-08-13T02:43:14+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 05336ec3034d7b925e01a3bee431c6f6e952b7b4
Dirty paths: none
Resume summary:
Next step:
Specs: none
Spec exception: The existing native-context-bridge spec already documents JSON credential redaction; this patch only makes escaped JSON output conform to that current contract.

## Intent

Prevent a literal escaped-JSON error payload such as `{\"token\": \"value\"}` from bypassing Failure Capsule redaction. Acceptance requires the persisted failure summary to omit the credential value even when backslashes remain in stderr.

## Changed behavior

Before: Normal JSON and credentials extracted from a command were redacted, but an independently produced stderr line containing escaped quote characters could preserve the JSON credential value.

After: Structured label redaction accepts ordinary or backslash-escaped quotes and conservatively removes text through the field or line boundary. Literal escaped JSON, normal JSON, colon, equals, and whitespace forms use the same fail-closed output sanitizer.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::redact_secret_text` | Sanitizes command and verification text before persistence. | Treats escaped quotes as part of a credential label and redacts the remaining structured field conservatively. |
| `tests/test_ledger.py::test_failed_verification_records_redacted_failure_capsule` | Covers persisted Failure Capsule secrecy. | Adds a direct assertion for literal backslash-escaped JSON stderr independent of command-derived secret values. |

## Boundaries and risks

- Invariant: Raw verification output is never persisted; only its hash and a bounded, sanitized summary remain available for continuation.
- Failure / recovery: The sanitizer intentionally over-redacts the remainder of a labeled field when quoting is ambiguous, preserving secrecy at the cost of some diagnostic detail.
- Not changed: Verification execution, exit status, hashing, context routing, repository discovery, and evidence behavior are unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token>`
  - Status: passed
  - Exit code: 0
  - Duration: 1.59s
  - Recorded: 2026-08-13T02:40:22+08:00
  - Output evidence: sha256:a434e806f5e16dac8044b2d1f961d4256206b6869adc288e0bdeb5bb6f011634 (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py`
  - Status: passed
  - Exit code: 0
  - Duration: 116.31s
  - Recorded: 2026-08-13T02:42:49+08:00
  - Output evidence: sha256:409eebd5053bf7c61fb01baf404bcbd065bc4cc441646ea0223a1079f79ba981 (280 characters captured; content not persisted; last=OK)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `docs/specs/native-context-bridge.md` and `docs/ai/context-packs/native-context-bridge.md` remain the stable contract from the preceding release-review correction.

Reason: Those documents already require common JSON credential forms to be sanitized on both the command and output sides; this correction closes the escaped representation of that same contract.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `05336ec3034d7b925e01a3bee431c6f6e952b7b4`
- Current commit: `05336ec3034d7b925e01a3bee431c6f6e952b7b4`
- Changed paths:
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
