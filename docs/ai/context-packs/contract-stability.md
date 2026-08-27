# Contract Stability context pack

Status: current
Feature: contract-stability
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: cc673f18238af119ecfe5cf08ffc2b4b3fc698e8
Base branch: main
Base commit: cc673f18238af119ecfe5cf08ffc2b4b3fc698e8
Last refreshed: 2026-08-27T20:39:19+08:00

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
| `schemas/*.schema.json` | Publishes Draft 2020-12 top-level contracts for every stable JSON protocol. |
| `tests/test_protocol_schemas.py` | Recursively compares real success, no-match, and error reports with published required fields, types, constants, arrays, and enums. |
| `tests/test_contract_stability.py` | Protects schemas, required fields, stable errors, privacy, and exits. |
| `scripts/evaluate_routing.py` | Produces the synthetic routing quality and latency report. |
| `tests/test_routing_evaluation.py` | Protects labeled routing, ambiguity/fallback, lifecycle selection, and read budget metrics. |
| `.github/workflows/test.yml` | Runs the complete suite on supported operating-system and Python boundaries, including release/nightly macOS. |

## Contracts and boundaries

- Invariants and contracts: 1.x minor versions preserve commands, required fields, scalar types, meanings, privacy, and exit classes; incompatible changes require a new schema and major project version.
- Failure / recovery: golden or routing failures block release until the change is additive or receives an explicit new schema and migration; human text output remains available for recovery.
- Non-goals: compatibility does not freeze timing values or every prose line, import production data, support Python below 3.10, or expose foreign private session details.

## Verification

`python tests/test_protocol_schemas.py` checks real success, no-match, error, and Resume Capsule reports against published schemas. `python -m unittest discover -s tests -p test_contract_stability.py` verifies privacy, stable errors, and exit codes. `python -m unittest discover -s tests -p test_routing_evaluation.py` verifies the synthetic routing corpus. The GitHub Actions matrix runs `python -m unittest discover -s tests -v` on Windows/Ubuntu and Python 3.10/3.12, plus release/nightly/manual macOS.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Contract Stability](../../specs/contract-stability.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/constants.pyfrag` — `sha256:81a8fb3f2c0e857b28f88b9a6d75e31e6d40e485835517d7c50c95296ff5ed44`
- `src/repo_context_ledger/errors.pyfrag` — `sha256:7cd76293bd376f12cf7e13ba747159820667919afcc720098e7958ee05bb9717`
- `src/repo_context_ledger/models.pyfrag` — `sha256:a22d3de153c2deff0417d79af5e90dbb907ec2820d475fc7d9be7ed9fc06893a`
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:703ce2da25b3f3455576ce0bbe2ef3e1307d076113de234b20fc8ac02f209603`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:b9dfc812d8554191ad300a6816092ff171d9062c76af51d5dfc6f13f4c6ba0f7`
- `schemas/README.md` — `sha256:edfc6ed9e01236021278fbd276092a8acd8fb44c140cd81be4170006278ffb29`
- `schemas/workflow-plan-v1.schema.json` — `sha256:8e298fa8bd11aaeab1a89b322b2b4f63541b8137ebc7f492b526e4ba802f7ebe`
- `schemas/context-bundle-v1.schema.json` — `sha256:bba40cd2f4e0d8a630b82cc3372fc820a110f2a0433741aec766da84a903806d`
- `schemas/resume-capsule-v2.schema.json` — `sha256:fcd63396affee88abe9c55201051cd98356bfedcbebd1576ed0a4e52276b17cf`
- `schemas/doctor-v1.schema.json` — `sha256:9c81036fb2bc9092106a42da6348acedb43321ff8a11e663c0d3a7f83f2d250f`
- `schemas/status-v1.schema.json` — `sha256:cf073a9cde02783cb4d3f7e3212110d76b7ca2ce959e2e3e6e2ff660b71b2cad`
- `schemas/check-v1.schema.json` — `sha256:09394e23e49e2fde53b351b17fda961ca8cb4fa0d975bba4ac6d87786703b789`
- `tests/test_protocol_schemas.py` — `sha256:ee28283b2ace2f73e0e674e53abb97fa0a7952c1bd961a7d6022cb0a5f8ec59b`
- `tests/test_baseline_contract.py` — `sha256:9b5385a16b70793062744809f8d70e28cbe468b130bc98a4629bd93af6789baa`
- `tests/golden/v0.6.0-contract.json` — `sha256:2035883115255bdb5d7108427699dfbf2dac39261426e84fa6e46ddda32784c0`
- `tests/golden/v0.6.0-status-text.txt` — `sha256:063e99bc6187672743bef6a8fdc444c2f26118008ba700927830d08a958a3a50`
- `tests/fixtures/v0.6.0-legacy-context-state.json` — `sha256:87dc4808f14910a693f01433675a8f4f3898e0972848518f6de585ba4cfcffd6`
- `tests/test_contract_stability.py` — `sha256:c9a2a07ce6987d4510344c559fc4152de82e828588a09067b2b85e171a7cd61e`
- `tests/golden/v0.6.2-cli-contract.json` — `sha256:814c73bf300d90966625dce4fd727a0d3f9c9184eeced8cd42251686cd6611d0`
- `scripts/evaluate_routing.py` — `sha256:d798030a684e81e0f8d298136abf3a72309da3f4c51384fcebdc251210137833`
- `tests/test_routing_evaluation.py` — `sha256:4bee2325cc493db7fedc8c77b637806cf84cabb2e513f424b64f51da61f6f53d`
- `tests/fixtures/routing-eval-v1.json` — `sha256:6eaf30268655247499174dfa9913969f4b1915aa98b02c0587f5ff9a7e53c4cc`
- `.github/workflows/test.yml` — `sha256:8d268c040a7c68c86a738aee36d01e5a34d102723bbf722e3665ee982d195ade`
- `COMPATIBILITY.md` — `sha256:8d8836a2a0bd7f96e863309eead81a2044272c58212d7e6fde88303352b8525d`
- `MIGRATIONS.md` — `sha256:3883ad8ec72e7ddda2e05d04fef4c851083d85bb511667e70fe84cec7b72ab48`
<!-- repo-context-ledger:pack-files:end -->
