# Harden Failure Capsule redaction before v0.5.6 release

Status: completed
Feature: native-context-bridge
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260813023156-gviiisen-640b12d3d4
Session ID: 20260813023156-gviiisen-640b12d3d4
Actor: gviiisen
Branch: agent/release-v0.5.6
Started: 2026-08-13T02:31:56+08:00
Completed: 2026-08-13T02:37:53+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 727b10eec08e544e9272fbc61fd2b8a4f9be2112
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/native-context-bridge.md
Spec exception: none

## Intent

Close the release-review gap that allowed colon-, JSON-, or whitespace-delimited credentials to remain in a failed verification handoff. Acceptance requires the same extracted secret values to be removed from both the displayed command and the bounded Failure Capsule, with regression coverage for every supported separator.

## Changed behavior

Before: Failure Capsule redaction covered URLs, long token-like strings, `key=value`, and bearer-style output, but inline commands could still persist values written as `password: value`, `"token": "value"`, or `api_key value`.

After: Command arguments are scanned for common labeled credential forms before display. Structured `=`, `:`, JSON/quoted, and whitespace-delimited values are replaced consistently in the displayed command, failed output excerpt, and successful last-line summary.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::secret_values_from_command` | Extracts labeled credential values from verification command arguments. | Recognizes equals, colon, quoted/JSON, escaped-quote, and whitespace separators and deduplicates the extracted values. |
| `skills/repo-context-ledger/scripts/ledger.py::redact_secret_text` | Sanitizes persisted command and verification summaries. | Redacts the same structured credential forms before bounded output is recorded. |
| `tests/test_ledger.py::test_failed_verification_records_redacted_failure_capsule` | Prevents raw verification secrets from entering a handoff. | Covers URL credentials plus colon, JSON, and whitespace-delimited secret values across command and output persistence. |

## Boundaries and risks

- Invariant: Verification commands still run unchanged; redaction affects only the bounded text persisted in the task draft and eventual completed history.
- Failure / recovery: Unknown unlabeled data cannot be classified deterministically, so raw logs remain unpersisted and the capsule remains length-bounded. Recognized credential labels fail closed by redacting their associated value.
- Not changed: Context routing, repository discovery, evidence selection, Pack lineage, and `init --dry-run` behavior are unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token>`
  - Status: failed
  - Exit code: 1
  - Duration: 1.47s
  - Recorded: 2026-08-13T02:32:50+08:00
  - Output evidence: sha256:c223619fa9c8a3c237ae9be84240343ce9c5e9f24edc08fe14e88688f6e6bd39 (3127 characters captured; content not persisted; failure=FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertNotIn("json-secret-value", text) | AssertionError: 'json-secret-value' unexpectedly found in '# Record failure capsule\n\nStatus: active\nFeature: record-failure-capsule\nQuality profile: evidence-v1\nLanguage: en\nDetail: standard\nHandoff ID: <redacted-token>\nSession ID: <redacted-token>\nActor: gviiisen\nBranch: detached\nStarted: 2026-08-13T02:32:49+08:00\nCompleted:\nPaused:\nResumed:\nCheckpointed:\nCheckpoint actor:\nBase commit: none\nDirty paths: none\nResume summary:\nNext step:\nSpecs: none\nSpec exception:\n\n## Intent\n\nDeliver the requested behavior and make its acceptance result observable to callers.\n\n## Changed behavior\n\nBefore: The previous behavio…)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token>`
  - Status: failed
  - Exit code: 1
  - Duration: 1.47s
  - Recorded: 2026-08-13T02:33:21+08:00
  - Output evidence: sha256:b6f64e5119c55a698defe5d8d552654378e0b0938d18dbf2f75e5f13f4f6d691 (3127 characters captured; content not persisted; failure=FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertNotIn("json-secret-value", text) | AssertionError: 'json-secret-value' unexpectedly found in '# Record failure capsule\n\nStatus: active\nFeature: record-failure-capsule\nQuality profile: evidence-v1\nLanguage: en\nDetail: standard\nHandoff ID: <redacted-token>\nSession ID: <redacted-token>\nActor: gviiisen\nBranch: detached\nStarted: 2026-08-13T02:33:20+08:00\nCompleted:\nPaused:\nResumed:\nCheckpointed:\nCheckpoint actor:\nBase commit: none\nDirty paths: none\nResume summary:\nNext step:\nSpecs: none\nSpec exception:\n\n## Intent\n\nDeliver the requested behavior and make its acceptance result observable to callers.\n\n## Changed behavior\n\nBefore: The previous behavio…)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token>`
  - Status: passed
  - Exit code: 0
  - Duration: 1.48s
  - Recorded: 2026-08-13T02:33:50+08:00
  - Output evidence: sha256:5d8a6a3ec582b58316b7ed688fcb2aeea279a3b754899173864739a6e537b60f (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py`
  - Status: passed
  - Exit code: 0
  - Duration: 103.81s
  - Recorded: 2026-08-13T02:37:39+08:00
  - Output evidence: sha256:3f69884b99d74a8767cc41fbfe77e724f8861a20ea08d698bd1f49373ca19041 (280 characters captured; content not persisted; last=OK)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `docs/specs/native-context-bridge.md` and `docs/ai/context-packs/native-context-bridge.md`.

Reason: The stable contract now states that command display and verification output use the same structured credential redaction before a Failure Capsule can be published.

## Open questions

None. Arbitrary unlabeled sensitive output remains outside deterministic classification and is handled by never persisting raw logs.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `727b10eec08e544e9272fbc61fd2b8a4f9be2112`
- Current commit: `727b10eec08e544e9272fbc61fd2b8a4f9be2112`
- Changed paths:
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/native-context-bridge.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
