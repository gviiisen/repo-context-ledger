# Build deterministic standalone runtime architecture

Status: completed
Feature: runtime-architecture
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260821233623-gviiisen-a1d83814d8
Session ID: 20260821233623-gviiisen-a1d83814d8
Actor: gviiisen
Branch: feat/v0.7.0-runtime-architecture
Started: 2026-08-21T23:36:23+08:00
Completed: 2026-08-21T23:45:42+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 6bdf90c56b59fde8890632b113bd61ccb9239c73
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/runtime-architecture.md
Spec exception: none

## Intent

Replace hand-maintained duplicate runtimes with one deterministic build source before gradual modular extraction. Acceptance requires byte-identical standalone outputs, non-writing drift detection, atomic generation, CI enforcement, focused architecture tests, and unchanged installed-runtime/CLI behavior.

## Changed behavior

Before: one logical runtime change had to be repeated manually in `.context-ledger/ledger.py` and the Skill runtime, creating silent drift risk and making safe source modularization impossible.

After: one template plus a contracts fragment generates both standalone files deterministically; version/schema/exit/error and typed result contracts are extracted first, CI rejects drift, and `init` still distributes one zero-dependency runtime.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl` | Owns the executable body. | Became the canonical source with one explicit contracts marker. |
| `src/repo_context_ledger/contracts.pyfrag` | Owns low-coupling runtime contracts. | Extracted version/schema/exit constants, `LedgerError`, and importlib-safe typed `CommandResult`. |
| `scripts/build_runtime.py::render_runtime` | Owns deterministic generation. | Added UTF-8/LF normalization, exact marker replacement, atomic writes, explicit outputs, and non-writing drift checks. |
| `tests/test_runtime_build.py` | Protects distribution architecture. | Added byte identity, compilation, standalone version, and drift-without-write tests. |

## Boundaries and risks

- Invariant: generated outputs remain byte-identical standalone Python with no timestamp/absolute build path, use only Python 3.10+ standard library, and preserve v0.6.2 CLI/JSON/exit and state migration contracts.
- Failure / recovery: invalid UTF-8 source, missing/duplicate marker, or stale output returns 2; repair source and rebuild atomically instead of editing either output. The initial dataclass model was replaced after importlib regression evidence with an explicit typed class.
- Not changed: `init` distribution, repository schema v8, Pack/spec/Change layers, router/Doctor/lifecycle semantics, native adapters, and vendor Memory boundaries remain unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_runtime_build.py`
  - Status: failed
  - Exit code: 1
  - Duration: 0.17s
  - Recorded: 2026-08-21T23:36:49+08:00
  - Output evidence: sha256:398af4d25f2ca7e899c109028d08066811694453871781555fafc49dbc94e359 (2822 characters captured; content not persisted; failure=Traceback (most recent call last): | self.assertEqual(expected, result.returncode, result.stdout + result.stderr) | AssertionError: 0 != 2 : <USER_HOME>\AppData\Local\Programs\Python\Python312\python.exe: can't open file '<REPO_ROOT>\\scripts\\build_runtime.py': [Errno 2] No such file or directory | FAIL: <redacted-token> (test_runtime_build.RuntimeBuildTests.<redacted-token>) | Traceback (most recent call last): | self.assertEqual(expected, result.returncode, result.stdout + result.stderr) | AssertionError: 0 != 2 : <USER_HOME>\AppData\Local\Programs\Python\Python312\python.exe: can't open file '<REPO_ROOT>\\scripts\\build_runtime.py': [Errno 2] No such file or directory | FAILED (failures=3))
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-21T23:40:19+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -m unittest discover -s tests -p test_runtime_build.py`
  - Status: passed
  - Exit code: 0
  - Duration: 0.58s
  - Recorded: 2026-08-21T23:40:20+08:00
  - Output evidence: sha256:d6d5c1f2d40b66b67be7cb04736300754dfeb1b5d195fdef1162baccce8af8ed (101 characters captured; content not persisted; last=OK)
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-21T23:40:51+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python -m unittest discover -s tests -v`
  - Status: failed
  - Exit code: 1
  - Duration: 0.72s
  - Recorded: 2026-08-21T23:40:53+08:00
  - Output evidence: sha256:0a263864147ccc5824a5094d83262ab751433e2c61a2184067275ce64bba909b (6117 characters captured; content not persisted; failure=ImportError: Failed to import test module: test_contract_stability | Traceback (most recent call last): | AttributeError: 'NoneType' object has no attribute '__dict__'. Did you mean: '__dir__'? | ERROR: test_ledger (unittest.loader._FailedTest.test_ledger) | ImportError: Failed to import test module: test_ledger | Traceback (most recent call last): | AttributeError: 'NoneType' object has no attribute '__dict__'. Did you mean: '__dir__'? | FAILED (errors=3))
- Command: `python -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 199.31s
  - Recorded: 2026-08-21T23:45:24+08:00
  - Output evidence: sha256:ca48feb289faa3447e2956b37860f744ab417203401e1ef87b8135faba271890 (14456 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-21T23:45:31+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 2.83s
  - Recorded: 2026-08-21T23:45:35+08:00
  - Output evidence: sha256:2b2bc836d65a344f21b3a1636561a105d4346be652bc498ed4193453c96967b7 (187 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `ARCHITECTURE.md`, `README.md`, `README.zh-CN.md`, `skills/repo-context-ledger/SKILL.md`, `docs/specs/runtime-architecture.md`, and affected Context Packs.

Reason: Establish the canonical/generated boundary, contributor commands, deterministic build guarantees, gradual extraction sequence, failure recovery, and installed-runtime compatibility.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `6bdf90c56b59fde8890632b113bd61ccb9239c73`
- Current commit: `6bdf90c56b59fde8890632b113bd61ccb9239c73`
- Changed paths:
  - `.github/workflows/test.yml`
  - `ARCHITECTURE.md`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/runtime-architecture.md`
  - `scripts/build_runtime.py`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/__init__.py`
  - `src/repo_context_ledger/contracts.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_runtime_build.py`
<!-- repo-context-ledger:evidence:end -->
