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


def field_from_file(path: Path, field: str) -> str:
    return LEDGER_MODULE.field_value(path.read_text(encoding="utf-8"), field)


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

    def run_git(self, repo: Path, *args: str, expected: int = 0):
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            capture_output=True,
            encoding="utf-8",
        )
        if result.returncode != expected:
            self.fail(
                f"git returned {result.returncode}, expected {expected}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

    def init_git_repo(self, repo: Path, actor: str = "Alice"):
        repo.mkdir(parents=True, exist_ok=True)
        self.run_git(repo, "init", "-b", "main")
        self.run_git(repo, "config", "user.name", actor)
        self.run_git(repo, "config", "user.email", f"{actor.casefold()}@example.test")
        source = repo / "src/service.py"
        source.parent.mkdir(parents=True)
        source.write_text("VALUE = 1\n", encoding="utf-8")
        self.run_ledger(repo, "init")
        self.run_git(repo, "add", "-A")
        self.run_git(repo, "commit", "-m", "Initialize repository")

    def fill_context_pack(self, path: Path):
        text = path.read_text(encoding="utf-8")
        replacements = [
            "Keeps authentication behavior understandable across fresh AI sessions.",
            "Read the linked spec first, followed by the tracked implementation file.",
            "The public entry point is the tracked authentication service module.",
            "Preserve credential validation, permissions, and existing failure behavior.",
            "Run the authentication unit tests and the strict ledger validation.",
        ]
        for replacement in replacements:
            text = re.sub(r"(?m)^TODO:.*$", replacement, text, count=1)
        path.write_text(text, encoding="utf-8")

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
            self.assertTrue((repo / ".context-ledger/context-state.json").exists())
            self.assertTrue((repo / ".context-ledger/templates/context-pack-template.md").exists())
            self.assertEqual(
                3,
                json.loads((repo / ".context-ledger/config.json").read_text(encoding="utf-8"))["schema_version"],
            )
            self.assertIn("Keep this text.", (repo / "AGENTS.md").read_text(encoding="utf-8"))

            # Re-initializing from the repository-local runtime is safe and idempotent.
            self.run_ledger(repo, "init")
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
            completed_state = json.loads(
                (repo / ".context-ledger/context-state.json").read_text(encoding="utf-8")
            )
            self.assertIsNone(completed_state["active_handoff"])
            self.assertFalse((repo / "docs/changes/.active-handoff").exists())
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

    def test_context_pack_focus_and_staleness_detection(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            source = repo / "src/auth.py"
            source.parent.mkdir(parents=True)
            source.write_text("def authenticate():\n    return True\n", encoding="utf-8")
            self.run_ledger(repo, "init")
            spec = repo / "docs/specs/authentication.md"
            spec.write_text("# Authentication\n\nStatus: current\n", encoding="utf-8")

            created = self.run_ledger(
                repo,
                "pack",
                "--feature",
                "authentication",
                "--title",
                "Authentication",
                "--file",
                "src/auth.py",
                "--spec",
                "docs/specs/authentication.md",
            )
            pack = repo / created.stdout.splitlines()[0]
            self.assertTrue(pack.exists())
            self.assertIn("Fill every TODO", created.stdout)
            incomplete = self.run_ledger(repo, "focus", "--feature", "authentication", expected=2)
            self.assertIn("TODO placeholders", incomplete.stderr)

            self.fill_context_pack(pack)
            focused = self.run_ledger(repo, "focus", "--feature", "authentication")
            self.assertIn("Context pack: docs/ai/context-packs/authentication.md", focused.stdout)
            self.assertIn("Stable spec: docs/specs/authentication.md", focused.stdout)
            self.assertIn("Tracked file: src/auth.py", focused.stdout)
            state = json.loads((repo / ".context-ledger/context-state.json").read_text(encoding="utf-8"))
            self.assertEqual("authentication", state["active_feature"])
            self.run_ledger(repo, "check", "--strict")

            source.write_text("def authenticate():\n    return False\n", encoding="utf-8")
            stale = self.run_ledger(repo, "focus", "--feature", "authentication", expected=2)
            self.assertIn("tracked file changed: src/auth.py", stale.stderr)
            strict = self.run_ledger(repo, "check", "--strict", expected=2)
            self.assertIn("Context pack is stale", strict.stderr)

            self.run_ledger(repo, "pack", "--feature", "authentication")
            self.run_ledger(repo, "focus", "--feature", "authentication")
            self.run_ledger(repo, "check", "--strict")

    def test_pause_stack_and_selected_resume(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            first = self.run_ledger(
                repo, "start", "--title", "Repair withdrawals", "--feature", "withdrawals"
            )
            first_path = first.stdout.strip().splitlines()[-1]
            self.run_ledger(
                repo,
                "pause",
                "--summary",
                "Withdrawal behavior has been inspected and no code is changed yet.",
                "--next",
                "Update the withdrawal service and its tests.",
            )
            paused_state = json.loads(
                (repo / ".context-ledger/context-state.json").read_text(encoding="utf-8")
            )
            self.assertIsNone(paused_state["active_handoff"])
            self.assertFalse((repo / "docs/changes/.active-handoff").exists())
            self.assertEqual("paused", field_from_file(repo / first_path, "Status"))
            self.assertNotIn(".write.lock", field_from_file(repo / first_path, "Dirty paths"))

            second = self.run_ledger(
                repo, "start", "--title", "Repair authentication", "--feature", "authentication"
            )
            second_path = second.stdout.strip().splitlines()[-1]
            self.run_ledger(
                repo,
                "pause",
                "--summary",
                "Authentication timeout behavior and tests have been located.",
                "--next",
                "Implement the timeout fix and run focused tests.",
            )
            state = json.loads((repo / ".context-ledger/context-state.json").read_text(encoding="utf-8"))
            self.assertEqual([second_path, first_path], state["paused_handoffs"])

            resumed_second = self.run_ledger(repo, "resume")
            self.assertIn(second_path, resumed_second.stdout)
            self.assertEqual("active", field_from_file(repo / second_path, "Status"))
            self.run_ledger(
                repo,
                "pause",
                "--summary",
                "Authentication remains paused after confirming the intended timeout fix.",
                "--next",
                "Apply the timeout change when this task becomes active again.",
            )
            resumed_first = self.run_ledger(repo, "resume", "--handoff", first_path)
            self.assertIn(first_path, resumed_first.stdout)
            final_state = json.loads((repo / ".context-ledger/context-state.json").read_text(encoding="utf-8"))
            self.assertEqual(first_path, final_state["active_handoff"])
            self.assertEqual("withdrawals", final_state["active_feature"])
            self.assertEqual([second_path], final_state["paused_handoffs"])

    def test_git_workspace_state_is_private_and_handoff_has_identity(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            started = self.run_ledger(
                repo, "start", "--title", "Repair authentication", "--feature", "authentication"
            )
            handoff_rel = started.stdout.strip().splitlines()[-1]
            handoff = repo / handoff_rel
            state_path = LEDGER_MODULE.context_state_path(repo)
            self.assertTrue(state_path.exists())
            self.assertIn(".git", state_path.parts)
            self.assertFalse((repo / ".context-ledger/context-state.json").exists())
            self.assertFalse((repo / "docs/changes/.active-handoff").exists())
            status = self.run_git(repo, "status", "--porcelain").stdout
            self.assertNotIn("context-state.json", status)
            self.assertNotIn(".active-handoff", status)
            text = handoff.read_text(encoding="utf-8")
            self.assertEqual("Alice", LEDGER_MODULE.field_value(text, "Actor"))
            self.assertEqual("main", LEDGER_MODULE.field_value(text, "Branch"))
            self.assertRegex(LEDGER_MODULE.field_value(text, "Handoff ID"), r"^\d{14}-alice-[0-9a-f]{10}$")
            self.assertIn("-alice-", handoff.name)

    def test_v2_git_state_and_active_pointer_migrate_to_private_v3_state(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            started = self.run_ledger(
                repo, "start", "--title", "Repair authentication", "--feature", "authentication"
            )
            handoff_rel = started.stdout.strip().splitlines()[-1]
            private_state = LEDGER_MODULE.context_state_path(repo)
            private_state.unlink()

            legacy_state = repo / ".context-ledger/context-state.json"
            legacy_state.write_text(
                json.dumps(
                    {
                        "version": 2,
                        "active_feature": "authentication",
                        "paused_handoffs": [],
                        "recent_features": ["authentication"],
                    }
                ),
                encoding="utf-8",
            )
            legacy_pointer = repo / "docs/changes/.active-handoff"
            legacy_pointer.write_text(handoff_rel + "\n", encoding="utf-8")
            config_path = repo / ".context-ledger/config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["schema_version"] = 2
            config.pop("team", None)
            config_path.write_text(json.dumps(config), encoding="utf-8")

            migrated = self.run_ledger(repo, "init")
            self.assertIn("Migrated shared v0.2 state to workspace-local v0.3 state", migrated.stdout)
            state = json.loads(LEDGER_MODULE.context_state_path(repo).read_text(encoding="utf-8"))
            self.assertEqual(handoff_rel, state["active_handoff"])
            self.assertEqual("authentication", state["active_feature"])
            self.assertFalse(legacy_state.exists())
            self.assertFalse(legacy_pointer.exists())
            self.assertEqual(3, json.loads(config_path.read_text(encoding="utf-8"))["schema_version"])

    def test_git_worktrees_have_independent_active_state(self):
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            repo = base / "repo"
            worktree = base / "worktree-b"
            self.init_git_repo(repo, "Alice")
            self.run_git(repo, "worktree", "add", "-b", "feature-b", str(worktree), "main")

            main_start = self.run_ledger(
                repo, "start", "--title", "Repair withdrawals", "--feature", "withdrawals"
            )
            other_start = self.run_ledger(
                worktree, "start", "--title", "Repair login", "--feature", "authentication"
            )
            main_state_path = LEDGER_MODULE.context_state_path(repo)
            other_state_path = LEDGER_MODULE.context_state_path(worktree)
            self.assertNotEqual(main_state_path, other_state_path)
            main_state = json.loads(main_state_path.read_text(encoding="utf-8"))
            other_state = json.loads(other_state_path.read_text(encoding="utf-8"))
            self.assertEqual(main_start.stdout.strip().splitlines()[-1], main_state["active_handoff"])
            self.assertEqual(other_start.stdout.strip().splitlines()[-1], other_state["active_handoff"])
            self.assertEqual("withdrawals", main_state["active_feature"])
            self.assertEqual("authentication", other_state["active_feature"])

    def test_feature_branch_skips_shared_derived_files(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            self.run_git(repo, "switch", "-c", "feature/auth")
            readme = repo / "README.md"
            change_index = repo / "docs/changes/README.md"
            before_readme = readme.read_text(encoding="utf-8")
            before_index = change_index.read_text(encoding="utf-8")

            started = self.run_ledger(
                repo, "start", "--title", "Repair authentication", "--feature", "authentication"
            )
            handoff = repo / started.stdout.strip().splitlines()[-1]
            self.assertTrue(handoff.exists())
            self.assertEqual(before_readme, readme.read_text(encoding="utf-8"))
            self.assertEqual(before_index, change_index.read_text(encoding="utf-8"))
            self.assertFalse((handoff.parent / "README.md").exists())
            skipped = self.run_ledger(repo, "sync")
            self.assertIn("Skipped shared README", skipped.stdout)

            self.run_ledger(repo, "sync", "--derived")
            self.assertTrue((handoff.parent / "README.md").exists())
            self.assertIn("Repair authentication", readme.read_text(encoding="utf-8"))

    def test_team_check_detects_same_path_and_feature_changed_upstream(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            source = repo / "src/service.py"

            self.run_git(repo, "switch", "-c", "feature/auth")
            source.write_text("VALUE = 2\n", encoding="utf-8")
            self.run_ledger(
                repo, "start", "--title", "Feature authentication", "--feature", "authentication"
            )
            self.run_git(repo, "add", "-A")
            self.run_git(repo, "commit", "-m", "Change authentication on feature")

            self.run_git(repo, "switch", "main")
            source.write_text("VALUE = 3\n", encoding="utf-8")
            self.run_ledger(
                repo, "start", "--title", "Main authentication", "--feature", "authentication"
            )
            self.run_git(repo, "add", "-A")
            self.run_git(repo, "commit", "-m", "Change authentication on main")

            self.run_git(repo, "switch", "feature/auth")
            checked = self.run_ledger(repo, "team-check", "--base", "main", expected=2)
            self.assertIn("Both this branch and main changed: src/service.py", checked.stderr)
            self.assertIn("Concurrent handoffs affect the same feature: authentication", checked.stderr)

    def test_focus_refuses_to_abandon_another_active_feature(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            source = repo / "src/auth.py"
            source.parent.mkdir(parents=True)
            source.write_text("enabled = True\n", encoding="utf-8")
            self.run_ledger(repo, "init")
            created = self.run_ledger(
                repo, "pack", "--feature", "authentication", "--file", "src/auth.py"
            )
            pack = repo / created.stdout.splitlines()[0]
            self.fill_context_pack(pack)
            self.run_ledger(
                repo, "start", "--title", "Repair withdrawals", "--feature", "withdrawals"
            )
            blocked = self.run_ledger(repo, "focus", "--feature", "authentication", expected=2)
            self.assertIn("pause it before focusing authentication", blocked.stderr)

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
                    state = LEDGER_MODULE.load_context_state(repo)
                    state["active_handoff"] = None
                    LEDGER_MODULE.save_context_state(repo, state)
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

    def test_legacy_repository_migrates_to_v3_without_losing_docs(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            project_context = repo / "docs/ai/project-context.md"
            project_context.write_text(
                project_context.read_text(encoding="utf-8").replace(
                    "TODO: Summarize what this repository delivers and who uses it.",
                    "Preserved project purpose.",
                ),
                encoding="utf-8",
            )
            config_path = repo / ".context-ledger/config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["schema_version"] = 1
            config_path.write_text(json.dumps(config), encoding="utf-8")
            (repo / ".context-ledger/context-state.json").unlink()
            (repo / ".context-ledger/templates/context-pack-template.md").unlink()

            self.run_ledger(repo, "init")
            migrated = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(3, migrated["schema_version"])
            self.assertTrue((repo / ".context-ledger/context-state.json").exists())
            self.assertTrue((repo / ".context-ledger/templates/context-pack-template.md").exists())
            self.assertIn("Preserved project purpose.", project_context.read_text(encoding="utf-8"))

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
