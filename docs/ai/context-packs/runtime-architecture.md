# Runtime Architecture context pack

Status: current
Feature: runtime-architecture
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: f71e59fd47dfa3a39d192d3bee2c7990d365320b
Base branch: main
Base commit: b5086a53c21962593ada4a0b96903faf10a7e54c
Last refreshed: 2026-08-22T00:28:00+08:00

## Purpose

Routes runtime changes to one editable template, ordered low-coupling fragments, the deterministic builder, and focused architecture tests. Generated Skill/dogfood runtimes remain byte-identical standalone files so initialized repositories gain the maintainability improvement without a package dependency.

## Load order

- Read first: Read `ARCHITECTURE.md` and `docs/specs/runtime-architecture.md`, then edit the relevant source template or fragment.
- Read if needed: Read `scripts/build_runtime.py`, `tests/test_runtime_build.py`, and the affected public contract tests when changing generation or extraction boundaries.
- Do not load by default: Do not edit generated runtime outputs, load completed Changes, or split unrelated subsystems merely because they remain in the template.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl` | Canonical executable body and ordered build markers. |
| `src/repo_context_ledger/constants.pyfrag` | Canonical version/schema/exit and runtime constants. |
| `src/repo_context_ledger/errors.pyfrag` | Canonical `LedgerError` and stable machine error codes. |
| `src/repo_context_ledger/models.pyfrag` | Canonical typed result models such as `CommandResult`. |
| `src/repo_context_ledger/contracts.pyfrag` | Non-built compatibility pointer to the ordered fragments. |
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
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:749a0e9e21aaeb2aa30458d4e6362093f378cd686fbe15eb388fab38e2bf4095`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:9f8f74c038568a3960d15e9591fcd3c57d4a9dd6b8f3a7e03e7ce7afb5c7ca70`
- `src/repo_context_ledger/errors.pyfrag` — `sha256:7cd76293bd376f12cf7e13ba747159820667919afcc720098e7958ee05bb9717`
- `src/repo_context_ledger/models.pyfrag` — `sha256:b059542121c00e2177408be18fc1252d4d3f32a5ae4438b2634eb3da49f874d4`
- `src/repo_context_ledger/contracts.pyfrag` — `sha256:7c16c987fa157b6333528f6f6d42bb5aa72718ba28dc7186c3832fb5c59ca860`
- `scripts/build_runtime.py` — `sha256:23b564a2d6517b80f2266f0f6304bbf122839c691486873302de858c9f68446c`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:10ad9799b414ba117d7d6c16598f31401bdce626ecf959d9c4ef3f6ae69dd561`
- `tests/test_runtime_build.py` — `sha256:bcfcc1a0f6db972b5da68a579a3a4478bdd86cf0511e6ed18386be086803fb90`
- `ARCHITECTURE.md` — `sha256:eea140b99405958b26834b6da7e224824c606ed0d3201f0cc8c3a8dd8a6b9efe`
- `.github/workflows/test.yml` — `sha256:8d268c040a7c68c86a738aee36d01e5a34d102723bbf722e3665ee982d195ade`
<!-- repo-context-ledger:pack-files:end -->
