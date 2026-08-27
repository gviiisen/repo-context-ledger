# Runtime Architecture context pack

Status: current
Feature: runtime-architecture
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 25b94983f63d44d3f7134c37621957d531ad88f2
Base branch: main
Base commit: 0d7e1f289e726edc4ae2b621361f89c621de5623
Last refreshed: 2026-08-27T18:55:02+08:00

## Purpose

Routes runtime changes to one editable template, ordered low-coupling fragments, the deterministic builder, Git-path reliability code, and focused architecture tests. Generated Skill/dogfood runtimes remain byte-identical standalone files so initialized repositories gain the maintainability improvement without a package dependency.

## Load order

- Read first: Read `ARCHITECTURE.md` and `docs/specs/runtime-architecture.md`, then edit the relevant source template or fragment.
- Read if needed: Read `scripts/build_runtime.py`, `tests/test_runtime_build.py`, `tests/test_repository_reliability.py`, `tests/test_lock_and_preset_trust.py`, and the affected public contract tests when changing generation, Git state, write coordination, preset execution, or extraction boundaries.
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
| `tests/test_lock_and_preset_trust.py` | Verifies lock diagnosis/ownership and exact principal-local preset trust. |
| `SECURITY.md` / `THREAT_MODEL.md` | Explain the public security and local trust boundary. |

## Contracts and boundaries

- Invariants and contracts: both generated outputs are byte-identical after Windows or Unix checkout, contain no timestamp or absolute build path, use only Python 3.10+ standard library, report the version from `constants.pyfrag`, preserve an existing target's Unix mode, and retain all v0.6.2 CLI/JSON/exit behavior. Git path readers split NUL-delimited bytes before decoding and use rename destinations.
- Failure / recovery: invalid source, a missing/duplicate marker, output drift, a failed required Git query, or missing preset trust returns 2. Required Git failures use `GIT_COMMAND_FAILED`; untrusted presets use `PRESET_TRUST_REQUIRED`. Diagnose locks before manual cleanup and repair canonical source/repository state rather than patching one generated file or assuming an empty change set.
- Non-goals: v0.7.0 does not create a published Python package, add dependencies, split every subsystem, change `init` distribution, or redesign routing/lifecycle semantics.

## Verification

`python scripts/build_runtime.py --check` verifies repository outputs match source. `python -m unittest discover -s tests -p test_runtime_build.py` verifies deterministic fresh builds, drift detection, compilation, and standalone version execution. `python -m unittest discover -s tests -p test_repository_reliability.py` verifies Git paths, fail-closed reads, and permissions. `python -m unittest discover -s tests -p test_lock_and_preset_trust.py` verifies lock safety and preset trust; the complete suite protects behavior.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Runtime Architecture](../../specs/runtime-architecture.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `.gitattributes` — `sha256:74b3190f5e5511242a0f8cca97184bafadf3ae5a151d95fe9f1d45cb5944dc29`
- `src/repo_context_ledger/__init__.py` — `sha256:afeadce023c709f93c003327e9b023da4b14aaf59e275418e47de6978ce42615`
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:b5b0d9eba8bb211c07ba21e39e83ee8269ba598645a83872534bed4f3bdd7d7e`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:baf40f4ac0a9038f33d90975b07c5e7fdd581ab45561e8cf29e522b59954a95f`
- `src/repo_context_ledger/errors.pyfrag` — `sha256:7cd76293bd376f12cf7e13ba747159820667919afcc720098e7958ee05bb9717`
- `src/repo_context_ledger/models.pyfrag` — `sha256:54149dd494724f91ee4a4530892b074261c9888d940e561ee0b301687a37d4d2`
- `src/repo_context_ledger/contracts.pyfrag` — `sha256:7c16c987fa157b6333528f6f6d42bb5aa72718ba28dc7186c3832fb5c59ca860`
- `scripts/build_runtime.py` — `sha256:122a996b6ce173547def7ae68a449c4afdb274e5f1c01d5cd9edeed0a64b4b05`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:a54d09dbb14a7ca7b6368bb8ec957dfa5a4a4f4aafe06fc8ce507c97895384b6`
- `skills/repo-context-ledger/SKILL.md` — `sha256:c49a692005ff85c62c4fc3ebb5617af4725c55bba3857a3413b5c4d8bba4e12a`
- `skills/repo-context-ledger/references/verification-presets.md` — `sha256:0650fa160e9a46a3b0f6cad68c8153f09614626e2046eb4acada3ab8b59e04f3`
- `tests/test_runtime_build.py` — `sha256:99ccffc22f8bdf26596ad97c5b21c7681d37b0505d2b9836810645f0dd9421d5`
- `tests/test_repository_reliability.py` — `sha256:4d3df992a9a933830eb42b9c6c76b7f6156d4eadbef82dc2a8c99b21b9b90022`
- `tests/test_lock_and_preset_trust.py` — `sha256:4efb34f5c3d2de6d8ea226fa570d66399061e7497d1e8b84fd3acfcfa0ab1e5d`
- `tests/test_ledger.py` — `sha256:7944c012f406e8c8dabe7946a07f6477a886515104e53b2de9c8497162bfc65e`
- `ARCHITECTURE.md` — `sha256:f100d252d793d5477d614f96f565fa43c1aebf0785a464c7bc996c853b0581f1`
- `SECURITY.md` — `sha256:e3bae6d08d032d2b56bc23ad9571b3dc94f0e81502f802b484aa031634e4734c`
- `THREAT_MODEL.md` — `sha256:3ff1f8795c87223a7b3c8d03ad714150c135571bfa458de039e10756739e3575`
- `.github/workflows/test.yml` — `sha256:8d268c040a7c68c86a738aee36d01e5a34d102723bbf722e3665ee982d195ade`
<!-- repo-context-ledger:pack-files:end -->
