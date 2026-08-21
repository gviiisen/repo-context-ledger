# Migrations

## Upgrade

1. Install the intended Skill release.
2. Run its runtime with `--repo <repository> init --dry-run` and review creates, managed-block changes, deletions, and state migrations.
3. Run the same `init` without `--dry-run` only when the preview matches the intended repository scope.
4. Confirm the installed and repository runtimes report the same version.
5. Run `adapters check`, `manifest check` on the default branch, `doctor`, and the repository's focused verification.

Initialization preserves prose outside managed markers, existing completed Changes, custom documentation roots, mature month layouts, and private session drafts. Feature branches continue to defer shared Manifest, README, and monthly-index regeneration.

## Rollback

Keep the prior Skill installation or release artifact until the upgraded repository passes its checks. Repository file changes are ordinary Git changes and should be reviewed or reverted through Git. Private state is not committed; back it up separately before a state-schema migration when an active task cannot be recreated safely.

Do not copy an older standalone runtime over a newer migrated private state and assume compatibility. Restore the matching private-state backup or finish/pause work with the runtime that performed the migration first.

## Schema changes

Minor releases may add optional JSON fields and migrate older repository state forward while preserving documented behavior. A removal, incompatible meaning change, or exit-class change requires a new public schema name and a major project version. Migration code must be exercised on both Windows and Ubuntu and on the minimum supported Python version.
