# Pack Health and Doctor context pack

Status: current
Feature: pack-health-doctor
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 978493f3a7bd73354eb164a0ad6d07df8a68b9fc
Base branch: main
Base commit: b5086a53c21962593ada4a0b96903faf10a7e54c
Last refreshed: 2026-08-22T00:41:03+08:00

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

- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:749a0e9e21aaeb2aa30458d4e6362093f378cd686fbe15eb388fab38e2bf4095`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:78e661a3e3191382b3de4fc92116ebb96bddca6e1e13bbdae390c4bbfd0317fe`
- `tests/test_doctor.py` — `sha256:a5003dbdfe5bf7205d87fa78f3f505f5dbb60f09c3e5f3ff6113916d55b14316`
<!-- repo-context-ledger:pack-files:end -->
