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

## Rollback

Keep the prior Skill installation or release artifact until the upgraded repository passes its checks. Repository file changes are ordinary Git changes and should be reviewed or reverted through Git. Private state is not committed; back it up separately before a state-schema migration when an active task cannot be recreated safely.

Do not copy an older standalone runtime over a newer migrated private state and assume compatibility. Restore the matching private-state backup or finish/pause work with the runtime that performed the migration first.

## Schema changes

Minor releases may add optional JSON fields and migrate older repository state forward while preserving documented behavior. A removal, incompatible meaning change, or exit-class change requires a new public schema name and a major project version. Migration code must be exercised on both Windows and Ubuntu and on the minimum supported Python version.
