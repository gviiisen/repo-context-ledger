# Verification presets context pack

Status: current
Feature: verification-presets
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 2c5ea2f81b7b8f8939ad274f44094a6b937faca5
Base branch: main
Base commit: 0d7e1f289e726edc4ae2b621361f89c621de5623
Last refreshed: 2026-08-27T19:05:08+08:00

## Purpose

Verification presets let a repository review a repeated check once as structured executable arguments, then let any Agent select it by name. The runtime resolves platform, repository-relative working directory, timeout, and sensitivity before invoking the executable directly and attaching the result to the selected private task session.

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
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:6552c343fb986f841042fae89716668ad7612165eaf594b7bb6f0bd8022e57aa`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:e4b8e16789bce7ba8e405f0069f0372dd0ff25fcbfd9dc805cb460b0fbe5a62a`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:0bfead16d1f3312ac8a0eacbb907905be4159c123f85f96dab4bc7ed4e0c985a`
- `skills/repo-context-ledger/SKILL.md` — `sha256:c49a692005ff85c62c4fc3ebb5617af4725c55bba3857a3413b5c4d8bba4e12a`
- `skills/repo-context-ledger/references/verification-presets.md` — `sha256:0650fa160e9a46a3b0f6cad68c8153f09614626e2046eb4acada3ab8b59e04f3`
- `tests/test_ledger.py` — `sha256:7944c012f406e8c8dabe7946a07f6477a886515104e53b2de9c8497162bfc65e`
<!-- repo-context-ledger:pack-files:end -->
