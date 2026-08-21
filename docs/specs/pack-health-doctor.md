# Pack Health and Doctor

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-08-21

## Purpose and behavior

`doctor` gives people and automation one bounded, deterministic view of repository health before they choose a repair task. It observes configuration, runtime installation, native Agent adapters, the Context Manifest, private task-state structure, Context Pack lifecycle and fingerprints, local documentation links, and shared derived-file safety without modifying repository or private state.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::doctor_repo` | Builds and renders the `doctor-v1` report and determines the exit class. |
| `skills/repo-context-ledger/scripts/ledger.py::doctor_pack_findings` | Groups Pack freshness, missing files, duplicate features, overlap, and explicit lineage findings. |
| `tests/test_doctor.py` | Locks the public report schema, bounded output, read-only behavior, privacy boundary, and lifecycle rules. |

## Data flow and contracts

- Input: the selected repository, live `.context-ledger/config.json`, enabled Agent adapters, current Manifest and documentation, current worktree-private task state, Context Pack metadata and tracked file contents, Git branch, and `--max-items` between 1 and 100.
- Flow: the command loads live repository files without using or writing the router cache, groups deterministic conditions into findings, bounds every item list, computes severity counts, and renders text or JSON from the same report object.
- Persistence / dependencies: Doctor uses only the Python standard library, repository files, Git metadata, and read-only Git commands. It creates no cache, lock, session, fingerprint, file, or derived index and changes no timestamps through an explicit write.
- Output: each finding has a stable code, severity, repository-relative scope, summary, bounded details, and suggested actions. JSON uses `doctor-v1`; text is a projection of the same report. `pass`, `warning`, and `repairable` return exit code 0, while any `error` returns exit code 2. Diagnostic text redacts repository, temporary, Codex-home, and user-home roots.

## Boundaries and failure modes

- Invariants: Doctor never rewrites files, refreshes a fingerprint, changes Pack status, infers semantic replacement, cleans a private session, or regenerates derived indexes. Every public path stays repository-relative and detail counts remain accurate when items are omitted.
- Permissions / concurrency: Doctor does not inspect or report foreign private session fields and uses no repository write lock because it never writes. A concurrent writer may make observations momentarily stale, so repair commands must revalidate their own preconditions rather than treating a Doctor report as a lock or lease.
- Failure / recovery: invalid configuration and invalid private state become redacted structured errors instead of uncaught command failures. Missing tracked files, stale fingerprints, adapter/Manifest drift, broken links, and orphan reservations remain visible as repair plans; recovery occurs only through a separately reviewed command or code change.
- Non-goals: Doctor does not judge business semantics, become a release gate by itself, contact another task, clean historical debt, auto-supersede Packs, or replace focused `check`, `team-check`, and executed tests.

A `superseded` Pack must identify its replacement. A `current` Pack must not claim it is superseded. The replacement may be an existing feature ID or repository-relative Pack path. Two current Packs may intentionally track a shared file, so overlap alone is a warning. Duplicate current feature IDs and an explicit `Superseded by` target that cannot be resolved are errors. Lifecycle repair remains a reviewed human/Agent action because shared code scope does not prove that one feature replaces another.

## Verification

Run `python -m unittest discover -s tests -p test_doctor.py` for the focused health and privacy suite. Run `python -m unittest discover -s tests -v` plus the Skill validator before release.

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Build Pack health diagnostics and lifecycle governance](../changes/2026/08/20260821230730-gviiisen-4c00275b82-build-pack-health-diagnostics-and-lifecycle-gove.md)
<!-- repo-context-ledger:changes:end -->
