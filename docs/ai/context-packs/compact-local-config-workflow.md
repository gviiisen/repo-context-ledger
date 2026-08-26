# Compact Local Configuration Workflow context pack

Status: current
Feature: compact-local-config-workflow
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: dd283c73130ec672e183fe8018c4b19217efdf52
Base branch: main
Base commit: dd283c73130ec672e183fe8018c4b19217efdf52
Last refreshed: 2026-08-27T03:10:11+08:00

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
| `src/repo_context_ledger/runtime.py.tmpl::finish_change` | Collects scoped evidence, validates the private draft, and publishes the completed record. |
| `src/repo_context_ledger/runtime.py.tmpl::managed_rules` | Generates the shortest-path policy used by native Agent adapters. |
| `skills/repo-context-ledger/SKILL.md` | Defines when a local configuration task can skip broad context routing and manual handoff editing. |

## Contracts and boundaries

- Invariants and contracts: Sensitive verification still executes and records status, exit code, and duration, but persists neither the command arguments nor captured output. Evidence remains limited to explicit Git-changed paths, and completed records identify worktree-local scope without claiming portable repository behavior.
- Failure / recovery: A failed sensitive check preserves the private draft with a sanitized result. `finish` must report the exact missing semantic fields or evidence instead of requiring blind retries.
- Non-goals: The workflow does not commit secrets, manage `.env` values, replace Git source isolation, infer business behavior from local configuration, or weaken ordinary medium/large change gates.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py` for public CLI lifecycle, sensitive persistence, explicit finish evidence, adapter text, and diagnostic coverage. Run `python scripts/build_runtime.py --check` to prove generated runtimes match the canonical source.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Compact local configuration workflow](../../specs/compact-local-config-workflow.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:40c2eb4a9416c016389a7ac2103a7e13dd0ee1071f4a4942d3b9a06854a5d179`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:fd4513a88e9c6f4fffe0fb2830aa3d244896f84d4b9f0244b8eac583580aa013`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:5ee5cb22543f6503690ed2ec029d26b08fd01112e4f55fc98f4daa90bb7ecc8f`
- `skills/repo-context-ledger/SKILL.md` — `sha256:9447c641f2f1c18fa5277802884168ca0012ce723ba5ef242d5d6400dfec5f29`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:dd1e26e29993ac93d5f52de315df130b270982125b4037dc01c17d9cb63f9a52`
- `tests/test_ledger.py` — `sha256:1ddd3a3772db670e54caf4035278e902e0ac413ba0c205f8889eb0b21e1551c4`
- `tests/test_doctor.py` — `sha256:84526dcc76e8bc08fcc4888763426729c8e73db4c6c70242abeecd763fcad8bd`
<!-- repo-context-ledger:pack-files:end -->
