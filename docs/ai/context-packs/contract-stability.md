# Contract Stability context pack

Status: current
Feature: contract-stability
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: db89319282707f639addbd92e6e6fd1f8e88444d
Base branch: main
Base commit: b5086a53c21962593ada4a0b96903faf10a7e54c
Last refreshed: 2026-08-21T23:35:26+08:00

## Purpose

Routes compatibility work to the public CLI schemas, golden fixtures, routing corpus, and platform matrix. It keeps human text output available while giving automation explicit versioned JSON and documented exit behavior across minor upgrades.

## Load order

- Read first: Read `docs/specs/contract-stability.md` and `COMPATIBILITY.md`, then the command-specific runtime function.
- Read if needed: Read `tests/test_contract_stability.py`, its golden fixture, the synthetic routing corpus, and `MIGRATIONS.md` when changing a public schema, exit class, upgrade, or platform guarantee.
- Do not load by default: Do not load completed Changes, private session bodies, production repositories, or unrelated command implementations.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::status_report` | Produces `status-v1` with privacy-bounded session and inventory data. |
| `skills/repo-context-ledger/scripts/ledger.py::captured_command_json` | Projects existing checks into `check-v1` without changing their exit class. |
| `tests/test_contract_stability.py` | Protects schemas, required fields, privacy, exits, and synthetic routing selection. |
| `.github/workflows/test.yml` | Runs the complete suite on supported operating-system and Python boundaries. |

## Contracts and boundaries

- Invariants and contracts: minor versions preserve commands, required fields, meanings, privacy, and exit classes; incompatible changes require a new schema and major project version.
- Failure / recovery: golden or routing failures block release until the change is additive or receives an explicit new schema and migration; human text output remains available for recovery.
- Non-goals: compatibility does not freeze timing values or every prose line, import production data, support Python below 3.10, or expose foreign private session details.

## Verification

`python -m unittest discover -s tests -p test_contract_stability.py` verifies JSON schemas, privacy, exit codes, and the synthetic routing corpus. The GitHub Actions matrix runs `python -m unittest discover -s tests -v` on Windows/Ubuntu and Python 3.10/3.12.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Contract Stability](../../specs/contract-stability.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:5c468f83b60312eaa70064e50e140fe75aa258f1560da8b8362a9148532c0d0a`
- `tests/test_contract_stability.py` — `sha256:d83717b74cc199e8b0fb0839921c0eec36fbf8f649bc2f9c5d3b37b649451705`
- `tests/golden/v0.6.2-cli-contract.json` — `sha256:8f360ad905e6a2621ffbf09e02bf0184120e724053bb7478e0d3a436ab6ba608`
- `tests/fixtures/routing-eval-v1.json` — `sha256:ac41c44d00ff9bb5055a6af23983e60e0fea235ef91acb3ec66c8cffb7c15db0`
- `.github/workflows/test.yml` — `sha256:00a34390ac38e45969dbfa058650e6fa3117c8e580ddfdc7cc6f6f9751f9a6b6`
- `COMPATIBILITY.md` — `sha256:a852b2f0f75e98a774d3376e94bfd7b9f1fbbfe878cc4ce4a5f725d878c7a6ac`
- `MIGRATIONS.md` — `sha256:ec18bc88ff8a84b33da51fc59ae114982b64cc42e4881ae2e6b8e341922a7923`
<!-- repo-context-ledger:pack-files:end -->
