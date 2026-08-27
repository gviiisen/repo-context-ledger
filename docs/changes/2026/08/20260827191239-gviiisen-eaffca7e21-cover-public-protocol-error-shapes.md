# Cover public protocol error shapes

Status: completed
Feature: contract-stability
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827191239-gviiisen-eaffca7e21
Session ID: 20260827191239-gviiisen-eaffca7e21
Actor: gviiisen
Branch: feat/v1.0-modular-runtime-contracts
Started: 2026-08-27T19:12:39+08:00
Completed: 2026-08-27T19:19:48+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 2c5ea2f81b7b8f8939ad274f44094a6b937faca5
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/contract-stability.md
Spec exception: none

## Intent

Close the final public-protocol review gaps before freezing the 1.x compatibility boundary. Every published command response and the nested Resume Capsule must have a declaration that accepts real success, no-match, and error output while rejecting incompatible required-field, type, constant, array-item, and enum drift.

## Changed behavior

Before: Protocol tests checked only shallow top-level types. They sampled a no-match Context Bundle but not a successful one, so the published schema incorrectly rejected the runtime's `result: ok` and `error: null` output. The documented `resume-capsule-v2` protocol had no checked-in schema, and compatibility prose named the wrong Workflow Plan field.

After: Real success, no-match, and error responses are checked recursively for the supported Draft 2020-12 keywords. `context-bundle-v1` matches its actual success envelope, `resume-capsule-v2` has a published schema exercised against an owned private continuation, and compatibility/architecture documentation matches the runtime and build layout.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `tests/test_protocol_schemas.py::ProtocolSchemaTests` | Exercises real public JSON output against checked-in declarations. | Adds recursive validation, a successful Context Bundle, a no-match variant, error variants, and a real Resume Capsule sample. |
| `schemas/context-bundle-v1.schema.json` | Declares the stable context routing envelope. | Corrects the result enum, permits the successful null error value, and declares actual success fields. |
| `schemas/resume-capsule-v2.schema.json` | Declares private continuation guidance nested in a Context Bundle. | Freezes required Capsule fields, scalar/array types, stable enums, and budget shape while leaving additive extensions open. |
| `COMPATIBILITY.md` | Defines the 1.x consumer promise. | Lists the Capsule protocol and corrects `next_action.kind`. |
| `README.md` / `README.zh-CN.md` | Explain the release contract to users. | List all six protocols and describe recursive success/no-match/error checks. |
| `docs/specs/contract-stability.md` | Defines the stable protocol boundary. | Aligns the specification with nested Capsule coverage and recursive checks. |

## Boundaries and risks

- Invariant: The shipped runtime remains standard-library only and never loads a schema file at execution time; schemas are integration and release gates.
- Failure / recovery: A real emitted value that violates a declared supported keyword fails the protocol test with its JSON path, blocking release until code or schema is corrected deliberately.
- Not changed: Text output, command exit classes, private ownership rules, runtime serialization, and the policy that consumers ignore additive unknown fields remain unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python tests/test_protocol_schemas.py`
  - Status: passed
  - Exit code: 0
  - Duration: 4.50s
  - Recorded: 2026-08-27T19:18:54+08:00
  - Output evidence: sha256:e65c7f162b4ad900a6d688c8e0250796963615ddd084c8348c6d9b683c6f16c8 (101 characters captured; content not persisted; last=OK)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `schemas/README.md`, `README.md`, `README.zh-CN.md`, `COMPATIBILITY.md`, `ARCHITECTURE.md`, `docs/specs/contract-stability.md`, and `docs/ai/context-packs/contract-stability.md`.

Reason: The public compatibility promise must enumerate the Capsule and describe the checks that actually enforce it; architecture prose must not encode a stale fragment count.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `2c5ea2f81b7b8f8939ad274f44094a6b937faca5`
- Current commit: `2c5ea2f81b7b8f8939ad274f44094a6b937faca5`
- Changed paths:
  - `ARCHITECTURE.md`
  - `COMPATIBILITY.md`
  - `README.md`
  - `README.zh-CN.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/workflow-planning.md`
  - `docs/specs/contract-stability.md`
  - `schemas/README.md`
  - `schemas/context-bundle-v1.schema.json`
  - `schemas/resume-capsule-v2.schema.json`
  - `tests/test_protocol_schemas.py`
<!-- repo-context-ledger:evidence:end -->
