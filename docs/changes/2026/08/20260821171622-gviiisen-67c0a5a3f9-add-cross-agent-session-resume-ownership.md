# Add cross-Agent session resume ownership

Status: completed
Feature: task-session-integrity
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260821171622-gviiisen-67c0a5a3f9
Session ID: 20260821171622-gviiisen-67c0a5a3f9
Actor: gviiisen
Branch: agent/v0.5.10-cross-agent-resume-ownership
Started: 2026-08-21T17:16:22+08:00
Completed: 2026-08-21T18:06:48+08:00
Paused:
Resumed:
Checkpointed: 2026-08-21T18:04:56+08:00
Checkpoint actor: gviiisen
Base commit: cbdc584220e1f6868be6b20a5125e1b67151cdd3
Dirty paths: .context-ledger/config.json, .context-ledger/ledger.py, .cursor/rules/repo-context-ledger.mdc, .github/copilot-instructions.md, AGENTS.md, CLAUDE.md, README.md, README.zh-CN.md, docs/ai/context-packs/native-context-bridge.md, docs/ai/context-packs/task-session-integrity.md, docs/specs/native-context-bridge.md, docs/specs/task-session-integrity.md, skills/repo-context-ledger/SKILL.md, skills/repo-context-ledger/references/document-model.md, skills/repo-context-ledger/references/production-workflow.md, skills/repo-context-ledger/scripts/ledger.py, tests/test_ledger.py
Resume summary: Implemented v0.5.10 principal-owned cross-Agent keyword resume, bounded Capsules, continuation epochs, explicit grants, progressive code expansion, docs, adapters, and migration.
Next step: Run strict delta and team checks, then publish the validated private handoff without committing.
Specs: docs/specs/task-session-integrity.md, docs/specs/native-context-bridge.md
Spec exception: none

## Intent

Allow a user to leave a long Agent conversation and continue the same unfinished repository task from fresh Codex, Cursor, Claude, Copilot, or Grok context by supplying task keywords. The continuation must be bounded and directional without limiting necessary code investigation, preserve the existing Ledger session, isolate different human principals by default, and keep all existing evidence, finish, Git, and parallel-task semantics intact.

## Changed behavior

Before: `context --query` routed only Git-tracked Pack/spec/history metadata through `context-plan-v1`. Active and paused private sessions had no durable principal owner or Agent tool metadata; `resume` selected paused tasks only and did not invalidate stale writers. A different repository user could not be distinguished from the original user at the Ledger state layer, and there was no explicit bounded read-only, fork, or transfer operation.

After: `context-plan-v2` first filters private task sessions by principal access, routes task keywords to one active/paused match, and generates a maximum 4,000-character Resume Capsule containing the checkpoint, next action, implementation evidence paths, verification, Git position, Pack, warnings, tool, and epoch. `resume --query --tool` continues that same session and rotates an epoch required by later writes. Foreign principals receive only an overlap signal unless the owner creates an expiring read-only, fork, or paused transfer grant. All generated Agent policies define the Capsule and Required reads as an initial route and require expansion through every behavior-relevant code boundary.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::context_search` | Builds the tool-neutral context route consumed by fresh Agent windows. | Emits `context-plan-v2`, integrates the private session route, prioritizes the session's Pack, enforces Capsule size, and states progressive code-expansion rules. |
| `skills/repo-context-ledger/scripts/ledger.py::current_principal`, `route_resume_sessions` | Separates human ownership from Agent tool identity and selects continuation candidates. | Added pseudonymous principals, owner/grant filtering before private draft reads, keyword scoring, ambiguity blocking, and minimal foreign-overlap detection. |
| `skills/repo-context-ledger/scripts/ledger.py::resume_change`, `validate_session_epoch` | Owns continuation and stale-writer protection. | Continues active or paused work in place, rotates tool/epoch metadata, and requires the current epoch on later lifecycle mutations. |
| `skills/repo-context-ledger/scripts/ledger.py::share_session`, `fork_granted_session` | Implements explicit cross-principal handoff. | Added expiring read-only/fork/transfer grants; fork creates a new recipient-owned private child while transfer requires a paused source and changes ownership on acceptance. |
| `.context-ledger/ledger.py` | Provides the installed repository-local runtime used by native Agent adapters. | Synchronized the canonical v0.5.10 runtime and migrated configuration/private state to schema v8. |
| `tests/test_ledger.py` | Exercises runtime, migration, Agent adapters, evidence, and publication behavior. | Added same-principal cross-tool resume, bounded Capsule, stale epoch, foreign non-read/non-write, grant expiry/fork/transfer, empty LF/CRLF metadata, and v8 migration coverage. |

## Boundaries and risks

- Invariant: Resume guidance is not a completeness claim. Agents read only the bounded route initially, then must expand through callers, implementations, configuration, persistence, permissions, concurrency, retries, tests, and external APIs whenever those boundaries can affect behavior. Unfinished drafts remain private and only validated `finish` publishes history.
- Failure / recovery: Ambiguous matches, stale epochs, expired grants, foreign access, missing summaries, missing Packs, moved Git state, and stale fingerprints fail closed or return guided warnings without mutating the source session. A fork leaves the source draft byte-identical; a transfer cannot be granted until the source is paused. Existing drafts migrate conservatively only when their Actor matches the current Git actor.
- Not changed: Principal checks are logical workflow isolation rather than a filesystem security sandbox. Private state still does not travel through Git or another clone. The Ledger still does not copy, lock, merge, or coordinate source-code edits, and existing evidence, Coverage, PR delta, team-check, verification redaction, and atomic finish behavior remain in force.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_ledger.py`
  - Status: failed
  - Exit code: 1
  - Duration: 125.01s
  - Recorded: 2026-08-21T17:28:00+08:00
  - Output evidence: sha256:d030c54e6073583a46c1dffeb6c467174be1404e8373075a090ca51eca444891 (6471 characters captured; content not persisted; failure=Traceback (most recent call last): | self.assertIn("Multiple paused task sessions exist", ambiguous.stderr) | AssertionError: 'Multiple paused task sessions exist' not found in 'ERROR: Multiple resumable task sessions exist (<redacted-token>, <redacted-token>); rerun with --session <id>.\n' | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("MIGRATE configuration schema v2 to v7", preview.stdout) | AssertionError: 'MIGRATE configuration schema v2 to v7' not found in 'Repo Context Ledger init plan for <TEMP_DIR>\\tmpnhed5e84\\repo\nUPDATE .context-ledger/config.json [configuration]\nDELETE .context-ledger/context-state.json [legacy workspace state]\nCREATE .git/repo-context-ledger/states/main-b28b7af6/context-state.js…)
- Command: `python -m unittest tests.test_ledger.LedgerFlowTests.<redacted-token> tests.test_ledger.LedgerFlowTests.<redacted-token> tests.test_ledger.LedgerFlowTests.<redacted-token>`
  - Status: failed
  - Exit code: 1
  - Duration: 0.08s
  - Recorded: 2026-08-21T17:29:39+08:00
  - Output evidence: sha256:d9b65719ab953f808c4bfce057eb9abc16e904e26bacc57eb61ba8855670226c (1775 characters captured; content not persisted; failure=ImportError: Failed to import test module: test_ledger | Traceback (most recent call last): | ModuleNotFoundError: No module named 'tests.test_ledger' | ERROR: test_ledger (unittest.loader._FailedTest.test_ledger) | ImportError: Failed to import test module: test_ledger | Traceback (most recent call last): | ModuleNotFoundError: No module named 'tests.test_ledger' | FAILED (errors=3))
- Command: `python tests/test_ledger.py LedgerFlowTests.<redacted-token> LedgerFlowTests.<redacted-token> LedgerFlowTests.<redacted-token>`
  - Status: failed
  - Exit code: 1
  - Duration: 14.28s
  - Recorded: 2026-08-21T17:30:06+08:00
  - Output evidence: sha256:ecb5ad342656d1cc94f650fd0eef03bf5568b57edf6e9b4faec0aefca8769aba (1106 characters captured; content not persisted; failure=FAIL: <redacted-token> (__main__.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertEqual(["src/service.py"], capsule["evidence_paths"]) | AssertionError: Lists differ: ['src/service.py'] != ['docs/ai/context-manifest.json', 'docs/ai/[55 chars].py'] | FAILED (failures=1))
- Command: `python tests/test_ledger.py LedgerFlowTests.<redacted-token>`
  - Status: passed
  - Exit code: 0
  - Duration: 6.17s
  - Recorded: 2026-08-21T17:30:28+08:00
  - Output evidence: sha256:d58749ceb8e468421cb4627a0cd061aeeb95ceb0bc6f4fd277cc0ea6a11a0b61 (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k explicit_session_grants`
  - Status: passed
  - Exit code: 0
  - Duration: 10.33s
  - Recorded: 2026-08-21T17:36:41+08:00
  - Output evidence: sha256:aeb354bb1de88a62e6ff2153862bd2b9f718f1b2b3b14953b18eb2e18413d9a8 (99 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k "owned_session_routes or foreign_principal or resume_query_fails"`
  - Status: failed
  - Exit code: 5
  - Duration: 0.14s
  - Recorded: 2026-08-21T17:36:49+08:00
  - Output evidence: sha256:e70fec2825d9bf206d27463a792768195039599cb39bcca66339f47283f84cce (108 characters captured; content not persisted; failure=---------------------------------------------------------------------- | Ran 0 tests in 0.000s | NO TESTS RAN)
- Command: `python -m unittest discover -s tests -p test_ledger.py`
  - Status: failed
  - Exit code: 1
  - Duration: 179.58s
  - Recorded: 2026-08-21T17:39:57+08:00
  - Output evidence: sha256:38a2142f2cabef470b93e38fb3a6660a8a0d3d833cca3c417f3b42e5feb66bf7 (6357 characters captured; content not persisted; failure=self.fail( | AssertionError: command returned 2, expected 0 | ERROR: Task session <redacted-token> was continued in another Agent window; rerun with --epoch 2. | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertEqual(7, json.loads(config_path.read_text(encoding="utf-8"))["schema_version"]) | AssertionError: 7 != 8 | FAILED (failures=3))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k native_adapters`
  - Status: passed
  - Exit code: 0
  - Duration: 1.28s
  - Recorded: 2026-08-21T17:40:21+08:00
  - Output evidence: sha256:e42dc0901d9d0c9a86a0c9fe52038eb0f857ea357e999efca048e5b6ad5aab1f (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k pause_stack`
  - Status: passed
  - Exit code: 0
  - Duration: 3.58s
  - Recorded: 2026-08-21T17:40:31+08:00
  - Output evidence: sha256:a47b3754abb8f20ffc6a2cc7d7025745c982671f195322f9b570959c5bc04623 (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k v2_git_state`
  - Status: passed
  - Exit code: 0
  - Duration: 4.77s
  - Recorded: 2026-08-21T17:40:40+08:00
  - Output evidence: sha256:72e29aa1e8abb31cf40d8e06663770558487fcf871bf94f0dfb45a48b4efdc17 (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k foreign_principal`
  - Status: passed
  - Exit code: 0
  - Duration: 4.77s
  - Recorded: 2026-08-21T17:47:16+08:00
  - Output evidence: sha256:63d56143dbb4d50b711d1a6c8d8f1b0e4a2a64133a5ffd832e729660bf43f881 (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k explicit_session_grants`
  - Status: passed
  - Exit code: 0
  - Duration: 9.58s
  - Recorded: 2026-08-21T17:47:30+08:00
  - Output evidence: sha256:22337f9299a01093f4912d95f2e0c1d30023d0197b06d957188cff49c71ec337 (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k empty_metadata_field`
  - Status: passed
  - Exit code: 0
  - Duration: 0.23s
  - Recorded: 2026-08-21T17:51:02+08:00
  - Output evidence: sha256:fb184ea57734512b1f088f9181209901b9cd46df3eb7eaa2500ea9e48dde20b5 (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k owned_session_routes`
  - Status: passed
  - Exit code: 0
  - Duration: 6.08s
  - Recorded: 2026-08-21T17:52:25+08:00
  - Output evidence: sha256:e1accb27049ed1357b4ed0914db266b2c0c6f0dade651785c796cebcdfa28bac (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k uncheckpointed`
  - Status: passed
  - Exit code: 0
  - Duration: 2.58s
  - Recorded: 2026-08-21T17:54:45+08:00
  - Output evidence: sha256:6701711ba5138ff9222695c8005b02b63a11d02f059a1d035e00a9b0114c0cf8 (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k explicit_session_grants`
  - Status: passed
  - Exit code: 0
  - Duration: 10.83s
  - Recorded: 2026-08-21T17:55:00+08:00
  - Output evidence: sha256:5f745c2a1e98e69b12d4d115ab2bda5a4dc98584e726f51959d584eab6f8342e (99 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py`
  - Status: failed
  - Exit code: 1
  - Duration: 163.61s
  - Recorded: 2026-08-21T17:58:10+08:00
  - Output evidence: sha256:e451aa5edc4e747a86a7e38b0ef73e8104d8e5dd5221d8a1571cd58a071d3fbd (954 characters captured; content not persisted; failure=...................................................Injected post-publication failure. | Published record validation failed; the private draft and session were preserved for recovery. | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertEqual(LEDGER_MODULE.current_principal(repo), sessions[0]["owner_principal"]) | AssertionError: 'p-540a547d5be9d8e6' != '' | FAILED (failures=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k active_pointer_migrate`
  - Status: passed
  - Exit code: 0
  - Duration: 4.72s
  - Recorded: 2026-08-21T17:59:08+08:00
  - Output evidence: sha256:268e3bbc6a5a0d241691abeed8b6d7e315cc392a81259e60d2ed49deca6e700f (98 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py`
  - Status: passed
  - Exit code: 0
  - Duration: 173.70s
  - Recorded: 2026-08-21T18:03:54+08:00
  - Output evidence: sha256:3f34c415479e69c9c242cc1923818f7da73665a82aab49821bfe16dead2c3d74 (303 characters captured; content not persisted; last=OK)
- Command: `python .context-ledger/ledger.py --repo . team-check --base origin/main`
  - Status: failed
  - Exit code: 2
  - Duration: 1.28s
  - Recorded: 2026-08-21T18:05:13+08:00
  - Output evidence: sha256:79d954c988a0f2b6147df7cee1f912c7e2201860defdd42b024a9105485b734c (432 characters captured; content not persisted; failure=ERROR: docs/ai/context-packs/coverage-integrity.md: Context pack is stale; tracked file changed: skills/repo-context-ledger/scripts/ledger.py | ERROR: docs/ai/context-packs/coverage-integrity.md: Context pack is stale; tracked file changed: tests/test_ledger.py)
- Command: `python .context-ledger/ledger.py --repo . team-check --base origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 1.14s
  - Recorded: 2026-08-21T18:05:38+08:00
  - Output evidence: sha256:3566713ed43d6045a7ffe2e3cd5370bd7a0e4e660c024d1bc718d4235d65a291 (204 characters captured; content not persisted; last=Team collaboration check passed.)
- Command: `python .context-ledger/ledger.py --repo . check --strict --coverage --changed-since origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 2.24s
  - Recorded: 2026-08-21T18:05:46+08:00
  - Output evidence: sha256:9d6c0a7559012e49839dcfae5833ec1f438d11d99bf924fa3733e5282f5b46e4 (187 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: failed
  - Exit code: 1
  - Duration: 0.11s
  - Recorded: 2026-08-21T18:06:02+08:00
  - Output evidence: sha256:cfeb92fd8993d65b56191fbfa8908d6582d2edc481a6b12f7f7e524ed6275336 (694 characters captured; content not persisted; failure=Traceback (most recent call last): | UnicodeDecodeError: 'gbk' codec can't decode byte 0x92 in position 2036: illegal multibyte sequence)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.05s
  - Recorded: 2026-08-21T18:06:09+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/document-model.md`, `skills/repo-context-ledger/references/production-workflow.md`, `docs/specs/task-session-integrity.md`, `docs/specs/native-context-bridge.md`, `docs/ai/context-packs/task-session-integrity.md`, `docs/ai/context-packs/native-context-bridge.md`, `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/repo-context-ledger.mdc`, and `.github/copilot-instructions.md`.

Reason: The behavior changes the cross-Agent continuation contract, private task ownership model, CLI lifecycle requirements, native Agent instructions, migration schema, and user-facing workflow in both supported README languages.

## Open questions

None. Operating-system accounts and repository permissions remain the real confidentiality boundary and are documented as such.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `cbdc584220e1f6868be6b20a5125e1b67151cdd3`
- Current commit: `cbdc584220e1f6868be6b20a5125e1b67151cdd3`
- Changed paths:
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/native-context-bridge.md`
  - `docs/specs/task-session-integrity.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/document-model.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
