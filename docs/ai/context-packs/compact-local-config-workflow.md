# Compact Local Configuration Workflow context pack

Status: current
Feature: compact-local-config-workflow
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 44630d3805a54ae02184131497c715d64fa88e5a
Base branch: main
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Last refreshed: 2026-09-08T00:14:56+08:00

## Purpose

Routes small, worktree-local configuration changes through a compact Ledger lifecycle. It keeps the same evidence and verification trust boundary as ordinary changes while preventing sensitive commands or output from entering Git-tracked records.

Also routes known low-risk repository small fixes: one request stays in one session, nine prompts preserve change explanations and documentation rationale while removing repetitive table authoring, and optional finish preview reports resolvable blockers without writes. Meaningful findings stay in the same private draft throughout the request. The local-config sensitive path remains distinct.

## Load order

- Read first: `src/repo_context_ledger/runtime.py.tmpl` lifecycle parser, verification, evidence, and finish functions.
- Read if needed: `skills/repo-context-ledger/SKILL.md` and `tests/test_ledger.py` when the Agent workflow or CLI contract changes.
- Do not load by default: Context routing, Pack lifecycle governance, derived README generation, and unrelated completed Change bodies.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::record_verification` | Executes a verification outside the state lock and controls what is persisted. |
| `src/repo_context_ledger/runtime.py.tmpl::finish_change` | Collects scoped evidence in memory, validates outside the write lock, then rechecks bounded inputs before short atomic publication. |
| `src/repo_context_ledger/runtime.py.tmpl::complete_small_fix_draft` | Generates only the documentation Updated list and retains change explanations, rationale, and decisions. |
| `src/repo_context_ledger/runtime.py.tmpl::small_fix_explanation_errors` | Checks new short-form path references and rejects path-only explanations; it cannot prove business semantics. |
| `src/repo_context_ledger/runtime.py.tmpl::labeled_value` | Prevents blank inline values from borrowing the following line, including CRLF records. |
| `tests/test_small_fix_closeout.py` | Covers short-form publication, missing explanations, blank fields, legacy compatibility, decision preservation across resume, preview immutability, reference semantics, and session isolation. |
| `src/repo_context_ledger/runtime.py.tmpl::managed_rules` | Generates the shortest-path policy used by native Agent adapters. |
| `skills/repo-context-ledger/SKILL.md` | Defines when a local configuration task can skip broad context routing and manual handoff editing. |

## Contracts and boundaries

- Invariants and contracts: Sensitive verification still executes and records status, exit code, and duration, but persists neither the command arguments nor captured output. Evidence remains limited to explicit Git-changed paths, and completed records identify worktree-local scope without claiming portable repository behavior.
- Failure / recovery: A failed sensitive check preserves the private draft with a sanitized result. `finish` must report the exact missing semantic fields or evidence instead of requiring blind retries; concurrent changes to its draft or bounded inputs preserve the session and require a fresh retry.
- Non-goals: The workflow does not commit secrets, manage `.env` values, replace Git source isolation, infer business behavior from local configuration, or weaken ordinary medium/large change gates.

Reading references added via `pack --reference` are optional navigation, never an escape from dependency review or Coverage. Keep real behavioral dependencies fingerprinted. Preview cannot guarantee a future finish if inputs change; scoped evidence and epoch revalidation still apply.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py` for public CLI lifecycle, sensitive persistence, explicit finish evidence, adapter text, and diagnostic coverage. Run `python scripts/build_runtime.py --check` to prove generated runtimes match the canonical source.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Compact local configuration workflow](../../specs/compact-local-config-workflow.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:c01e9bee65a2e168ee22d0a8e1fe5b1b7686f61c7cd4320d17cbfb25f1c6ccf4`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:1d78f4e2545641efce1a3ef6db9948769ec39cfd530d795a4727a3c7214dcd7f`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:12ae39362268ec7c1c2e27d4a4d73ee1ffd0beecc1509f7b3d7f234db412463e`
- `skills/repo-context-ledger/SKILL.md` — `sha256:5ded6a55fcd32c9cd6ae07eef809b7c33a9c158fdc13a26b70752eb3288a3e69`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:e9b3f1fbf7b1e5f25486f17d1d4fb6756f7b90d408c108be514c1b5c882cc6e7`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:dd1e26e29993ac93d5f52de315df130b270982125b4037dc01c17d9cb63f9a52`
- `tests/test_ledger.py` — `sha256:8f5041ab68473240b1e6cf571c3fe31df732a09110ccd48475a9236ca1cd3f70`
- `tests/test_doctor.py` — `sha256:84526dcc76e8bc08fcc4888763426729c8e73db4c6c70242abeecd763fcad8bd`
- `benchmarks/closeout_workflow_benchmark.py` — `sha256:22d6b75799ca24e8b3289a0c77caa312acac8763b511550722b7ce23d1a396be`
- `benchmarks/README.md` — `sha256:7646ec968c4a325196bac99b26ce855f6ad46ad1993d82a7ffe0b67862cf7ae2`
- `tests/test_small_fix_closeout.py` — `sha256:16fa4f5ad1265aae066c801411ed9e293606833b1e202436b1e35537078b8f9b`
- `benchmarks/small_fix_authoring_benchmark.py` — `sha256:f12065d57870fe140c8480a7d6efaab3ea60590a52b0c7c624caf7795c838679`
- `skills/repo-context-ledger/references/writing-quality.md` — `sha256:1583f96c127ea3dba2a83885dc4160172e01295c4b0c56d6781a6e31d449db60`
<!-- repo-context-ledger:pack-files:end -->
