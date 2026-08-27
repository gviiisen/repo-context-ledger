# Compatibility

Repo Context Ledger ships a zero-dependency Python runtime and a vendor-neutral Agent Skill.

## Supported environments

- Python 3.10 through 3.12.
- Windows and Ubuntu are exercised in the required push/PR CI matrix. macOS is exercised for release tags, scheduled runs, and manually dispatched validation.
- Git repositories are the supported collaboration environment. Non-Git directories keep a local fallback state but cannot provide branch/worktree isolation or PR checks.
- Codex, Claude Code, Cursor, GitHub Copilot, Grok, and other tools may use the same Git-tracked Pack/spec/Change knowledge. Vendor-private Memory is outside the compatibility contract.

## CLI compatibility

Minor releases preserve existing command names, arguments, text-mode exit classes, repository schema migrations, and published JSON schema names. New optional fields and new commands may be added in a minor release. Automation must ignore unknown JSON fields and must select JSON explicitly with `--format json`.

The v1.0 contract freezes the listed schema names, required fields, documented scalar types, and exit classes for the 1.x line. Draft 2020-12 declarations live in `schemas/` and are exercised against real CLI output. Extension objects remain open so minor releases can add optional detail without forcing a new protocol.

The stable JSON contracts are:

| Command | Schema | Purpose |
| --- | --- | --- |
| `plan --format json` | `workflow-plan-v1` | Read-only workflow classification and structured next action. |
| `context --format json` | `context-bundle-v1` | Bounded context route and optional Resume Capsule. |
| `context --format json` → `resume.capsule` | `resume-capsule-v2` | Private, bounded continuation guidance for an owned task. |
| `doctor --format json` | `doctor-v1` | Read-only health findings and repair suggestions. |
| `status --format json` | `status-v1` | Privacy-bounded session counts/details and repository inventory. |
| `check --format json` | `check-v1` | Existing check result projected into separated messages and errors. |

Exit classes are `0` for success, `1` for a valid query with no context match, and `2` for invalid input, an unhealthy required contract, or a failed gate. A future incompatible field removal, meaning change, or exit-class change requires a new JSON schema name and a major project version.

Starting in v0.8.0, an owned continuation may include an additive `resume-capsule-v2` object under `context-bundle-v1.resume.capsule`. Every pre-v0.8 Capsule field remains present; v2 adds structured guidance fields. Consumers must continue to ignore unknown fields, and a missing Capsule remains valid for no-match, ambiguous, or foreign-only routes.

Starting in v0.9.0, `plan --format json` publishes `workflow-plan-v1` with the stable modes `readonly`, `small-fix`, `ordinary-change`, and `resume`. Its `next_action.argv` is data, not a shell command, and the planner never executes it. When `requires_confirmation` is true, `next_action.kind` is `clarify` and `argv` is empty. `context-bundle-v1` additively includes the same object under `workflow`; existing consumers may ignore it.

Expected JSON failures remain inside the requested schema and use stable machine codes: `LEDGER_ERROR`, `INVALID_ARGUMENT`, `UNSUPPORTED_SCHEMA`, `CONTEXT_NO_MATCH`, `CHECK_FAILED`, and `DOCTOR_FAILED`. Human messages may improve without changing the code. Unknown future repository/private-state schemas fail closed with `UNSUPPORTED_SCHEMA` rather than being normalized or rewritten.

Starting in v0.8.1, a confirmed Git worktree that cannot answer a required status/diff query fails with `GIT_COMMAND_FAILED`. This is an additive error code within the existing schemas and exit class 2. Git path readers use NUL-delimited byte output, so filenames are interpreted by the operating-system filesystem codec rather than Git's display quoting. Genuine non-Git directories retain their local fallback behavior.

Starting in v0.8.2, an untrusted or changed verification preset fails before execution with `PRESET_TRUST_REQUIRED` and exit class 2. Trust is keyed by the current local principal and the canonical normalized preset digest. It is private clone state, not a repository schema or portable Git contract. Existing direct `verify -- <command>` behavior is unchanged.

## Repository and private-state compatibility

`.context-ledger/config.json` and private task state currently use schema v8. `init --dry-run` must preview the same migration plan as real `init`. Git-tracked Packs, specs, and completed Changes remain readable across minor releases. Private active/paused state remains local to the clone/worktree and is not a portable Git contract.

`config.verification.presets` is an optional v8 field added in v0.7.3. Presets are explicit executable argument arrays with bounded metadata; they never execute during initialization, routing, checking, or finishing. Existing direct `verify -- <command>` calls remain compatible.

Context Pack `Aliases` are optional Git-tracked metadata added in v0.8.0. Existing Packs without the field behave as before. Aliases are explicit phrases only; upgrade and routing never generate translations or infer private task state.

The initialized `.context-ledger/ledger.py` is a standalone artifact. Its version should match the installed Skill runtime after `init`; the repository does not require a Python package installation or API key.

Source contributors may edit ordered build fragments, but installed repositories continue to receive one byte-complete `ledger.py`. The schema files and source fragments are development/review assets and are not imported by that runtime.

Atomic rewrites preserve the permission mode of an existing target on Unix-like systems. Newly created Git-tracked documents and configuration use `0644`; private session, state, cache, and preset-trust files use `0600`; copied runtime files preserve their source mode. This does not add a cross-platform promise for Windows ACL inheritance or ownership metadata.
