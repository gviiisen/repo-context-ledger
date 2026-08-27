# Runtime Architecture context pack

Status: current
Feature: runtime-architecture
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 0d7e1f289e726edc4ae2b621361f89c621de5623
Base branch: main
Base commit: 0d7e1f289e726edc4ae2b621361f89c621de5623
Last refreshed: 2026-08-27T17:14:38+08:00

## Purpose

Routes runtime changes to one editable template, ordered low-coupling fragments, the deterministic builder, Git-path reliability code, and focused architecture tests. Generated Skill/dogfood runtimes remain byte-identical standalone files so initialized repositories gain the maintainability improvement without a package dependency.

## Load order

- Read first: Read `ARCHITECTURE.md` and `docs/specs/runtime-architecture.md`, then edit the relevant source template or fragment.
- Read if needed: Read `scripts/build_runtime.py`, `tests/test_runtime_build.py`, `tests/test_repository_reliability.py`, and the affected public contract tests when changing generation, Git state, or extraction boundaries.
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
| `.gitattributes` | Pins build inputs and both generated outputs to LF on Windows and Unix. |
| `tests/test_runtime_build.py` | Verifies drift detection, atomic build outputs, byte identity, compilation, and standalone execution. |
| `tests/test_repository_reliability.py` | Verifies NUL-safe Git paths, fail-closed required Git reads, and existing target modes. |

## Contracts and boundaries

- Invariants and contracts: both generated outputs are byte-identical after Windows or Unix checkout, contain no timestamp or absolute build path, use only Python 3.10+ standard library, report the version from `constants.pyfrag`, preserve an existing target's Unix mode, and retain all v0.6.2 CLI/JSON/exit behavior. Git path readers split NUL-delimited bytes before decoding and use rename destinations.
- Failure / recovery: invalid source, a missing/duplicate marker, output drift, or a failed required Git query returns 2; required Git failures use `GIT_COMMAND_FAILED`. Repair canonical source/repository state and retry rather than patching one generated file or assuming an empty change set.
- Non-goals: v0.7.0 does not create a published Python package, add dependencies, split every subsystem, change `init` distribution, or redesign routing/lifecycle semantics.

## Verification

`python scripts/build_runtime.py --check` verifies repository outputs match source. `python -m unittest discover -s tests -p test_runtime_build.py` verifies deterministic fresh builds, drift detection, compilation, and standalone version execution. `python -m unittest discover -s tests -p test_repository_reliability.py` verifies Git paths, fail-closed reads, and permissions; the complete suite protects behavior.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Runtime Architecture](../../specs/runtime-architecture.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `.gitattributes` — `sha256:74b3190f5e5511242a0f8cca97184bafadf3ae5a151d95fe9f1d45cb5944dc29`
- `src/repo_context_ledger/__init__.py` — `sha256:afeadce023c709f93c003327e9b023da4b14aaf59e275418e47de6978ce42615`
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:cd9b6bdb236a0a82663ac5103e6ce497b582af6f34e17fc90efead02f470f556`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:b2b8255878e161e8bb714579a5f23db7f81dac14d31b5b3b3f506c4ec3bd0c65`
- `src/repo_context_ledger/errors.pyfrag` — `sha256:7cd76293bd376f12cf7e13ba747159820667919afcc720098e7958ee05bb9717`
- `src/repo_context_ledger/models.pyfrag` — `sha256:54149dd494724f91ee4a4530892b074261c9888d940e561ee0b301687a37d4d2`
- `src/repo_context_ledger/contracts.pyfrag` — `sha256:7c16c987fa157b6333528f6f6d42bb5aa72718ba28dc7186c3832fb5c59ca860`
- `scripts/build_runtime.py` — `sha256:122a996b6ce173547def7ae68a449c4afdb274e5f1c01d5cd9edeed0a64b4b05`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:cc9b316f93acba5c60710dbbc139dbcf1bdc35b5f398f52a2d13ff52bb7dc167`
- `tests/test_runtime_build.py` — `sha256:3e7edd024277cc1a8c4a426684c15520afce186e85793fea31cd59cbaf4c3fa1`
- `tests/test_repository_reliability.py` — `sha256:4d3df992a9a933830eb42b9c6c76b7f6156d4eadbef82dc2a8c99b21b9b90022`
- `ARCHITECTURE.md` — `sha256:291fe4f9aa62674eb320369f6f79261631e4419c2026e5f5a02a0e5a4f400e87`
- `.github/workflows/test.yml` — `sha256:8d268c040a7c68c86a738aee36d01e5a34d102723bbf722e3665ee982d195ade`
<!-- repo-context-ledger:pack-files:end -->
