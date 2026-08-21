# Bound context loading and delta validation

Status: completed
Feature: native-context-bridge
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260821154209-gviiisen-25df54aeac
Session ID: 20260821154209-gviiisen-25df54aeac
Actor: gviiisen
Branch: agent/v0.5.9-bounded-context-delta-validation
Started: 2026-08-21T15:42:09+08:00
Completed: 2026-08-21T16:29:34+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: ba915523eb59aa27ad01f9299dca19b0c5bdf723
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/native-context-bridge.md, docs/specs/coverage-integrity.md
Spec exception: none

## Intent

Bound the first repository-context load and make pull-request validation proportional to the current delta, so large production repositories do not force an Agent to read every Markdown record or repair unrelated historical debt. Acceptance requires one deterministic Context Plan with explicit file and character budgets, a stable JSON contract for automation, cold change-history bodies, generated no-broad-read rules, and a changed-scope strict gate that still rejects defects introduced by the current branch.

## Changed behavior

Before: `context --query` ranked a primary Pack and printed linked specifications, but it did not define a hard initial-read budget or a machine-readable plan. Generated Agent rules did not explicitly prohibit recursive ledger-document reads. `check --strict` audited the entire repository, so unrelated pre-existing documentation debt could block a focused pull request.

After: `context --query` emits `context-plan-v1`, selects exactly one current primary Pack, excludes superseded/archived routes, bounds Required reads and characters, derives only limited ID/title/feature/date/summary/evidence metadata from the Manifest, keeps Change bodies cold, and supports terminal-stable JSON with routing metrics. All four generated adapters enforce the same Required-read boundary. `check --strict --changed-since <base>` validates the merge-base delta plus directly related current Packs/specs; optional Coverage accepts private evidence or spec exceptions only from sessions that intersect the changed implementation paths, while the existing full-repository strict audit remains unchanged.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::context_search` | Builds the repository context response. | Replaced the unbounded text listing with a budgeted Context Plan and deterministic text/JSON renderers. |
| `skills/repo-context-ledger/scripts/ledger.py::manifest_change_summaries` | Supplies recent history metadata without reading Change bodies. | Added bounded, feature-filtered manifest summaries for the selected Pack. |
| `skills/repo-context-ledger/scripts/ledger.py::completed_change_manifest_entry` | Produces cold, auditable history metadata. | Added stable IDs, feature/date/summary fields, and repository-relative evidence paths without making Change bodies required reads. |
| `skills/repo-context-ledger/scripts/ledger.py::check_changed_repo` | Enforces the pull-request delta gate. | Added merge-base-aware structural, related Pack/spec, adapter, manifest, and optional Coverage validation. |
| `skills/repo-context-ledger/scripts/ledger.py::relevant_private_handoff_texts` | Selects private evidence eligible for integration Coverage. | Prevents an unrelated session's evidence or spec exception from satisfying the current implementation delta. |
| `skills/repo-context-ledger/scripts/ledger.py::context_plan_policy` | Generates cross-Agent repository instructions. | Gives AGENTS, Claude, Cursor, and Copilot one Required-read, cold-Change, no-recursive-read policy. |
| `tests/test_ledger.py::LedgerFlowTests` | Covers public CLI and generated adapter behavior. | Added red/green coverage for budgets, JSON, cold history, stable terminal transport, 1,000 Changes, 100 Packs, private-session relevance, and delta-validation isolation. |
| `skills/repo-context-ledger/references/production-workflow.md` | Documents the production operating model. | Defines bounded initial loading, cold history, PR delta gates, and scheduled full audits. |

## Boundaries and risks

- Invariant: Context Packs remain the routing source, stable specs remain current truth, Changes remain completed evidence, and full `check --strict` behavior remains available and unchanged.
- Failure / recovery: Invalid budgets, an oversized primary Pack, no eligible current Pack, an invalid base reference, new broken links, or a source change that makes a directly related Pack stale fail with explicit diagnostics. The user can correct configuration, documentation, or the base reference and rerun the same deterministic command.
- Not changed: This version adds no LLM gate, vector database, daemon, private cache, code locking, worktree orchestration, fourth documentation layer, or automatic derived-index update on a feature branch. Cache and baseline work remains deferred to v0.6.0.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 1.12s
  - Recorded: 2026-08-21T15:42:48+08:00
  - Output evidence: sha256:cebacd46a3a0fd2f41645fd0e7008057c68c3af01b6d166a7f88f66511cd9441 (1100 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("Context plan: context-plan-v1", result.stdout) | AssertionError: 'Context plan: context-plan-v1' not found in 'Primary pack: docs/ai/context-packs/bounded-router.md\nFeature: bounded-router\nTitle: Bounded Router\nStatus: current\nWhy: feature=bounded-router, title, tracked=src/router.py\nScore: 23260\nFingerprints: current\nStable specs:\n- docs/specs/router-1.md\n- docs/specs/router-2.md\n- docs/specs/router-3.md\n- docs/specs/router-4.md\n' | FAILED (failures=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 1.24s
  - Recorded: 2026-08-21T15:44:00+08:00
  - Output evidence: sha256:321dcc8647351b20ebda41e78b641d3c62d9bdb02937bd9a2389a0ccff6f05f2 (214 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 1.30s
  - Recorded: 2026-08-21T15:44:34+08:00
  - Output evidence: sha256:0ccfac374f25b3e81ec56508d024d046c37d7f3fd3f47080ec87bf6b0f179bfb (1205 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.fail( | AssertionError: command returned 2, expected 0 | ledger.py: error: unrecognized arguments: --format json | FAILED (failures=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 1.06s
  - Recorded: 2026-08-21T15:45:37+08:00
  - Output evidence: sha256:8d519f44e76e6f703f9224177fd68d33f554e8025b9b2f16eea8c8585bc2f5ea (248 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 0.59s
  - Recorded: 2026-08-21T15:46:11+08:00
  - Output evidence: sha256:c367be983c241204692d6592a34c95cf07a36d6b0a2c5d24498922fd351b5af0 (3869 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("Read only the Context Plan's Required reads initially", agents_text) | AssertionError: "Read only the Context Plan's Required reads initially" not found in '# Agent instructions\n\n<!-- repo-context-ledger:rules:start -->\n## Repository context ledger\n\nFor every feature, bug fix, refactor, interface change, or other behavior-changing code task:\n\n1. Before editing code, run `status`, then start or reuse only this task\'s private draft session. Keep the returned session ID and pass `--session <id>` whenever multiple sessions exist.\n2. Resolve `quality.language`; when it is `auto`, follow nea…)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 1.19s
  - Recorded: 2026-08-21T15:46:40+08:00
  - Output evidence: sha256:226d92564af8b5d593da813553759cf9bd6b7294043333346666d20c9acf1014 (256 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 1.75s
  - Recorded: 2026-08-21T15:47:22+08:00
  - Output evidence: sha256:a69ec6073537dbbb6df92db7774ab865b0b20ca2cec2971e6e4ea26b8c38e8cf (1387 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.fail( | AssertionError: command returned 2, expected 0 | ledger.py: error: unrecognized arguments: --changed-since <redacted-token> | FAILED (failures=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 2.17s
  - Recorded: 2026-08-21T15:49:12+08:00
  - Output evidence: sha256:af54ba8e327eae86b942c41fa7ccb0d04fe23584de2ee1b88635db6aabfddfe9 (262 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 1.44s
  - Recorded: 2026-08-21T15:49:41+08:00
  - Output evidence: sha256:deb9f6c515e50b073cc8d03c007a4ef1f875f78702cb0093656c17564208ebc6 (841 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... ERROR | ERROR: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertEqual(1, plan["metrics"]["packs_considered"]) | KeyError: 'metrics' | FAILED (errors=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 1.42s
  - Recorded: 2026-08-21T15:49:58+08:00
  - Output evidence: sha256:fe33569d75183825d4c2747e0d56ea89a7b8edfa51ef8e7fc32390f4f095540f (248 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 1.16s
  - Recorded: 2026-08-21T15:50:49+08:00
  - Output evidence: sha256:83bd65e926c01c7af9bd4b7d6692c7a9af55184a54dd57b275a4f2f59a8aca47 (1223 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertEqual( | AssertionError: Lists differ: [{'path': 'docs/changes/2026/08/20260801-r[75 chars]ed'}] != [] | FAILED (failures=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 1.12s
  - Recorded: 2026-08-21T15:51:29+08:00
  - Output evidence: sha256:ec52f9b79d660903e4d66630bc332c7915c8d4402c754c8b2553c0812469ea9c (272 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 4.01s
  - Recorded: 2026-08-21T15:51:59+08:00
  - Output evidence: sha256:be710fb87db762003f48704b7cf383b0b4f275176848204dba4bbea3ad1c315c (402 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 1.97s
  - Recorded: 2026-08-21T15:52:23+08:00
  - Output evidence: sha256:8bb55d337b5bb4acea546a4b04086176c09e757a2ed6c89f955a1642ca963001 (258 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k "context or changed_scope or native_adapters" -v`
  - Status: failed
  - Exit code: 5
  - Duration: 0.12s
  - Recorded: 2026-08-21T15:52:48+08:00
  - Output evidence: sha256:e70fec2825d9bf206d27463a792768195039599cb39bcca66339f47283f84cce (108 characters captured; content not persisted; failure=---------------------------------------------------------------------- | Ran 0 tests in 0.000s | NO TESTS RAN)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k context -k changed_scope -k native_adapters -v`
  - Status: passed
  - Exit code: 0
  - Duration: 41.00s
  - Recorded: 2026-08-21T15:53:36+08:00
  - Output evidence: sha256:5c650b7a857a9cdf44aae4fc5c5c36ba946f2c30f564e29defd56f8397d358f0 (2965 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 1.14s
  - Recorded: 2026-08-21T15:58:45+08:00
  - Output evidence: sha256:5e4c7023c5c82497c84bc2d2fe06d219be91dee363b816fb058b5c662ebfb9aa (1419 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertEqual( | AssertionError: Lists differ: [{'pa[35 chars]-router.md', 'title': '�޸���ʷ·��', 'status': 'completed'}] != [{'pa[35 chars]-router.md', 'title': '\ufffd\u07b8\ufffd\ufffd\ufffd\u02b7��\ufffd\ufffd', 'status': 'completed'}] | FAILED (failures=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token> -v`
  - Status: passed
  - Exit code: 0
  - Duration: 1.19s
  - Recorded: 2026-08-21T15:59:04+08:00
  - Output evidence: sha256:54e8c4b6780e30ac45e5f56936838b0d5964b7e38489a7fd443c5d4a4052460f (272 characters captured; content not persisted; last=OK)
- Command: `python -m py_compile skills/repo-context-ledger/scripts/ledger.py .context-ledger/ledger.py`
  - Status: passed
  - Exit code: 0
  - Duration: 0.17s
  - Recorded: 2026-08-21T15:59:41+08:00
  - Output evidence: No output.
- Command: `python -m unittest discover -s tests -p test_ledger.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 119.64s
  - Recorded: 2026-08-21T16:01:45+08:00
  - Output evidence: sha256:4b713c8c473d87296de137000cb6dca87acc0aef6e81dfd827a20352908edf86 (9766 characters captured; content not persisted; last=OK)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-21T16:02:10+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python -c "from pathlib import Path; a=Path('skills/repo-context-ledger/scripts/ledger.py').read_bytes(); b=Path('.context-ledger/ledger.py').read_bytes(); assert a == b, 'runtime copies differ'; print('runtime copies are byte-identical')"`
  - Status: passed
  - Exit code: 0
  - Duration: 0.05s
  - Recorded: 2026-08-21T16:02:17+08:00
  - Output evidence: sha256:51749a648483195fa9ba5a259f6d415b00db4b67d395bae51940bb7692e268cd (34 characters captured; content not persisted; last=runtime copies are byte-identical)
- Command: `python .context-ledger/ledger.py adapters check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.12s
  - Recorded: 2026-08-21T16:02:22+08:00
  - Output evidence: sha256:9eab9a5a937791f0f7f83f779889ec7ce552e860d827df0cf9411b8db2d296ac (163 characters captured; content not persisted; last=copilot: current (.github/copilot-instructions.md))
- Command: `python .context-ledger/ledger.py check --strict --changed-since main`
  - Status: failed
  - Exit code: 2
  - Duration: 0.88s
  - Recorded: 2026-08-21T16:02:30+08:00
  - Output evidence: sha256:5a3cd957bd2e45c4e6de59a26a048346fa5dca0f5d18fb09ccc2b206914cd6f5 (191 characters captured; content not persisted; failure=ERROR: Broken link in skills/repo-context-ledger/SKILL.md: .context-ledger/writing-quality.md)
- Command: `python .context-ledger/ledger.py check --strict --changed-since main`
  - Status: passed
  - Exit code: 0
  - Duration: 0.86s
  - Recorded: 2026-08-21T16:02:58+08:00
  - Output evidence: sha256:1663994c02f4bda69461be9adf187a2013f3fb39c1ca90cc4b93bd601bf984ac (144 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since main`
  - Status: failed
  - Exit code: 2
  - Duration: 1.22s
  - Recorded: 2026-08-21T16:03:25+08:00
  - Output evidence: sha256:0747f05d7aabb7203f9b9cade99289efa61a6540b107d541ecab5b22198dc411 (418 characters captured; content not persisted; failure=ERROR: Related Context Pack was not changed for behavior-changing path skills/repo-context-ledger/SKILL.md: docs/ai/context-packs/task-session-integrity.md | ERROR: Related Context Pack was not changed for behavior-changing path skills/repo-context-ledger/scripts/ledger.py: docs/ai/context-packs/task-session-integrity.md)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since main`
  - Status: failed
  - Exit code: 2
  - Duration: 1.17s
  - Recorded: 2026-08-21T16:05:06+08:00
  - Output evidence: sha256:0747f05d7aabb7203f9b9cade99289efa61a6540b107d541ecab5b22198dc411 (418 characters captured; content not persisted; failure=ERROR: Related Context Pack was not changed for behavior-changing path skills/repo-context-ledger/SKILL.md: docs/ai/context-packs/task-session-integrity.md | ERROR: Related Context Pack was not changed for behavior-changing path skills/repo-context-ledger/scripts/ledger.py: docs/ai/context-packs/task-session-integrity.md)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since main`
  - Status: passed
  - Exit code: 0
  - Duration: 1.41s
  - Recorded: 2026-08-21T16:05:33+08:00
  - Output evidence: sha256:d899bd44fe8b87697cf0150cf683589861dcc4a0f855230f327e33c4961b3d98 (144 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
- Command: `python .context-ledger/ledger.py context --query "native context bridge" --format json`
  - Status: passed
  - Exit code: 0
  - Duration: 0.89s
  - Recorded: 2026-08-21T16:09:01+08:00
  - Output evidence: sha256:5f5b6599e6ad6e5a2dba059f98146954d01d861eebb1a22b3f1b947bf8316f91 (1804 characters captured; content not persisted; last=})
- Command: `python -m unittest discover -s tests -p test_ledger.py -k native_adapters -k ignores_spec_exception -k uses_change_metadata -k one_hundred -k never_selects -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 13.66s
  - Recorded: 2026-08-21T16:17:35+08:00
  - Output evidence: sha256:923b41ee1780514d9e6963fd4afe885069e6ad63b8910506be71119181b271e0 (9051 characters captured; content not persisted; failure=self.fail( | AssertionError: command returned 2, expected 0 | ERROR: Multiple task sessions exist; pass --path for only this task when capturing session 20260821161734-alice-10bcd58207. | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn(phrase, adapter_text, f"{phrase!r} missing from {adapter_path}") | AssertionError: 'Do not open completed Change bodies unless' not found in '# Agent instructions\n\n<!-- repo-context-ledger:rules:start -->\n## Repository context ledger\n\nFor every feature, bug fix, refactor, interface change, or other behavior-changing code task:\n\n1. Before editing code, run `status`, then start or reuse only this task\'s private draft session. Keep the returned session ID and pass `--session <id>…)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k native_adapters -k ignores_spec_exception -k uses_change_metadata -k one_hundred -k never_selects -k <redacted-token> -v`
  - Status: failed
  - Exit code: 1
  - Duration: 15.31s
  - Recorded: 2026-08-21T16:22:06+08:00
  - Output evidence: sha256:8d10a108f187444065a709c0f52c0b30417a69a3b227ada287dd2034c1678705 (3153 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("\\u4fee\\u590d", result.stdout) | AssertionError: '\\u4fee\\u590d' not found in '{\n  "schema": "context-plan-v1",\n  "query": "bounded router",\n  "confidence": "high",\n  "primary_pack": "docs/ai/context-packs/bounded-router.md",\n  "feature": "bounded-router",\n  "title": "Bounded Router",\n  "status": "current",\n  "selection": {\n    "score": 23260,\n    "reasons": [\n      "feature=bounded-router",\n      "title",\n      "tracked=src/router.py"\n    ],\n    "fingerprints": "current"\n  },\n  "required_reads": [\n    {\n      "kind": "pack",\n      "path": "docs/ai/context-packs/bounded-ro…)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k uses_change_metadata -v`
  - Status: passed
  - Exit code: 0
  - Duration: 1.14s
  - Recorded: 2026-08-21T16:22:20+08:00
  - Output evidence: sha256:3982721c32459a2a8d834cf955556579cdfedaf5e9b1c448cb1505e771c8507e (272 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k context -k coverage -k manifest -k native_adapters -v`
  - Status: passed
  - Exit code: 0
  - Duration: 46.38s
  - Recorded: 2026-08-21T16:25:11+08:00
  - Output evidence: sha256:8252e2ebbc2d5674f921fcea3edeb9282ece08ab6fa8fc7e04d992862da67f9d (3462 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -p test_ledger.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 128.92s
  - Recorded: 2026-08-21T16:27:50+08:00
  - Output evidence: sha256:ff6825cb0325986170f43d14c83dda3b779cf8cd12856b79895b1537508ccb22 (10301 characters captured; content not persisted; last=OK)
- Command: `python -m py_compile skills/repo-context-ledger/scripts/ledger.py .context-ledger/ledger.py`
  - Status: passed
  - Exit code: 0
  - Duration: 0.16s
  - Recorded: 2026-08-21T16:29:04+08:00
  - Output evidence: No output.
- Command: `python -c "from pathlib import Path; a=Path('skills/repo-context-ledger/scripts/ledger.py').read_bytes(); b=Path('.context-ledger/ledger.py').read_bytes(); assert a == b, 'runtime copies differ'; print('runtime copies are byte-identical')"`
  - Status: passed
  - Exit code: 0
  - Duration: 0.03s
  - Recorded: 2026-08-21T16:29:05+08:00
  - Output evidence: sha256:51749a648483195fa9ba5a259f6d415b00db4b67d395bae51940bb7692e268cd (34 characters captured; content not persisted; last=runtime copies are byte-identical)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.09s
  - Recorded: 2026-08-21T16:29:06+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python .context-ledger/ledger.py adapters check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.12s
  - Recorded: 2026-08-21T16:29:07+08:00
  - Output evidence: sha256:9eab9a5a937791f0f7f83f779889ec7ce552e860d827df0cf9411b8db2d296ac (163 characters captured; content not persisted; last=copilot: current (.github/copilot-instructions.md))
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since main`
  - Status: passed
  - Exit code: 0
  - Duration: 2.14s
  - Recorded: 2026-08-21T16:29:10+08:00
  - Output evidence: sha256:c4830195c87117c97c3f57448358b6ab851638fc989d9f2e614c82b08da70cf2 (180 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
- Command: `python .context-ledger/ledger.py team-check --base origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 1.14s
  - Recorded: 2026-08-21T16:29:12+08:00
  - Output evidence: sha256:2ff34c29fbc2fb3c8b92cb62ab52f1ed21b3616d7d010ea4f71fa403b932d066 (207 characters captured; content not persisted; last=Team collaboration check passed.)
- Command: `python .context-ledger/ledger.py check --strict --coverage`
  - Status: passed
  - Exit code: 0
  - Duration: 2.30s
  - Recorded: 2026-08-21T16:29:15+08:00
  - Output evidence: sha256:74952ea792336837ef8400c980dc0f9978862f98d9f3a3af55dc87a68840e681 (34 characters captured; content not persisted; last=Repo Context Ledger check passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/document-model.md`, `skills/repo-context-ledger/references/production-workflow.md`, `docs/specs/native-context-bridge.md`, `docs/specs/coverage-integrity.md`, `docs/ai/context-packs/native-context-bridge.md`, `docs/ai/context-packs/coverage-integrity.md`, and `docs/ai/context-packs/task-session-integrity.md`.

Reason: The public CLI contract, complete cold-history metadata, four-Adapter read boundary, changed-scope related-document/session policy, configuration budgets, stable truth, and affected routing fingerprints all changed and must remain discoverable across Codex, Claude, Cursor, and Copilot.

## Open questions

None. Private caching, stored PR baselines, and Pack ownership/lifecycle policy are deliberately scheduled after measured v0.5.9 adoption rather than treated as unresolved behavior in this release.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `ba915523eb59aa27ad01f9299dca19b0c5bdf723`
- Current commit: `ba915523eb59aa27ad01f9299dca19b0c5bdf723`
- Changed paths:
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/coverage-integrity.md`
  - `docs/specs/native-context-bridge.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/document-model.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
