# Compact Local Configuration Workflow context pack

Status: current
Feature: compact-local-config-workflow
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: e9589ed8c0474590bc6266d9d92424ac1b5050cb
Base branch: main
Base commit: b7e4eb53249faa64881e37401a764093faf476b7
Last refreshed: 2026-08-27T07:16:02+08:00

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

- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:bb86aed0eb01b87403cfcfe6f95f3895cc2fa7dc6d74b5c38568b5b0ff8a9a08`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:3df3ad1683588826e815cb3576f8e63d8bb320928c478222bead0c55736dffc2`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:187328722f04f19285b4e95115a6bda0b565ab554419156797307229a911045c`
- `skills/repo-context-ledger/SKILL.md` — `sha256:819c709ed64de35af4cf57efc4967ccb68554d340ffc4aac673222fb5763b6d2`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:6dc2c1cc8f3483e2c977e0e58483559d93411247d69fe3623d047e4486279003`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:dd1e26e29993ac93d5f52de315df130b270982125b4037dc01c17d9cb63f9a52`
- `tests/test_ledger.py` — `sha256:bb1837198bb1324bea43b4f974991d59041780970efe5251a20085a83fd4a03a`
- `tests/test_doctor.py` — `sha256:84526dcc76e8bc08fcc4888763426729c8e73db4c6c70242abeecd763fcad8bd`
- `benchmarks/closeout_workflow_benchmark.py` — `sha256:33fb3dc82c2acd29e5bab6d3870046868a5d79858c2ac7641bb0a8102c089d6c`
- `benchmarks/README.md` — `sha256:9244091fc1202a9c40c54f2fb7f81d7e708dacd3d619f8e68e70f70ee633088a`
<!-- repo-context-ledger:pack-files:end -->
