# Compact Local Configuration Workflow context pack

Status: current
Feature: compact-local-config-workflow
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 645a736f8220153a77d8cb041d6317eb85d10b9d
Base branch: main
Base commit: dd283c73130ec672e183fe8018c4b19217efdf52
Last refreshed: 2026-08-27T03:24:07+08:00

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

- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:9f28b035993bed81e544a97df92606b97f64ad2582d36eb20f75a2d646ab38c4`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:fd4513a88e9c6f4fffe0fb2830aa3d244896f84d4b9f0244b8eac583580aa013`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:86474076e7bc9a017add5f7bc2876ff5673ea1f070ed3e9db92e798dba9e5335`
- `skills/repo-context-ledger/SKILL.md` — `sha256:e11f507cc45f9656a678735dd173e538aa630ec8cc76c4f7cf0278048ed45ca7`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:dd1e26e29993ac93d5f52de315df130b270982125b4037dc01c17d9cb63f9a52`
- `tests/test_ledger.py` — `sha256:f0e658499374846c84e107a55a30d150d49ffaf60bf788e9be2fb8a952b81bad`
- `tests/test_doctor.py` — `sha256:84526dcc76e8bc08fcc4888763426729c8e73db4c6c70242abeecd763fcad8bd`
<!-- repo-context-ledger:pack-files:end -->
