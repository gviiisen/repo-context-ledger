# Verification presets context pack

Status: current
Feature: verification-presets
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 44630d3805a54ae02184131497c715d64fa88e5a
Base branch: main
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Last refreshed: 2026-09-08T00:14:50+08:00

## Purpose

Verification presets let a repository review a repeated check once as structured executable arguments, then let any Agent select it by name. The runtime resolves platform, repository-relative working directory, timeout, and sensitivity before invoking the executable directly and attaching the result to the selected private task session.

Choose one acceptance goal per invocation, not one wrapper per helper. Optional bounded step annotations retain failed/not-run details without replacing the aggregate exit-code gate. Private timings distinguish actual subprocess work from preparation, recording, and total Ledger overhead. A tested optional `skills/repo-context-ledger/assets/verify-change.py` example groups serial acceptance only; normal operations and deployment remain outside that helper.

## Load order

- Read first: `docs/specs/verification-presets.md`, then `src/repo_context_ledger/runtime.py.tmpl::normalize_verification_config`, `resolve_verification_preset`, and `record_verification`.
- Read if needed: `skills/repo-context-ledger/references/verification-presets.md` for project configuration examples; `tests/test_ledger.py` verification-preset cases for executable behavior and failure contracts; `src/repo_context_ledger/constants.pyfrag` for version, timeout, platform, and key limits.
- Do not load by default: Context routing, Pack lifecycle, README derivation, sharing grants, and local-config finish internals unless the requested change crosses those boundaries.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::normalize_verification_config` | Canonicalizes and rejects unsafe or malformed Git-tracked preset definitions during config loading. |
| `src/repo_context_ledger/runtime.py.tmpl::resolve_verification_preset` | Fails closed for an unknown name, unsupported platform, repository escape, or missing working directory before execution. |
| `src/repo_context_ledger/runtime.py.tmpl::record_verification` | Executes argv without a shell and records sanitized evidence under short session locks. |
| `src/repo_context_ledger/runtime.py.tmpl::run_main` | Keeps preset, direct argv, and not-run selection mutually exclusive and applies timeout/sensitivity precedence. |
| `skills/repo-context-ledger/references/verification-presets.md` | Defines the user-facing schema and safe Python, Go, and PowerShell `-File` patterns. |

## Contracts and boundaries

- Invariants and contracts: Presets are explicit-only argv arrays, run with `shell=False`, stay within repository `cwd`, and cannot weaken a configured sensitive check. Initialization, routing, and finish never auto-run them; direct `verify -- <program> <args...>` remains supported.
- Failure / recovery: Invalid preset configuration and selection fail before starting a subprocess. Missing executables and command failures use the normal failed-verification record, leaving the private handoff available for repair and retry.
- Non-goals: Presets do not carry secrets or environment variables, infer which tests are sufficient, replace CI or project-native scripts, or turn shell command strings into a safe task runner.

## Verification

`python -B -m unittest discover -s tests -p test_ledger.py -k verification_preset -v` covers argv/cwd execution, normalized defaults, sensitive persistence, platform isolation, mutually exclusive selection, and shell-string rejection. `python scripts/build_runtime.py --check` proves generated runtime parity. `python -m unittest discover -s tests -v` exercises integration and compatibility contracts.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Verification presets](../../specs/verification-presets.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `.context-ledger/config.json` — `sha256:b70099d1d5911cc7edb1c3aefa182effb46314e5746f4b9c4318f9ed147cb4e8`
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:c01e9bee65a2e168ee22d0a8e1fe5b1b7686f61c7cd4320d17cbfb25f1c6ccf4`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:1d78f4e2545641efce1a3ef6db9948769ec39cfd530d795a4727a3c7214dcd7f`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:12ae39362268ec7c1c2e27d4a4d73ee1ffd0beecc1509f7b3d7f234db412463e`
- `skills/repo-context-ledger/SKILL.md` — `sha256:5ded6a55fcd32c9cd6ae07eef809b7c33a9c158fdc13a26b70752eb3288a3e69`
- `skills/repo-context-ledger/references/verification-presets.md` — `sha256:0e0e1a36b87590d36f9e2b75ea12f25599baf4ff5c500b951d3f74ebbc0be87a`
- `tests/test_ledger.py` — `sha256:8f5041ab68473240b1e6cf571c3fe31df732a09110ccd48475a9236ca1cd3f70`
- `skills/repo-context-ledger/assets/verify-change.py` — `sha256:fa08a967a74466e4cc69560d82aa147851bf929a0c30d0cd2f05f95923753a44`
- `tests/test_verification_boundaries.py` — `sha256:3b74053613339fc0d38d44d433660c0dd6b4a95bdec0400098b4883cd8fb8f0a`
<!-- repo-context-ledger:pack-files:end -->
