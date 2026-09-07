# Center product messaging on the feature change ledger

Status: completed
Feature: product-positioning
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260831182446-gviiisen-8decd6bb1b
Session ID: 20260831182446-gviiisen-8decd6bb1b
Actor: gviiisen
Branch: docs/feature-ledger-positioning
Started: 2026-08-31T18:24:46+08:00
Completed: 2026-08-31T18:29:42+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Dirty paths: none
Resume summary:
Next step:
Specs: none
Spec exception: This is product positioning and Skill discovery metadata, not a stable runtime behavior contract.

## Intent

Make the repository's primary value explicit: it records each behavior-changing feature addition, fix, and adjustment as verified repository knowledge. Present cross-window and cross-Agent continuation as a capability built from that ledger rather than as the product's only purpose.

## Changed behavior

Before: The README title, opening statement, discovery copy, and Skill introduction led with context switching and cross-Agent relay. Feature documentation and completed change records appeared as supporting mechanics, which understated the standalone value of preserving every functional change.

After: English and Chinese entry points lead with the feature change ledger, explain exactly which additions, fixes, and behavioral adjustments are recorded, and then show how those verified records enable accurate continuation across windows and Agent tools. The wording excludes formatting-only edits by consistently referring to behavior-changing work.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `README.md` | English project landing page and search/discovery entry point. | Reframed the title, hero, product summary, discovery terms, and problem statement around the feature change ledger. |
| `README.zh-CN.md` | Chinese project landing page and search/discovery entry point. | Added the same ledger-first positioning in natural Chinese while retaining context-management search intent. |
| `skills/repo-context-ledger/SKILL.md` | Native Skill discovery metadata and first operational explanation shown to Agents. | Made functional change recording the primary responsibility and continuation the derived capability. |

## Boundaries and risks

- Invariant: The project still promises bounded context routing, verified records, private unfinished drafts, and cross-Agent continuation; the change only corrects their product hierarchy.
- Failure / recovery: Documentation-only wording can be reverted independently and does not alter the runtime, schemas, generated adapters, or repository data.
- Not changed: No CLI behavior, document model, verification gate, session ownership rule, generated index, or installation command changed.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `git diff --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.05s
  - Recorded: 2026-08-31T18:28:49+08:00
  - Output evidence: sha256:33a00947854f3c6128b361c15123532e13cfff6b912daaa03d68878b130778ee (338 characters captured; content not persisted; last=warning: in the working copy of 'skills/repo-context-ledger/SKILL.md', LF will be replaced by CRLF the next time Git touches it)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, and `skills/repo-context-ledger/SKILL.md`.

Reason: These are the public and Agent-facing entry points that define the project's purpose and discovery language.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `68c3b0cb9de9d1f975f847046d9db2b883fef00f`
- Current commit: `68c3b0cb9de9d1f975f847046d9db2b883fef00f`
- Changed paths:
  - `docs/ai/context-packs/task-session-integrity.md`
  - `skills/repo-context-ledger/SKILL.md`
<!-- repo-context-ledger:evidence:end -->
