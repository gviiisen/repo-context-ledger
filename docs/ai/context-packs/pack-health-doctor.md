# Pack Health and Doctor context pack

Status: current
Feature: pack-health-doctor
Aliases: none
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 2c5ea2f81b7b8f8939ad274f44094a6b937faca5
Base branch: main
Base commit: 0d7e1f289e726edc4ae2b621361f89c621de5623
Last refreshed: 2026-08-27T19:05:05+08:00

## Purpose

Routes repository health work to the deterministic Doctor report instead of forcing an Agent to read every Pack or repeat every stale path. The report exposes bounded repair decisions while leaving repository files, private sessions, fingerprints, and Pack lineage unchanged.

## Load order

- Read first: Read `docs/specs/pack-health-doctor.md`, then the relevant `doctor_*` function in `skills/repo-context-ledger/scripts/ledger.py`.
- Read if needed: Read `tests/test_doctor.py` when changing finding codes, severities, exit behavior, lifecycle rules, privacy, or output bounds.
- Do not load by default: Do not load completed Changes, router implementation, or unrelated lifecycle commands for a Doctor-only change.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::doctor_repo` | Builds one `doctor-v1` report, renders text or JSON, and returns the stable exit class. |
| `skills/repo-context-ledger/scripts/ledger.py::doctor_pack_findings` | Aggregates Pack freshness, missing files, overlaps, duplicate features, and explicit lineage. |
| `tests/test_doctor.py` | Defines read-only, privacy, bounded-output, lifecycle, and compatibility examples. |

## Contracts and boundaries

- Invariants and contracts: Doctor reads live state without using the router cache, never inspects or reports foreign private session fields, emits repository-relative bounded details, never auto-supersedes overlapping Packs, and keeps `doctor-v1` stable for automation.
- Failure / recovery: invalid configuration or private state becomes a redacted structured error; stale, missing, drifted, and broken-link debt remains visible as a suggested repair plan instead of being changed automatically.
- Non-goals: Doctor does not repair files, clean sessions, refresh fingerprints, rewrite Pack status or lineage, regenerate derived indexes, or judge business semantics.

## Verification

`python -m unittest discover -s tests -p test_doctor.py` verifies the versioned report, bounded grouping, read-only behavior, privacy, overlap, and explicit lineage. `python -m unittest discover -s tests -v` protects the wider lifecycle before release.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Pack Health and Doctor](../../specs/pack-health-doctor.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:6552c343fb986f841042fae89716668ad7612165eaf594b7bb6f0bd8022e57aa`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:0bfead16d1f3312ac8a0eacbb907905be4159c123f85f96dab4bc7ed4e0c985a`
- `tests/test_doctor.py` — `sha256:84526dcc76e8bc08fcc4888763426729c8e73db4c6c70242abeecd763fcad8bd`
<!-- repo-context-ledger:pack-files:end -->
