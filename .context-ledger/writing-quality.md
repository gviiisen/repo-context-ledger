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

For a new `--workflow small-fix` draft, the runtime replaces the repeated path table with a free-form change explanation and generates only the `Updated` documentation list. Fill the nine authoring prompts with task-specific facts, including what each meaningful change does and why, its repository-relative file/symbol references, and why documentation changed or remains correct. Coupled files may share one explanation; boundaries and recorded verification may be referenced rather than restated. There is no fixed number of change items or artificial word cap. A changed-path list is not a change explanation, and "no documentation path changed" does not explain why no update is needed.

The `small-fix-explained-v1` record marker adds mechanical checks for prose beyond a path list and references to every implementation evidence path (or every evidence path when no implementation path exists). File/symbol references must use the exact repository-relative evidence path; a shared basename is ambiguous. These checks cannot prove the correctness of the explanation or detect every omitted behavior change in one file. Reconcile the actual diff against the record before finish; expand the same draft to ordinary work if there are independent behavior changes, high-risk boundaries, or uncertainty.

Archive once does not mean write only at the end. Preserve a changed diagnosis, key design decision, rejected approach that explains a boundary, or useful failure cause in the same private draft when discovered. An optional Decisions section can hold such notes; shared Verification already retains executed attempts. Before switching context, checkpoint the current result and next step without overwriting the reasoning already in the body. Do not record every command, duplicate raw logs, or keep irrelevant troubleshooting noise. Preserve uncertainty instead of converting it into confirmed behavior during final cleanup.

Example for one coupled fix:

```markdown
## Code paths

- `src/service.py::VALUE` reads `src/defaults.py::DEFAULT` so the exported value and shared default cannot drift. The import contract and verification below apply to both files.

## Documentation updates

Updated: Generated from scoped documentation paths at finish.
Reason: The usage guide states this default, so its example must match the corrected value; installation steps remain unchanged.
```

If the record grows beyond a known small boundary, expand its explanations and set `Workflow: ordinary-change` and `Detail: standard` in the same draft. Retain its existing sections, decisions, format marker, and managed checks. Do not start a replacement session or remove evidence to get past a gate. Existing completed records without the new marker keep their historical validation contract; old unfinished path-only short drafts must add explanations before publication.

### Stable spec: current truth

- Describe the merged behavior as it exists now; do not narrate the implementation history.
- Map entry points and ownership, then show input → processing → persistence/dependency → output.
- State contracts, permissions, validation, concurrency/idempotency rules, failure modes, and recovery only when they apply.
- Link history through the managed related-changes block instead of copying handoff prose.

### Context Pack: minimal loading route

- Keep it shorter than the configured maximum.
- Separate `Read first`, `Read if needed`, and `Do not load by default`.
- Track the smallest sufficient set of validity dependencies. Optional navigation can use `pack --reference` and Reading references; it does not count toward Coverage. Do not demote a real dependency merely to avoid stale warnings. Do not turn the pack into a second spec.
- Prefer navigation facts, boundaries, and reliable diagnostic commands over implementation narration.

## Detail levels

- `concise`: record the minimum evidence needed to resume safely.
- `standard`: cover the main flow, contracts, failure behavior, and focused verification.
- `detailed`: add justified secondary flows and operational boundaries; do not repeat source code.

More detail never relaxes the requirement for concrete evidence.
