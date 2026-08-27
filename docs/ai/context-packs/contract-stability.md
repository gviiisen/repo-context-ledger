# Contract Stability context pack

Status: current
Feature: contract-stability
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 45055d81262efa4ef1ec627ac22e578fb1be61d3
Base branch: main
Base commit: 45055d81262efa4ef1ec627ac22e578fb1be61d3
Last refreshed: 2026-08-27T08:06:27+08:00

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
| `tests/test_contract_stability.py` | Protects schemas, required fields, stable errors, privacy, and exits. |
| `scripts/evaluate_routing.py` | Produces the synthetic routing quality and latency report. |
| `tests/test_routing_evaluation.py` | Protects labeled routing, ambiguity/fallback, lifecycle selection, and read budget metrics. |
| `.github/workflows/test.yml` | Runs the complete suite on supported operating-system and Python boundaries, including release/nightly macOS. |

## Contracts and boundaries

- Invariants and contracts: minor versions preserve commands, required fields, meanings, privacy, and exit classes; incompatible changes require a new schema and major project version.
- Failure / recovery: golden or routing failures block release until the change is additive or receives an explicit new schema and migration; human text output remains available for recovery.
- Non-goals: compatibility does not freeze timing values or every prose line, import production data, support Python below 3.10, or expose foreign private session details.

## Verification

`python -m unittest discover -s tests -p test_contract_stability.py` verifies JSON schemas, privacy, stable errors, and exit codes. `python -m unittest discover -s tests -p test_routing_evaluation.py` verifies the synthetic routing corpus. The GitHub Actions matrix runs `python -m unittest discover -s tests -v` on Windows/Ubuntu and Python 3.10/3.12, plus release/nightly/manual macOS.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Contract Stability](../../specs/contract-stability.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/constants.pyfrag` — `sha256:bdfac50c0e0f2aa013c6f73e1ca259921559e999e715924994411dc9fad855c4`
- `src/repo_context_ledger/errors.pyfrag` — `sha256:7cd76293bd376f12cf7e13ba747159820667919afcc720098e7958ee05bb9717`
- `src/repo_context_ledger/models.pyfrag` — `sha256:b059542121c00e2177408be18fc1252d4d3f32a5ae4438b2634eb3da49f874d4`
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:8dbccc54b87e0dfd05f93edadc3f716ac4873450d1e240801ebfa2101f1ca9f5`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:c72b923b0c5f1cd758e5771e914e150f9bc885a2ba176410287c077804645007`
- `tests/test_baseline_contract.py` — `sha256:9b5385a16b70793062744809f8d70e28cbe468b130bc98a4629bd93af6789baa`
- `tests/golden/v0.6.0-contract.json` — `sha256:2035883115255bdb5d7108427699dfbf2dac39261426e84fa6e46ddda32784c0`
- `tests/golden/v0.6.0-status-text.txt` — `sha256:063e99bc6187672743bef6a8fdc444c2f26118008ba700927830d08a958a3a50`
- `tests/fixtures/v0.6.0-legacy-context-state.json` — `sha256:87dc4808f14910a693f01433675a8f4f3898e0972848518f6de585ba4cfcffd6`
- `tests/test_contract_stability.py` — `sha256:a401ce9600c5898308fc95baefc7db8598ac8f389aef556d78e86108060a9614`
- `tests/golden/v0.6.2-cli-contract.json` — `sha256:814c73bf300d90966625dce4fd727a0d3f9c9184eeced8cd42251686cd6611d0`
- `scripts/evaluate_routing.py` — `sha256:d798030a684e81e0f8d298136abf3a72309da3f4c51384fcebdc251210137833`
- `tests/test_routing_evaluation.py` — `sha256:4bee2325cc493db7fedc8c77b637806cf84cabb2e513f424b64f51da61f6f53d`
- `tests/fixtures/routing-eval-v1.json` — `sha256:6eaf30268655247499174dfa9913969f4b1915aa98b02c0587f5ff9a7e53c4cc`
- `.github/workflows/test.yml` — `sha256:8d268c040a7c68c86a738aee36d01e5a34d102723bbf722e3665ee982d195ade`
- `COMPATIBILITY.md` — `sha256:a217d760761004c34de3d9f32ab3f5eaa16628175b34cbdb47996fff9eb66a0e`
- `MIGRATIONS.md` — `sha256:f084594fb1a7c3bddaa70c74ffb93efcd6647b75ed9d57821f78c9813affc908`
<!-- repo-context-ledger:pack-files:end -->
