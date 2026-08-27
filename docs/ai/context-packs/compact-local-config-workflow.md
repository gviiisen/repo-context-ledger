# Compact Local Configuration Workflow context pack

Status: current
Feature: compact-local-config-workflow
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Base branch: main
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Last refreshed: 2026-08-28T00:07:36+08:00

## Purpose

Routes small, worktree-local configuration changes through a compact Ledger lifecycle. It keeps the same evidence and verification trust boundary as ordinary changes while preventing sensitive commands or output from entering Git-tracked records.

## Load order

- Read first: `src/repo_context_ledger/runtime.py.tmpl` lifecycle parser, verification, evidence, and finish functions.
- Read if needed: `skills/repo-context-ledger/SKILL.md` and `tests/test_ledger.py` when the Agent workflow or CLI contract changes.
- Do not load by default: Context routing, Pack lifecycle governance, derived README generation, and unrelated completed Change bodies.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::record_verification` | Executes a verification outside the state lock and controls what is persisted. |
| `src/repo_context_ledger/runtime.py.tmpl::finish_change` | Collects scoped evidence in memory, validates outside the write lock, then rechecks bounded inputs before short atomic publication. |
| `src/repo_context_ledger/runtime.py.tmpl::managed_rules` | Generates the shortest-path policy used by native Agent adapters. |
| `skills/repo-context-ledger/SKILL.md` | Defines when a local configuration task can skip broad context routing and manual handoff editing. |

## Contracts and boundaries

- Invariants and contracts: Sensitive verification still executes and records status, exit code, and duration, but persists neither the command arguments nor captured output. Evidence remains limited to explicit Git-changed paths, and completed records identify worktree-local scope without claiming portable repository behavior.
- Failure / recovery: A failed sensitive check preserves the private draft with a sanitized result. `finish` must report the exact missing semantic fields or evidence instead of requiring blind retries; concurrent changes to its draft or bounded inputs preserve the session and require a fresh retry.
- Non-goals: The workflow does not commit secrets, manage `.env` values, replace Git source isolation, infer business behavior from local configuration, or weaken ordinary medium/large change gates.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py` for public CLI lifecycle, sensitive persistence, explicit finish evidence, adapter text, and diagnostic coverage. Run `python scripts/build_runtime.py --check` to prove generated runtimes match the canonical source.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Compact local configuration workflow](../../specs/compact-local-config-workflow.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:288d4092f23898a34866d4769bd21d25a2276a44809fdcb8346a330f4d50f9cf`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:fe008b1cafebdd774a0d1cb14e239cadf11038be0d99ec577d56cf1e9addc315`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:b39c63137f5eb8f1daf9a8a5dad0b46c1ede47ca0d4528df86af27a3f83304c2`
- `skills/repo-context-ledger/SKILL.md` — `sha256:c63b2a91a103321129a819986d4e778c974d57a421fad6f157f8e7aa3217c893`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:bffa98610d841a753bf44a4eb2efed51752e428a6cfddaf5ffb07f730fb3db69`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:dd1e26e29993ac93d5f52de315df130b270982125b4037dc01c17d9cb63f9a52`
- `tests/test_ledger.py` — `sha256:8f5041ab68473240b1e6cf571c3fe31df732a09110ccd48475a9236ca1cd3f70`
- `tests/test_doctor.py` — `sha256:84526dcc76e8bc08fcc4888763426729c8e73db4c6c70242abeecd763fcad8bd`
- `benchmarks/closeout_workflow_benchmark.py` — `sha256:33fb3dc82c2acd29e5bab6d3870046868a5d79858c2ac7641bb0a8102c089d6c`
- `benchmarks/README.md` — `sha256:9244091fc1202a9c40c54f2fb7f81d7e708dacd3d619f8e68e70f70ee633088a`
<!-- repo-context-ledger:pack-files:end -->
