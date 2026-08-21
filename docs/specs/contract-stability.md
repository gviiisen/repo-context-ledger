# Contract Stability

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-08-21

## Purpose and behavior

Contract Stability keeps automation and initialized repositories safe across minor releases. Existing human-readable commands remain usable, while automation selects explicit versioned JSON for context routing, health, status, and checks. Golden fixtures and a synthetic routing corpus make accidental field, schema, exit-class, and selection drift visible before release.

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::status_report` | Produces privacy-bounded `status-v1` data without machine-local state paths. |
| `skills/repo-context-ledger/scripts/ledger.py::captured_command_json` | Projects existing check behavior into `check-v1` while preserving its exit code. |
| `tests/test_contract_stability.py` | Verifies JSON schemas, required fields, privacy, exit classes, and synthetic route selection. |
| `tests/golden/v0.6.2-cli-contract.json` | Records public schema names, required fields, and exit classes. |
| `.github/workflows/test.yml` | Exercises Windows/Ubuntu and supported Python boundary versions. |

## Data flow and contracts

- Input: existing CLI arguments, current repository/configuration/state, an explicit `--format json` request, golden contract fixtures, and fully synthetic routing cases.
- Flow: status builds a dedicated structured report; check captures its existing text operation in memory and separates ordinary messages from errors; tests compare stable schema identifiers/fields and evaluate synthetic Pack scores.
- Persistence / dependencies: JSON projections write no new state. Golden and routing fixtures are Git-tracked test inputs with no production paths, names, sessions, commits, or logs. Runtime support remains Python 3.10+ standard library only.
- Output: `status-v1` contains repository branch/default, principal, privacy-bounded owned/shared/foreign session data, and inventory. `check-v1` contains command, success flag, unchanged exit code, messages, and errors. `context-bundle-v1` and `doctor-v1` retain their existing contracts.

## Boundaries and failure modes

- Invariants: minor releases do not remove existing commands or required JSON fields, change documented field meanings, expose absolute machine paths, or change exit classes. Automation must ignore additional optional fields.
- Permissions / concurrency: status exposes details only for owned or explicitly shared sessions and only a count for foreign sessions. JSON projection does not grant access or lock repository writers.
- Failure / recovery: a contract fixture or routing evaluation failure blocks release until the change is made additive or receives a new schema and major-version migration. Text output remains the human recovery path when JSON consumers are unavailable.
- Non-goals: this version does not freeze every prose sentence, promise byte-identical timing metrics, support Python below 3.10, export vendor Memory, or turn synthetic routing cases into business-semantic tests.

## Verification

Run `python -m unittest discover -s tests -p test_contract_stability.py` for contract and routing evaluation. Required GitHub CI runs the complete suite on Windows and Ubuntu with Python 3.10 and 3.12.

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Stabilize CLI contracts and compatibility matrix](../changes/2026/08/20260821232648-gviiisen-09ef2502eb-stabilize-cli-contracts-and-compatibility-matrix.md)
<!-- repo-context-ledger:changes:end -->
