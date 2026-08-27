# Verification presets context pack

Status: current
Feature: verification-presets
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 45055d81262efa4ef1ec627ac22e578fb1be61d3
Base branch: main
Base commit: 45055d81262efa4ef1ec627ac22e578fb1be61d3
Last refreshed: 2026-08-27T08:19:59+08:00

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
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:8dbccc54b87e0dfd05f93edadc3f716ac4873450d1e240801ebfa2101f1ca9f5`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:bdfac50c0e0f2aa013c6f73e1ca259921559e999e715924994411dc9fad855c4`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:c72b923b0c5f1cd758e5771e914e150f9bc885a2ba176410287c077804645007`
- `skills/repo-context-ledger/SKILL.md` — `sha256:3b1e2c2b42ff57f3b9828d6f86394c47f9d0e0ae1f0a739750e565120027e101`
- `skills/repo-context-ledger/references/verification-presets.md` — `sha256:1be37f086638cd71b245a42931c9fe984ae51503d9948bc96bf27246286b785b`
- `tests/test_ledger.py` — `sha256:7ad70640f1331235e79c7860ea613b971b0b64991e09faf9008c0dd37f84e8f8`
<!-- repo-context-ledger:pack-files:end -->
