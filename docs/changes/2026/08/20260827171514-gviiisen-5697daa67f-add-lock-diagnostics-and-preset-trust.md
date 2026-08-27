# Add lock diagnostics and preset trust

Status: completed
Feature: runtime-architecture
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827171514-gviiisen-5697daa67f
Session ID: 20260827171514-gviiisen-5697daa67f
Actor: gviiisen
Branch: feat/v0.8.2-lock-security-trust
Started: 2026-08-27T17:15:14+08:00
Completed: 2026-08-27T18:30:05+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: a771dbcb55d5d732bc607795ee251cda0ef9e2f1
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/runtime-architecture.md
Spec exception: none

## Intent

Make lock recovery observable without automatic deletion, prevent an exiting writer from deleting another writer's replacement lock, and require explicit principal-local review before Git-tracked verification presets execute. Acceptance requires platform-safe liveness diagnosis, exact digest invalidation, cross-principal isolation, security documentation, and full regression coverage.

## Changed behavior

Before: A write lock recorded only PID/time, failures told users to remove it without diagnosing liveness, and cleanup unlinked the path unconditionally. Any explicitly selected valid preset executed immediately, so a pulled preset change could run before a local trust decision.

After: Locks contain bounded version/PID/time/command/nonce metadata, cleanup verifies file identity plus nonce, and `doctor` classifies live, stale, unknown, invalid, or unsafe locks without deleting them. Verification presets execute only after the current principal trusts their exact normalized SHA-256 digest; every preset change and different principal fails closed first.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::repo_lock` | Serializes short repository writes. | Adds private-mode creation, diagnostic metadata, ownership nonce, fsync, and identity-safe cleanup. |
| `src/repo_context_ledger/runtime.py.tmpl::doctor_lock_findings` | Diagnoses repository write locks read-only. | Adds bounded no-follow parsing and Windows/Unix-safe owner liveness classification. |
| `src/repo_context_ledger/runtime.py.tmpl::require_verification_preset_trust` | Gates preset execution. | Hashes normalized preset data and persists exact per-principal trust outside Git. |
| `tests/test_lock_and_preset_trust.py` | Protects security behavior. | Covers live/stale diagnosis, replacement ownership, initial/changed/foreign preset trust, and non-execution before trust. |

## Boundaries and risks

- Invariant: `doctor` stays read-only; presets never auto-run; direct verification remains compatible; public JSON schema names and repository/private-session schema v8 remain unchanged.
- Failure / recovery: Missing or changed preset trust exits 2 with `PRESET_TRUST_REQUIRED` and the exact expected digest. Lock contention directs users to `doctor`; stale/invalid locks require explicit confirmation and manual removal, while live locks must be left alone.
- Not changed: The runtime does not sandbox trusted project commands, auto-delete locks, encrypt local state, infer semantic preset safety, or coordinate source-code edits.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_lock_and_preset_trust.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 5.39s
  - Recorded: 2026-08-27T18:29:35+08:00
  - Output evidence: sha256:9967acb52fc69f7252ae1aa8942dbe6c8f77d5d1b01ac0fc289788745daebdbf (3962 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-27T18:29:36+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: failed
  - Exit code: 1
  - Duration: 0.12s
  - Recorded: 2026-08-27T18:29:36+08:00
  - Output evidence: sha256:abdc62d1372171445860a137fca3c03ff23520a7a84c7e274ff36091ee6b9bc5 (694 characters captured; content not persisted; failure=Traceback (most recent call last): | UnicodeDecodeError: 'gbk' codec can't decode byte 0x92 in position 2522: illegal multibyte sequence)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-27T18:29:44+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `SECURITY.md`, `THREAT_MODEL.md`, `COMPATIBILITY.md`, `MIGRATIONS.md`, `ARCHITECTURE.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/verification-presets.md`, `docs/specs/runtime-architecture.md`, and `docs/ai/context-packs/runtime-architecture.md`.

Reason: Users and Agents need an explicit review command, safe lock recovery procedure, public threat boundary, compatibility statement, and first-read code route for these security changes.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `a771dbcb55d5d732bc607795ee251cda0ef9e2f1`
- Current commit: `a771dbcb55d5d732bc607795ee251cda0ef9e2f1`
- Changed paths:
  - `SECURITY.md`
  - `THREAT_MODEL.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/specs/runtime-architecture.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/verification-presets.md`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_ledger.py`
  - `tests/test_lock_and_preset_trust.py`
  - `tests/test_runtime_build.py`
<!-- repo-context-ledger:evidence:end -->
