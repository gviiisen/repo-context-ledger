import datetime as dt
import importlib.util
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from contextlib import redirect_stdout
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
LEDGER_SPEC = importlib.util.spec_from_file_location("repo_context_ledger_runtime", LEDGER)
LEDGER_MODULE = importlib.util.module_from_spec(LEDGER_SPEC)
LEDGER_SPEC.loader.exec_module(LEDGER_MODULE)


class LedgerFlowTests(unittest.TestCase):
    def test_skill_metadata_matches_open_agent_skills_shape(self):
        skill = ROOT / "skills" / "repo-context-ledger" / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match)
        frontmatter = match.group(1)
        self.assertIn("name: repo-context-ledger", frontmatter)
        self.assertIn("description:", frontmatter)
        self.assertNotIn("[TODO:", text)

    def run_ledger(self, repo: Path, *args: str, expected: int = 0):
        result = subprocess.run(
            [sys.executable, str(LEDGER), "--repo", str(repo), *args],
            text=True,
            capture_output=True,
            encoding="utf-8",
        )
        if result.returncode != expected:
            self.fail(
                f"command returned {result.returncode}, expected {expected}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

    def test_end_to_end_preserves_readmes_and_links_specs(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            (repo / "README.md").write_text("# Demo\n\nHuman root text.\n", encoding="utf-8")
            (repo / "AGENTS.md").write_text("# Existing rules\n\nKeep this text.\n", encoding="utf-8")
            (repo / "CLAUDE.md").write_text("# Existing Claude notes\n", encoding="utf-8")
            module = repo / "apps" / "payments"
            module.mkdir(parents=True)
            (module / "package.json").write_text('{"name":"payments"}\n', encoding="utf-8")
            (module / "README.md").write_text("# Payments\n\nHuman module text.\n", encoding="utf-8")

            self.run_ledger(repo, "init")
            self.assertIn("Human root text.", (repo / "README.md").read_text(encoding="utf-8"))
            self.assertIn("Human module text.", (module / "README.md").read_text(encoding="utf-8"))
            self.assertTrue((repo / "AGENTS.md").exists())
            self.assertTrue((repo / ".cursor/rules/repo-context-ledger.mdc").exists())
            self.assertIn("Keep this text.", (repo / "AGENTS.md").read_text(encoding="utf-8"))

            # Re-initializing from the repository-local runtime is safe and idempotent.
            local_runtime = repo / ".context-ledger/ledger.py"
            result = subprocess.run(
                [sys.executable, str(local_runtime), "--repo", str(repo), "init"],
                text=True,
                capture_output=True,
                encoding="utf-8",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(1, (repo / "AGENTS.md").read_text(encoding="utf-8").count("<!-- repo-context-ledger:rules:start -->"))

            start = self.run_ledger(repo, "start", "--title", "Repair payment status")
            handoff_rel = start.stdout.strip().splitlines()[-1]
            handoff = repo / handoff_rel
            self.assertTrue(handoff.exists())

            spec = repo / "docs/specs/payment-status.md"
            spec.write_text(
                "# Payment status\n\nStatus: current\nLast reviewed: 2026-01-01\n\n"
                "## Purpose and behavior\n\nShows current state.\n\n"
                "## Entry points and code map\n\n`apps/payments/status.ts`.\n\n"
                "## Data flow and contracts\n\nReads the payment API.\n\n"
                "## Boundaries and failure modes\n\nUnknown states remain visible.\n\n"
                "## Verification\n\nRun payment tests.\n",
                encoding="utf-8",
            )
            handoff.write_text(handoff.read_text(encoding="utf-8").replace("TODO:", "Recorded:"), encoding="utf-8")
            self.run_ledger(repo, "finish", "--spec", "docs/specs/payment-status.md")
            self.assertEqual("", (repo / "docs/changes/.active-handoff").read_text(encoding="utf-8"))
            self.assertIn("Repair payment status", spec.read_text(encoding="utf-8"))
            self.assertIn("Latest recorded change", (module / "README.md").read_text(encoding="utf-8"))
            self.assertIn("Human root text.", (repo / "README.md").read_text(encoding="utf-8"))
            month_index = handoff.parent / "README.md"
            self.assertTrue(month_index.exists())
            self.assertIn("Repair payment status", month_index.read_text(encoding="utf-8"))
            root_change_index = (repo / "docs/changes/README.md").read_text(encoding="utf-8")
            self.assertIn(month_index.parent.relative_to(repo / "docs/changes").as_posix(), root_change_index)
            self.assertNotIn(handoff.name, root_change_index)
            self.run_ledger(repo, "check", "--strict")

            context = self.run_ledger(repo, "context", "--query", "payment status")
            self.assertIn("docs/specs/payment-status.md", context.stdout)

    def test_different_active_handoff_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            self.run_ledger(repo, "start", "--title", "First task")
            result = self.run_ledger(repo, "start", "--title", "Second task", expected=2)
            self.assertIn("Another handoff is active", result.stderr)

    def test_handoff_names_never_overwrite_history(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            fixed = dt.datetime(2026, 8, 11, 12, 30, 45, tzinfo=dt.timezone.utc)
            with redirect_stdout(io.StringIO()):
                with mock.patch.object(LEDGER_MODULE, "now", return_value=fixed):
                    self.assertEqual(0, LEDGER_MODULE.start_change(repo, "修复接口"))
                    config = LEDGER_MODULE.load_config(repo)
                    first = LEDGER_MODULE.active_handoff(repo, config)
                    original = first.read_text(encoding="utf-8")
                    LEDGER_MODULE.active_pointer(repo, config).write_text("", encoding="utf-8")
                    self.assertEqual(0, LEDGER_MODULE.start_change(repo, "修复接口"))
                    second = LEDGER_MODULE.active_handoff(repo, config)
            self.assertNotEqual(first, second)
            self.assertEqual(original, first.read_text(encoding="utf-8"))

    def test_finish_requires_content_and_explicit_spec_exception(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            start = self.run_ledger(repo, "start", "--title", "No stable spec change")
            handoff = repo / start.stdout.strip().splitlines()[-1]
            handoff.write_text(
                "# No stable spec change\n\nStatus: active\nStarted: 2026-08-11\nCompleted:\nSpecs: none\n\n"
                "## Intent\n\n\n## Changed behavior\n\n\n## Code paths\n\n\n"
                "## Boundaries and risks\n\n\n## Verification\n\n\n## Documentation updates\n",
                encoding="utf-8",
            )
            self.run_ledger(repo, "finish", expected=2)
            valid = (
                "# No stable spec change\n\nStatus: active\nStarted: 2026-08-11\nCompleted:\nSpecs: none\n\n"
                "## Intent\n\nRefresh generated navigation only.\n\n"
                "## Changed behavior\n\nNo runtime behavior changed.\n\n"
                "## Code paths\n\nOnly generated documentation files changed.\n\n"
                "## Boundaries and risks\n\nNo product contracts were affected.\n\n"
                "## Verification\n\nLedger validation completed successfully.\n\n"
                "## Documentation updates\n\nREADME navigation was refreshed.\n"
            )
            handoff.write_text(valid, encoding="utf-8")
            self.run_ledger(repo, "finish", expected=2)
            self.run_ledger(
                repo,
                "finish",
                "--no-spec",
                "--reason",
                "Only generated navigation changed; no stable behavior exists to document.",
            )

    def test_config_paths_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            repo = base / "repo"
            repo.mkdir()
            self.run_ledger(repo, "init")
            config_path = repo / ".context-ledger/config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["modules"] = [{"path": "module", "readme": "../outside.md", "source": "manual"}]
            config_path.write_text(json.dumps(config), encoding="utf-8")
            result = self.run_ledger(repo, "sync", expected=2)
            self.assertIn("outside the repository", result.stderr)
            self.assertFalse((base / "outside.md").exists())

    def test_custom_doc_paths_are_used_by_sync_and_check(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            config_path = repo / ".context-ledger/config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["docs"] = {
                "ai": "knowledge/ai",
                "specs": "knowledge/specs",
                "changes": "knowledge/changes",
            }
            config_path.write_text(json.dumps(config), encoding="utf-8")
            shutil.rmtree(repo / "docs")
            local_runtime = repo / ".context-ledger/ledger.py"
            result = subprocess.run(
                [sys.executable, str(local_runtime), "--repo", str(repo), "init"],
                text=True,
                capture_output=True,
                encoding="utf-8",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.run_ledger(repo, "check", "--strict")
            self.assertTrue((repo / "knowledge/changes/README.md").exists())

    def test_deleted_auto_module_is_not_recreated(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            module = repo / "apps/temporary"
            module.mkdir(parents=True)
            (module / "package.json").write_text('{"name":"temporary"}\n', encoding="utf-8")
            self.run_ledger(repo, "init")
            self.assertTrue((module / "README.md").exists())
            shutil.rmtree(module)
            local_runtime = repo / ".context-ledger/ledger.py"
            result = subprocess.run(
                [sys.executable, str(local_runtime), "--repo", str(repo), "init"],
                text=True,
                capture_output=True,
                encoding="utf-8",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertFalse(module.exists())
            config = json.loads((repo / ".context-ledger/config.json").read_text(encoding="utf-8"))
            self.assertEqual([], config["modules"])

    def test_invalid_config_is_not_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            runtime = repo / ".context-ledger"
            runtime.mkdir()
            config_path = runtime / "config.json"
            config_path.write_text("{not valid json", encoding="utf-8")
            result = self.run_ledger(repo, "init", expected=2)
            self.assertIn("Invalid ledger configuration", result.stderr)
            self.assertEqual("{not valid json", config_path.read_text(encoding="utf-8"))
            self.assertFalse((runtime / ".write.lock").exists())

    def test_concurrent_writer_lock_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            lock = repo / ".context-ledger/.write.lock"
            lock.write_text("existing writer", encoding="utf-8")
            result = self.run_ledger(repo, "sync", expected=2)
            self.assertIn("Another Repo Context Ledger write is active", result.stderr)
            self.assertEqual("existing writer", lock.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
