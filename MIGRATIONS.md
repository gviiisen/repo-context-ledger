# Migrations

## Upgrade

1. Install the intended Skill release.
2. Run its runtime with `--repo <repository> init --dry-run` and review creates, managed-block changes, deletions, and state migrations.
3. Run the same `init` without `--dry-run` only when the preview matches the intended repository scope.
4. Confirm the installed and repository runtimes report the same version.
5. Run `adapters check`, `manifest check` on the default branch, `doctor`, and the repository's focused verification.

Initialization preserves prose outside managed markers, existing completed Changes, custom documentation roots, mature month layouts, and private session drafts. Feature branches continue to defer shared Manifest, README, and monthly-index regeneration.

v0.7.3 adds an empty `verification.presets` object to normalized configuration. Upgrade does not infer commands from package manifests and never executes a preset. Add reviewed presets only for repeated checks, and keep secrets or machine-specific absolute paths out of Git-tracked configuration.

v0.8.0 does not change repository/private-state schema v8 or replace `context-bundle-v1`. Existing Context Packs remain valid without `Aliases`. Add repeated `pack --alias "<human phrase>"` values only when a team needs cross-language or colloquial routing, and keep the Pack code map's existing `path::Symbol` entries accurate. Resume Capsule v2 is generated on demand; no Capsule file or inferred task state is migrated or committed.

v0.8.1 does not change repository/private-state schema v8 or any published JSON schema. Re-run `init` to refresh the standalone runtime. Existing executable/read-only permission bits are preserved when an existing file is atomically replaced on Unix-like systems. No history, Pack, spec, completed Change, or private session migration is required.

v0.8.2 does not change repository/private-state schema v8 or public JSON schema names. Re-run `init` to refresh the standalone runtime. Existing legacy write locks are diagnosed as invalid metadata and are never auto-removed. The first explicit use of each verification preset now requires reviewing its normalized configuration and repeating the command with the printed `--trust-digest`; this principal-local trust state is created outside Git and can be discarded safely.

v0.9.0 does not change repository/private-state schema v8. Re-run `init` to refresh the standalone runtime and native Agent adapters. The new `plan` command and `workflow-plan-v1` schema are additive; `context-bundle-v1` consumers must continue to ignore unknown fields. Existing `start` calls default to `ordinary-change`, while new integrations should call `plan` first and require confirmation when the returned plan says so.

v1.0.0 does not change repository/private-state schema v8, private session ownership, or the installed single-file shape. Re-run `init` to replace the repository runtime. Source-only fragment paths and `schemas/*.schema.json` are contributor/integration assets; initialized application repositories do not need to copy them. Integrations already using the documented v1 schemas require no payload migration and must continue to ignore unknown optional fields.

v1.0.1 does not change repository/private-state schema v8 or any published JSON schema. Re-run `init` to replace the standalone runtime and native adapters. Existing files retain their mode; newly created public repository files use `0644` on POSIX, while private session, state, cache, and preset-trust files use `0600`. Existing integrations may observe additive `--tool` arguments in `workflow-plan-v1.next_action.argv` when the caller supplied a tool.

v1.0.3 includes the previously unreleased v1.0.2 policy/audit work. Repository/private-state schema v8 and public JSON schema names remain unchanged. New short drafts carry the additive small-fix-explained-v1 marker and need an actual change explanation and documentation rationale; existing completed records are not rewritten. Refresh the Skill and native adapters to use delta-first Agent guidance.

Runtime mode defaults to bundled. Explicit `init --runtime global --dry-run` previews a normal init using a forwarding entry; inspect the full plan before applying it. A mature repository that must preserve every document and private-state byte can instead follow the targeted migration in `skills/repo-context-ledger/references/global-runtime.md`. Global mode requires the Skill on each machine and must not silently fall back to a stale local runtime. Installing a global update changes the next executable invocation, not already-loaded Agent instructions.

PR workflows may use `policy --base <ref>` instead of separate team, changed-scope Coverage and diff gates. Optional historical dispositions under docs/audit-dispositions record an existing later resolution; never invent an approval or alter a failed historical result to satisfy a release gate.

## Rollback

Keep the prior Skill installation or release artifact until the upgraded repository passes its checks. Repository file changes are ordinary Git changes and should be reviewed or reverted through Git. Private state is not committed; back it up separately before a state-schema migration when an active task cannot be recreated safely.

Do not copy an older standalone runtime over a newer migrated private state and assume compatibility. Restore the matching private-state backup or finish/pause work with the runtime that performed the migration first.

## Schema changes

Minor releases may add optional JSON fields and migrate older repository state forward while preserving documented behavior. A removal, incompatible meaning change, or exit-class change requires a new public schema name and a major project version. Migration code must be exercised on both Windows and Ubuntu and on the minimum supported Python version.
