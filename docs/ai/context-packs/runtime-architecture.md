# Runtime Architecture context pack

Status: current
Feature: runtime-architecture
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 4800d58e9bde70c8f0b55a9afe0f6e7df90480d2
Base branch: main
Base commit: cc673f18238af119ecfe5cf08ffc2b4b3fc698e8
Last refreshed: 2026-08-27T21:54:17+08:00

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
| `src/repo_context_ledger/locks.pyfrag` | Canonical short-lock acquisition and ownership-safe cleanup. |
| `src/repo_context_ledger/git.pyfrag` | Canonical core Git execution and fail-closed identity queries. |
| `src/repo_context_ledger/workflow.pyfrag` | Canonical Workflow Plan classifier and renderer. |
| `src/repo_context_ledger/contracts.pyfrag` | Non-built compatibility pointer to the ordered fragments. |
| `scripts/build_runtime.py::render_runtime` | Produces normalized deterministic standalone bytes. |
| `.gitattributes` | Pins build inputs and both generated outputs to LF on Windows and Unix. |
| `tests/test_runtime_build.py` | Verifies drift detection, atomic build outputs, byte identity, compilation, and standalone execution. |
| `tests/test_repository_reliability.py` | Verifies NUL-safe Git paths, fail-closed required Git reads, and existing target modes. |
| `tests/test_lock_and_preset_trust.py` | Verifies lock diagnosis/ownership and exact principal-local preset trust. |
| `schemas/*.schema.json` | Publishes public 1.x JSON protocol boundaries without runtime imports. |
| `tests/test_protocol_schemas.py` | Executes CLI reports against those published top-level contracts. |
| `SECURITY.md` / `THREAT_MODEL.md` | Explain the public security and local trust boundary. |

## Contracts and boundaries

- Invariants and contracts: both generated outputs are byte-identical after Windows or Unix checkout, contain no timestamp or absolute build path, use only Python 3.10+ standard library, preserve existing Unix modes, assign new public/private files `0644`/`0600`, and retain published 1.x behavior. Git path readers split NUL-delimited bytes before decoding; rename Coverage resolves old ownership at merge base and new ownership from current same-feature Packs while destination-oriented consumers remain compatible.
- Failure / recovery: invalid source, a missing/duplicate marker, output drift, a failed required Git query, or missing preset trust returns 2. Required Git failures use `GIT_COMMAND_FAILED`; untrusted presets use `PRESET_TRUST_REQUIRED`. Diagnose locks before manual cleanup and repair canonical source/repository state rather than patching one generated file or assuming an empty change set.
- Non-goals: v1.0 does not create a published Python package, add dependencies, split every subsystem, change `init` distribution, or redesign routing/lifecycle semantics.

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
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:aabb91b17f8a9bae7d42d2932d20eeb5b37819e6c358a0b517c253d71c8c6a39`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:81a8fb3f2c0e857b28f88b9a6d75e31e6d40e485835517d7c50c95296ff5ed44`
- `src/repo_context_ledger/errors.pyfrag` — `sha256:7cd76293bd376f12cf7e13ba747159820667919afcc720098e7958ee05bb9717`
- `src/repo_context_ledger/models.pyfrag` — `sha256:a22d3de153c2deff0417d79af5e90dbb907ec2820d475fc7d9be7ed9fc06893a`
- `src/repo_context_ledger/locks.pyfrag` — `sha256:185ce4c5f8187f1c44d684299e0e090173d3ab371e556852ef82f78d708aff7a`
- `src/repo_context_ledger/git.pyfrag` — `sha256:934ffac62d7780f524f36aad7a431e8d4323daf43f7d440a2043a1cb78fa5b21`
- `src/repo_context_ledger/workflow.pyfrag` — `sha256:6099dec2fe65490a333c98ce9b61b363c56fc1012281ca83398c48088a33cc09`
- `src/repo_context_ledger/contracts.pyfrag` — `sha256:542f32ce352a7450693a70eb559c983188c150e08b5933d2ce9e9d28400d448c`
- `scripts/build_runtime.py` — `sha256:c94ec02761a97d70631a2f261780f569e357f026d1a86c6d293359dff5cb6324`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:f00aafdd16ed109963ed90b5bc4d77b2fc2b0c4f230a09e4cba7e52b8fa45d49`
- `skills/repo-context-ledger/SKILL.md` — `sha256:c49a692005ff85c62c4fc3ebb5617af4725c55bba3857a3413b5c4d8bba4e12a`
- `skills/repo-context-ledger/references/verification-presets.md` — `sha256:0650fa160e9a46a3b0f6cad68c8153f09614626e2046eb4acada3ab8b59e04f3`
- `tests/test_runtime_build.py` — `sha256:0059d7b363ceb71d9d25830aa2eefa19d8e10d2979a806be4fcec9e29ccf6a8e`
- `tests/test_repository_reliability.py` — `sha256:16d05703c805a7b0f7b88d74b6023274d45cdd64e2bb138d19608a60aea63f3e`
- `tests/test_lock_and_preset_trust.py` — `sha256:4efb34f5c3d2de6d8ea226fa570d66399061e7497d1e8b84fd3acfcfa0ab1e5d`
- `tests/test_protocol_schemas.py` — `sha256:ee28283b2ace2f73e0e674e53abb97fa0a7952c1bd961a7d6022cb0a5f8ec59b`
- `tests/test_ledger.py` — `sha256:8f5041ab68473240b1e6cf571c3fe31df732a09110ccd48475a9236ca1cd3f70`
- `ARCHITECTURE.md` — `sha256:b06788c0dc2e1ae5bf2f5292d3fda91e3876ebc2395976655f29dab5aeafcdd5`
- `SECURITY.md` — `sha256:e3bae6d08d032d2b56bc23ad9571b3dc94f0e81502f802b484aa031634e4734c`
- `THREAT_MODEL.md` — `sha256:3ff1f8795c87223a7b3c8d03ad714150c135571bfa458de039e10756739e3575`
- `.github/workflows/test.yml` — `sha256:50080dc86a7cbcf0c17fefe15766a65dc73fd78935ccd576c48116709f1add11`
<!-- repo-context-ledger:pack-files:end -->
