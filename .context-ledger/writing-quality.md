# Evidence-first writing quality

Apply this standard only to records with `Quality profile: evidence-v1`. Preserve legacy records unless the task explicitly upgrades them.

## Language

- Honor `Language` metadata: `en`, `zh-CN`, or `auto`.
- For `auto`, follow the predominant language of nearby repository documentation; if no pattern exists, follow the user's language.
- Keep paths, symbols, commands, protocol fields, error text, and identifiers in their source form. Do not translate them.
- Use one primary natural language per document. Quote another language only when it is part of an interface or evidence.

## Evidence rules

- Derive changed paths from the ledger evidence block and `git diff`, not memory.
- Cite concrete paths in backticks. Add the relevant class, function, route, job, or configuration key when known.
- Separate inspected fact from inference. Write `Unknown` or an open question when evidence is missing.
- Record only commands actually executed through `ledger.py verify`. Never convert an intended check into a reported result.
- Avoid unsupported claims such as “all edge cases are covered,” “fully compatible,” or “tests pass” without attached evidence.
- Reject vague standalone text such as “updated relevant files,” “fixed the logic,” or “修改了相关代码.” Replace it with an observable behavior, path, and boundary.

## Purpose-specific forms

### Handoff: chronological change evidence

- State intent and acceptance outcome.
- Describe observable `Before` and `After` behavior.
- Map changed paths and symbols to their responsibility and actual change.
- Record invariants, failure/recovery behavior, and what deliberately did not change.
- Keep verification results in the managed checks block.
- List documentation updated, or write `None — <reason>`.
- Preserve unresolved uncertainty under Open questions.

### Stable spec: current truth

- Describe the merged behavior as it exists now; do not narrate the implementation history.
- Map entry points and ownership, then show input → processing → persistence/dependency → output.
- State contracts, permissions, validation, concurrency/idempotency rules, failure modes, and recovery only when they apply.
- Link history through the managed related-changes block instead of copying handoff prose.

### Context Pack: minimal loading route

- Keep it shorter than the configured maximum.
- Separate `Read first`, `Read if needed`, and `Do not load by default`.
- Track the smallest useful set of files. Do not turn the pack into a second spec.
- Prefer navigation facts, boundaries, and reliable diagnostic commands over implementation narration.

## Detail levels

- `concise`: record the minimum evidence needed to resume safely.
- `standard`: cover the main flow, contracts, failure behavior, and focused verification.
- `detailed`: add justified secondary flows and operational boundaries; do not repeat source code.

More detail never relaxes the requirement for concrete evidence.
