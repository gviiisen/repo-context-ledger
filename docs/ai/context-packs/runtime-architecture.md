# Runtime Architecture context pack

Status: current
Feature: runtime-architecture
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 6bdf90c56b59fde8890632b113bd61ccb9239c73
Base branch: main
Base commit: b5086a53c21962593ada4a0b96903faf10a7e54c
Last refreshed: 2026-08-21T23:41:26+08:00

## Purpose

Routes runtime changes to one editable template, the contracts fragment, deterministic builder, and focused architecture tests. Generated Skill/dogfood runtimes remain byte-identical standalone files so initialized repositories gain the maintainability improvement without a package dependency.

## Load order

- Read first: Read `ARCHITECTURE.md` and `docs/specs/runtime-architecture.md`, then edit the relevant source template or fragment.
- Read if needed: Read `scripts/build_runtime.py`, `tests/test_runtime_build.py`, and the affected public contract tests when changing generation or extraction boundaries.
- Do not load by default: Do not edit generated runtime outputs, load completed Changes, or split unrelated subsystems merely because they remain in the template.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl` | Canonical executable body and one ordered build marker. |
| `src/repo_context_ledger/contracts.pyfrag` | Canonical version/schema/exit constants, `LedgerError`, and typed `CommandResult`. |
| `scripts/build_runtime.py::render_runtime` | Produces normalized deterministic standalone bytes. |
| `tests/test_runtime_build.py` | Verifies drift detection, atomic build outputs, byte identity, compilation, and standalone execution. |

## Contracts and boundaries

- Invariants and contracts: both generated outputs are byte-identical, contain no timestamp or absolute build path, use only Python 3.10+ standard library, and preserve all v0.6.2 CLI/JSON/exit behavior.
- Failure / recovery: invalid source, a missing/duplicate marker, or output drift returns 2; repair canonical source and rebuild rather than patching one generated file.
- Non-goals: v0.7.0 does not create a published Python package, add dependencies, split every subsystem, change `init` distribution, or redesign routing/lifecycle semantics.

## Verification

`python scripts/build_runtime.py --check` verifies repository outputs match source. `python -m unittest discover -s tests -p test_runtime_build.py` verifies deterministic fresh builds, drift detection, compilation, and standalone version execution; the complete suite protects behavior.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Runtime Architecture](../../specs/runtime-architecture.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/__init__.py` — `sha256:afeadce023c709f93c003327e9b023da4b14aaf59e275418e47de6978ce42615`
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:39eeac3c3784b2facf2feb142ef2f14e8cb7ec674a51db8dd64fd9d86681f7ce`
- `src/repo_context_ledger/contracts.pyfrag` — `sha256:83cacf48c9ef9e8f8edfe072ecc85961e8a6d1acf210b6808c7caa80fe21dce1`
- `scripts/build_runtime.py` — `sha256:17845507aeae186087f4c42df07c84252362c2b8420073316a011108d83d7c4e`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:15141c54d126e9d9d74b41163430e4c3d8bada1169b32e96a56e6fe8451ea9a9`
- `tests/test_runtime_build.py` — `sha256:753d14de763f5ac82441e2b28701e4e3a36829e38137369201e750e93b18402c`
- `ARCHITECTURE.md` — `sha256:48e5be9d3540eb82b6b6649f2855694f61bc205ab7db0310d7799092e4425d1e`
- `.github/workflows/test.yml` — `sha256:417cceafdabf577bb67d831cb5f58ec739aed3e75413a4357d65d4c2ef9884fd`
<!-- repo-context-ledger:pack-files:end -->
