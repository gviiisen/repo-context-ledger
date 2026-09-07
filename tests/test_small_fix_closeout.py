"""Small-fix authoring cost without weakening publication or isolation checks."""

import io
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

import test_ledger as flow


RUNTIME = flow.LEDGER_MODULE
EXCEPTION = "This isolated fixture corrects a value without defining a new shared contract."


class SmallFixCloseoutTests(unittest.TestCase):
    run_ledger = flow.LedgerFlowTests.run_ledger
    run_git = flow.LedgerFlowTests.run_git
    init_git_repo = flow.LedgerFlowTests.init_git_repo
    fill_context_pack = flow.LedgerFlowTests.fill_context_pack
    repository_snapshot = flow.LedgerFlowTests.repository_snapshot

    def start(self, repo, workflow="small-fix"):
        return self.run_ledger(
            repo, "start", "--title", "Correct the fixture value",
            "--feature", "fixture-value", "--workflow", workflow, "--language", "en",
        )

    def fill_short(self, draft):
        text = draft.read_text(encoding="utf-8")
        replacements = [
            "Correct the fixture default so callers receive the documented value of two.",
            "The fixture returned one although its documented default is two.",
            "The fixture now returns two and its README describes that same default.",
            "`src/service.py::VALUE` changes the default from one to two to match the documented caller expectation; the boundaries and verification below apply.",
            "The exported VALUE name and import behavior remain compatible for callers.",
            "Imports have no new side effects; reverting this isolated constant restores the old value.",
            "No persistence, authorization, network calls, or adjacent configuration is changed.",
            "The README documents the same default; update that sentence when necessary without changing installation instructions.",
            "None.",
        ]
        self.assertEqual(len(replacements), text.count("TODO:"))
        for replacement in replacements:
            text = re.sub(r"TODO:[^\r\n]*", replacement, text, count=1)
        draft.write_text(text, encoding="utf-8")

    def verify(self, repo, session, passed=True):
        return self.run_ledger(
            repo, "verify", "--session", session, "--", sys.executable, "-B", "-c",
            "from src.service import VALUE; assert VALUE == " + ("2" if passed else "99"),
            expected=0 if passed else 1,
        )

    def test_one_request_one_concise_record_with_real_verification_and_auto_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            self.run_git(repo, "checkout", "-b", "fix/fixture")
            started = self.start(repo)
            session = flow.session_from_result(started)
            draft = flow.private_draft(repo, started)
            published = flow.publish_target(repo, started)
            original = draft.read_text(encoding="utf-8")
            self.assertEqual("concise", RUNTIME.field_value(original, "Detail"))
            self.assertNotIn("| Responsibility |", original)
            self.fill_short(draft)
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            (repo / "README.md").write_text("# Fixture\n\nThe default VALUE is 2.\n", encoding="utf-8")
            self.verify(repo, session)
            before = self.repository_snapshot(repo)
            preview = self.run_ledger(
                repo, "finish", "--session", session, "--no-spec", "--reason", EXCEPTION,
                "--dry-run",
            )
            self.assertIn(published.relative_to(repo).as_posix(), preview.stdout)
            self.assertEqual(before, self.repository_snapshot(repo))
            self.run_ledger(repo, "finish", "--session", session, "--no-spec", "--reason", EXCEPTION)
            self.assertFalse(draft.exists())
            text = published.read_text(encoding="utf-8")
            self.assertIn("`src/service.py::VALUE` changes the default from one to two", text)
            self.assertIn("Reason: The README documents the same default", text)
            self.assertIn("Updated: `README.md`", text)
            self.assertIn("- Status: passed", text)
            self.assertNotIn("Generated from scoped", text)
            self.assertEqual([], RUNTIME.handoff_validation_errors(
                text, repo, RUNTIME.load_config(repo), expected_status="completed"
            ))
            records = list((repo / "docs/changes").glob("*/*/*-*.md"))
            self.assertEqual([published], records)

    def test_known_task_accumulates_deltas_without_resume_and_keeps_published_history_immutable(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            started = self.start(repo)
            session = flow.session_from_result(started)
            draft = flow.private_draft(repo, started)
            published = flow.publish_target(repo, started)
            self.fill_short(draft)
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.verify(repo, session)
            # A known-path read needs no Ledger lifecycle call or replacement draft.
            snapshot = self.repository_snapshot(repo)
            self.assertEqual("VALUE = 2\n", (repo / "src/service.py").read_text(encoding="utf-8"))
            self.assertEqual(snapshot, self.repository_snapshot(repo))
            first_reason = "The initial correction selected two; the clarified requirement now selects three."
            text = draft.read_text(encoding="utf-8") + "\n## Decisions\n\n" + first_reason + "\n"
            text = text.replace("value of two.", "value of three.")
            text = text.replace("now returns two", "now returns three")
            text = text.replace("from one to two", "from one to three")
            draft.write_text(text, encoding="utf-8")
            (repo / "src/service.py").write_text("VALUE = 3\n", encoding="utf-8")
            (repo / "README.md").write_text("# Fixture\n\nThe default VALUE is 3.\n", encoding="utf-8")
            # A changed input needs a new check, but not a new task or epoch.
            self.run_ledger(repo, "verify", "--session", session, "--epoch", "1", "--",
                            sys.executable, "-B", "-c", "from src.service import VALUE; assert VALUE == 3")
            self.assertEqual(1, flow.session_record(repo, started)["resume_epoch"])
            self.run_ledger(repo, "finish", "--session", session, "--epoch", "1",
                            "--no-spec", "--reason", EXCEPTION)
            final = published.read_bytes()
            self.assertIn(first_reason, final.decode("utf-8"))
            self.assertEqual(2, final.decode("utf-8").count("- Status: passed"))
            self.assertEqual([published], list((repo / "docs/changes").glob("*/*/*-*.md")))
            self.run_ledger(repo, "verify", "--session", session, "--", sys.executable,
                            "-c", "raise AssertionError('must not run for completed task')", expected=2)
            later = self.start(repo)
            self.assertNotEqual(session, flow.session_from_result(later))
            self.assertEqual(final, published.read_bytes())

    def test_preview_aggregates_missing_semantics_spec_verification_and_pack_without_writes(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            created = self.run_ledger(repo, "pack", "--feature", "fixture-value", "--file", "src/service.py")
            pack = repo / created.stdout.splitlines()[0]
            self.fill_context_pack(pack)
            self.run_git(repo, "add", "-A")
            self.run_git(repo, "commit", "-m", "Add a related pack")
            started = self.start(repo)
            session = flow.session_from_result(started)
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.verify(repo, session, passed=False)
            before = self.repository_snapshot(repo)
            preview = self.run_ledger(repo, "finish", "--session", session, "--dry-run", expected=2)
            self.assertIn("TODO", preview.stderr)
            self.assertIn("--spec", preview.stderr)
            self.assertIn("verification failed", preview.stderr)
            self.assertIn("did not refresh a related Context Pack", preview.stderr)
            self.assertEqual(before, self.repository_snapshot(repo))
            actual = self.run_ledger(repo, "finish", "--session", session, expected=2)
            self.assertEqual(preview.stderr, actual.stderr)
            self.assertTrue(flow.private_draft(repo, started).is_file())

    def test_preview_never_acquires_a_lock(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            started = self.start(repo)
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            with mock.patch.object(RUNTIME, "repo_lock", side_effect=AssertionError("preview locked")), \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                result = RUNTIME.finish_change(repo, [], session=flow.session_from_result(started), dry_run=True)
            self.assertEqual(2, result)

    def test_short_draft_checkpoint_resume_and_epoch_still_apply(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            started = self.start(repo)
            session = flow.session_from_result(started)
            self.run_ledger(repo, "checkpoint", "--session", session,
                            "--summary", "The constant correction is still in progress.",
                            "--next", "Verify the default against its callers.")
            self.run_ledger(repo, "pause", "--session", session,
                            "--summary", "Keep the same request in a new window.",
                            "--next", "Finish this correction after checking the caller.")
            self.run_ledger(repo, "resume", "--session", session, "--tool", "cursor")
            draft = flow.private_draft(repo, started).read_text(encoding="utf-8")
            self.assertIn("Workflow: small-fix", draft)
            stale = self.run_ledger(repo, "finish", "--session", session, "--epoch", "1", "--dry-run", expected=2)
            self.assertIn("epoch", stale.stderr.lower())

    def test_two_sessions_require_scoped_evidence_and_foreign_preview_is_denied(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            first = self.start(repo)
            second = self.start(repo)
            first_id = flow.session_from_result(first)
            other_draft = flow.private_draft(repo, second)
            other_before = other_draft.read_bytes()
            self.fill_short(flow.private_draft(repo, first))
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.verify(repo, first_id)
            denied = self.run_ledger(repo, "finish", "--session", first_id, "--dry-run", expected=2)
            self.assertIn("no scoped evidence", denied.stderr)
            self.run_ledger(repo, "evidence", "--session", first_id, "--path", "src/service.py")
            self.run_ledger(repo, "finish", "--session", first_id, "--no-spec", "--reason", EXCEPTION)
            self.assertEqual(other_before, other_draft.read_bytes())
            self.run_git(repo, "config", "repo-context-ledger.principal", "another-person")
            foreign = self.run_ledger(repo, "finish", "--session", flow.session_from_result(second), "--dry-run", expected=2)
            self.assertIn("owned by another principal", foreign.stderr)
            self.assertEqual(other_before, other_draft.read_bytes())

    def test_reading_reference_is_not_a_fingerprint_or_coverage_dependency(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            created = self.run_ledger(repo, "pack", "--feature", "fixture-value",
                                      "--file", "src/service.py", "--reference", "README.md")
            pack = repo / created.stdout.splitlines()[0]
            self.fill_context_pack(pack)
            original = pack.read_bytes()
            (repo / "README.md").write_text("# Updated fixture guide\n", encoding="utf-8")
            self.assertEqual([], RUNTIME.context_pack_errors(repo, pack))
            self.assertEqual(original, pack.read_bytes())
            owned = RUNTIME.tracked_context_packs(repo, RUNTIME.load_config(repo))
            self.assertNotIn("README.md", owned)
            self.assertIn("src/service.py", owned)
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.assertTrue(any("stale" in error for error in RUNTIME.context_pack_errors(repo, pack)))
            self.run_ledger(repo, "pack", "--feature", "fixture-value")
            self.assertEqual(["src/service.py"], [item[0] for item in RUNTIME.pack_file_entries(pack.read_text(encoding="utf-8"))])
            self.assertEqual(1, len(RUNTIME.pack_reference_paths(pack.read_text(encoding="utf-8"))))
            (repo / "README.md").unlink()
            self.assertTrue(any("Invalid reading reference" in error for error in RUNTIME.context_pack_errors(repo, pack)))

    def test_invalid_reference_cannot_downgrade_existing_dependency_or_write_pack(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            self.run_ledger(repo, "pack", "--feature", "fixture-value", "--file", "src/service.py")
            pack = repo / "docs/ai/context-packs/fixture-value.md"
            before = pack.read_bytes()
            overlap = self.run_ledger(repo, "pack", "--feature", "fixture-value",
                                      "--reference", "src/service.py", expected=2)
            self.assertIn("must not also be tracked", overlap.stderr)
            for reference in ("missing.md", "../outside.md"):
                self.run_ledger(repo, "pack", "--feature", "fixture-value", "--reference", reference, expected=2)
            (repo / "guide (extra).md").write_text("# Fixture guide\n", encoding="utf-8")
            self.run_ledger(repo, "pack", "--feature", "fixture-value", "--reference", "guide (extra).md", expected=2)
            self.assertEqual(before, pack.read_bytes())

    def test_existing_full_draft_keeps_its_layout_and_custom_small_fix_paths_survive(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            ordinary = self.start(repo, "ordinary-change")
            full = flow.private_draft(repo, ordinary).read_text(encoding="utf-8")
            self.assertIn("| Path / symbol | Responsibility | Actual change |", full)
            self.assertNotIn("Workflow: small-fix", full)
            short = RUNTIME.small_fix_draft(full)
            self.assertLess(len(short.splitlines()), len(full.splitlines()))
            self.assertEqual(9, short.count("TODO:"))
            custom = RUNTIME.replace_section_body(short, "## Code paths", "`src/service.py::VALUE` is the caller-visible default.")
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            custom, _ = RUNTIME.render_handoff_evidence(repo, RUNTIME.load_config(repo), custom, ["src/service.py"])
            rendered = RUNTIME.complete_small_fix_draft(repo, RUNTIME.load_config(repo), custom)
            self.assertIn("`src/service.py::VALUE` is the caller-visible default.", rendered)

    def test_path_only_record_and_generated_reason_cannot_publish(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            started = self.start(repo)
            session = flow.session_from_result(started)
            draft = flow.private_draft(repo, started)
            self.fill_short(draft)
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.verify(repo, session)
            text = RUNTIME.replace_section_body(
                draft.read_text(encoding="utf-8"), "## Code paths", "Scoped changed paths: `src/service.py`"
            )
            text = RUNTIME.replace_section_body(text, "## Documentation updates",
                "Updated: None — No documentation path appears in this task's scoped Git evidence.\n"
                "Reason: Derived from this task's scoped Git change evidence; stable-spec requirements are checked separately.")
            draft.write_text(text, encoding="utf-8")
            for preview in (True, False):
                result = self.run_ledger(repo, "finish", "--session", session,
                    "--no-spec", "--reason", EXCEPTION, *( ["--dry-run"] if preview else [] ), expected=2)
                self.assertIn("not only list paths", result.stderr)
                self.assertIn("file list is not a rationale", result.stderr)
                self.assertEqual(text, draft.read_text(encoding="utf-8"))
                self.assertFalse(flow.publish_target(repo, started).exists())

    def test_each_coupled_implementation_path_needs_an_explanation_reference(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            started = self.start(repo)
            session = flow.session_from_result(started)
            draft = flow.private_draft(repo, started)
            published = flow.publish_target(repo, started)
            self.fill_short(draft)
            (repo / "src/defaults.py").write_text("DEFAULT = 2\n", encoding="utf-8")
            (repo / "src/service.py").write_text("from .defaults import DEFAULT\nVALUE = DEFAULT\n", encoding="utf-8")
            self.verify(repo, session)
            missing = self.run_ledger(repo, "finish", "--session", session,
                "--no-spec", "--reason", EXCEPTION, "--dry-run", expected=2)
            self.assertIn("explanation does not cite changed path: src/defaults.py", missing.stderr)
            explanation = (
                "`src/service.py::VALUE` now reads `src/defaults.py::DEFAULT` so the exported value "
                "and its shared default cannot drift; both files implement the same correction. "
                "The invariant and import verification below apply to both."
            )
            text = RUNTIME.replace_section_body(draft.read_text(encoding="utf-8"), "## Code paths", explanation)
            # Expansion keeps the same draft, explanations and managed verification.
            text = RUNTIME.set_field(text, "Workflow", "ordinary-change")
            text = RUNTIME.set_field(text, "Detail", "standard")
            draft.write_text(text, encoding="utf-8")
            self.run_ledger(repo, "finish", "--session", session, "--no-spec", "--reason", EXCEPTION)
            self.assertIn(explanation, published.read_text(encoding="utf-8"))
            self.assertIn("Workflow: ordinary-change", published.read_text(encoding="utf-8"))

    def test_decision_and_failed_attempt_survive_checkpoint_resume_and_single_publication(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            started = self.start(repo)
            session = flow.session_from_result(started)
            draft = flow.private_draft(repo, started)
            published = flow.publish_target(repo, started)
            self.fill_short(draft)
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.verify(repo, session, passed=False)
            decision = "Rejected the fixture expectation of 99 because callers require the documented default of two; retained the existing import contract."
            draft.write_text(draft.read_text(encoding="utf-8") + "\n## Decisions\n\n" + decision + "\n", encoding="utf-8")
            self.run_ledger(repo, "checkpoint", "--session", session,
                "--summary", "The wrong test expectation was diagnosed; see Decisions in this draft.",
                "--next", "Verify the documented value of two without changing the import contract.")
            self.run_ledger(repo, "pause", "--session", session,
                "--summary", "Continue the same correction with its retained decision.",
                "--next", "Run the corrected verification and finish this session.")
            self.run_ledger(repo, "resume", "--session", session, "--tool", "cursor")
            self.run_ledger(repo, "verify", "--session", session, "--epoch", "2", "--",
                sys.executable, "-B", "-c", "from src.service import VALUE; assert VALUE == 2")
            self.run_ledger(repo, "finish", "--session", session, "--epoch", "2", "--no-spec", "--reason", EXCEPTION)
            text = published.read_text(encoding="utf-8")
            self.assertIn(decision, text)
            self.assertIn("- Status: failed", text)
            self.assertIn("- Status: passed", text)
            self.assertEqual([published], list((repo / "docs/changes").glob("*/*/*-*.md")))
            self.assertFalse(draft.exists())

    def test_old_completed_short_records_stay_readable_but_unfinished_ones_need_explanations(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            started = self.start(repo)
            session = flow.session_from_result(started)
            draft = flow.private_draft(repo, started)
            self.fill_short(draft)
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.verify(repo, session)
            text, _ = RUNTIME.render_handoff_evidence(repo, RUNTIME.load_config(repo), draft.read_text(encoding="utf-8"))
            text = RUNTIME.complete_small_fix_draft(repo, RUNTIME.load_config(repo), text)
            text = re.sub(r"(?m)^Record format:.*\n", "", text)
            text = RUNTIME.replace_section_body(text, "## Code paths", "Scoped changed paths: `src/service.py`")
            archived = RUNTIME.set_field(text, "Status", "completed")
            self.assertEqual([], RUNTIME.handoff_validation_errors(
                archived, repo, RUNTIME.load_config(repo), expected_status="completed"))
            draft.write_text(text, encoding="utf-8")
            blocked = self.run_ledger(repo, "finish", "--session", session, "--no-spec", "--reason", EXCEPTION, expected=2)
            self.assertIn("not only list paths", blocked.stderr)
            self.assertEqual(text, draft.read_text(encoding="utf-8"))
            old_placeholders = RUNTIME.replace_section_body(text, "## Code paths", RUNTIME.SMALL_FIX_CODE_PLACEHOLDER)
            old_placeholders = RUNTIME.replace_section_body(old_placeholders, "## Documentation updates", RUNTIME.SMALL_FIX_DOCS_PLACEHOLDER)
            draft.write_text(old_placeholders, encoding="utf-8")
            missing = self.run_ledger(repo, "finish", "--session", session, "--no-spec", "--reason", EXCEPTION, expected=2)
            self.assertIn("TODO", missing.stderr)
            self.assertEqual(old_placeholders, draft.read_text(encoding="utf-8"))

    def test_explanation_can_be_chinese_and_missing_docs_reason_still_fails(self):
        config = {"docs": {"ai": "docs/ai", "specs": "docs/specs", "changes": "docs/changes"}}
        text = (
            "## Code paths\n\n`src/service.py::VALUE` 将默认值改为二，以符合调用方约定；保留现有导入方式。\n\n"
            "## Documentation updates\n\nUpdated: `README.md`\nReason: 使用说明中的默认值需要与实际行为保持一致。\n\n"
            + RUNTIME.EVIDENCE_START + "\n## Git change evidence\n- Changed paths:\n  - `src/service.py`\n"
            + RUNTIME.EVIDENCE_END + "\n"
        )
        self.assertEqual([], RUNTIME.small_fix_explanation_errors(config, text))
        self.assertIn("Small-fix change explanation does not cite changed path: src/service.py",
                      RUNTIME.small_fix_explanation_errors(config, text.replace("`src/service.py::VALUE`", "`service.py::VALUE`")))
        without_reason = text.replace("Reason: 使用说明中的默认值需要与实际行为保持一致。", "Reason:")
        self.assertIn("Documentation updates requires a substantive Reason: value.",
                      RUNTIME.evidence_handoff_errors(Path("."), config, without_reason))

    def test_blank_labeled_values_do_not_borrow_the_next_line(self):
        for newline in ("\n", "\r\n"):
            for following in ("After: A different behavior is now implemented.",
                              "<!-- repo-context-ledger:evidence:start -->", "## Another section"):
                with self.subTest(newline=repr(newline), following=following):
                    self.assertEqual("", RUNTIME.labeled_value("Reason: \t" + newline + following, "Reason"))
            self.assertEqual("A concrete reason.", RUNTIME.labeled_value("- Reason: A concrete reason." + newline, "Reason"))


if __name__ == "__main__":
    unittest.main()
