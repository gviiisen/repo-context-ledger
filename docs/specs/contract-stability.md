# Contract Stability

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-08-28

## Purpose and behavior

Contract Stability keeps automation and initialized repositories safe across the 1.x line. Existing human-readable commands remain usable, while automation selects explicit versioned JSON for planning, context routing, health, status, and checks. Published Draft 2020-12 schemas, golden fixtures, and a synthetic routing corpus make accidental field, type, schema, exit-class, and selection drift visible before release.

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::status_report` | Produces privacy-bounded `status-v1` data without machine-local state paths. |
| `skills/repo-context-ledger/scripts/ledger.py::captured_command_json` | Projects existing check behavior into `check-v1` while preserving its exit code. |
| `tests/test_contract_stability.py` | Verifies JSON schemas, required fields, stable error codes, privacy, and exit classes. |
| `scripts/evaluate_routing.py` | Measures labeled synthetic routing accuracy, ambiguity/fallback behavior, lifecycle selection, read characters, and latency. |
| `tests/test_routing_evaluation.py` | Locks the routing evaluation report and expected corpus outcomes. |
| `tests/golden/v0.6.2-cli-contract.json` | Records public schema names, required fields, and exit classes. |
| `schemas/*.schema.json` | Publishes the stable top-level required fields, scalar types, enums, and open extension boundaries for every public JSON protocol. |
| `tests/test_protocol_schemas.py` | Executes real CLI reports and checks them against the published protocol declarations. |
| `.github/workflows/test.yml` | Exercises Windows/Ubuntu on pushes and PRs, runs PR-specific Ledger team/Coverage/diff gates from full Git history, and runs macOS on releases, schedules, and manual dispatch. |
| `skills/repo-context-ledger/scripts/ledger.py::load_historical_dispositions`, `audit_history` | Validate immutable recorded outcomes separately from hash-bound maintainer resolutions. |

## Data flow and contracts

- Input: existing CLI arguments, current repository/configuration/state, an explicit `--format json` request, published schema documents, golden contract fixtures, and fully synthetic routing cases. Optional additive configuration such as `verification.presets` must preserve repositories that omit it and existing direct `verify -- <argv>` callers.
- Flow: planning and status build dedicated reports; context, doctor, and check preserve their existing JSON projections and errors; `audit --history --policy as-recorded` validates original Change structure without rewriting a genuine recorded failure, while `--fail-on unresolved` requires a valid hash-bound disposition for each known finding; tests execute real commands and recursively compare declared required fields, types, arrays, constants, and enums with Draft 2020-12 declarations, then evaluate the labeled synthetic Pack corpus.
- Persistence / dependencies: JSON projections write no new state. Schemas, golden files, and routing fixtures are Git-tracked integration/test inputs with no production paths, names, sessions, commits, or logs. The standalone runtime does not load a schema library and remains Python 3.10+ standard-library only.
- Output: `workflow-plan-v1`, `context-bundle-v1`, its nested `resume-capsule-v2`, `doctor-v1`, `status-v1`, and `check-v1` each publish stable required fields. Extension objects remain open for additive minor-version detail; incompatible removal, meaning, scalar-type, or exit-class changes require a new protocol and major version.

## Boundaries and failure modes

- Invariants: 1.x minor releases do not remove existing commands or required JSON fields, change documented field meanings or scalar types, narrow stable enums incompatibly, expose absolute machine paths, or change exit classes. Automation must ignore additional optional fields. A historical disposition names one current finding, binds the exact original Change bytes with SHA-256, and references a later completed Change; editing the original record invalidates the disposition.
- Permissions / concurrency: status exposes details only for owned or explicitly shared sessions and only a count for foreign sessions. JSON projection does not grant access or lock repository writers.
- Failure / recovery: a published-schema, contract fixture, or routing evaluation failure blocks release until the implementation becomes compatible or receives a new schema and major-version migration. Text output remains the human recovery path when JSON consumers are unavailable.
- Non-goals: this version does not freeze every prose sentence, promise byte-identical timing metrics, support Python below 3.10, export vendor Memory, or turn synthetic routing cases into business-semantic tests.

## Verification

Run `python tests/test_protocol_schemas.py`, `python -m unittest discover -s tests -p test_contract_stability.py`, `python -m unittest discover -s tests -p test_routing_evaluation.py`, and `python -m unittest discover -s tests -p test_policy_and_audit.py`. Required GitHub CI runs the complete suite on Windows and Ubuntu with Python 3.10 and 3.12; release/nightly/manual validation also runs on macOS.

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Add ledger policy and historical dispositions](../changes/2026/08/20260827233705-gviiisen-a9641a2f72-add-ledger-policy-and-historical-dispositions.md)
- [Cover public protocol error shapes](../changes/2026/08/20260827191239-gviiisen-eaffca7e21-cover-public-protocol-error-shapes.md)
- [Add safe verification presets](../changes/2026/08/20260827065951-gviiisen-6daa4a6c38-add-safe-verification-presets.md)
- [Harden raw JSON command detection](../changes/2026/08/20260822002738-gviiisen-9d24fbee4b-harden-raw-json-command-detection.md)
- [Complete outer JSON error boundary](../changes/2026/08/20260822001817-gviiisen-3767cb15f0-complete-outer-json-error-boundary.md)
- [Close contract and privacy review gaps](../changes/2026/08/20260821235319-gviiisen-450163105c-close-contract-and-privacy-review-gaps.md)
- [Stabilize CLI contracts and compatibility matrix](../changes/2026/08/20260821232648-gviiisen-09ef2502eb-stabilize-cli-contracts-and-compatibility-matrix.md)
<!-- repo-context-ledger:changes:end -->
