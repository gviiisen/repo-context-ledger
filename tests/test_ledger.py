import datetime as dt
import importlib.util
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
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


def session_from_result(result) -> str:
    for line in result.stdout.splitlines():
        if line.startswith("Session: "):
            return line.removeprefix("Session: ").strip()
    raise AssertionError(f"start output did not contain a session ID: {result.stdout}")


def session_record(repo: Path, result) -> dict:
    state = json.loads(LEDGER_MODULE.context_state_path(repo).read_text(encoding="utf-8"))
    return state["task_sessions"][session_from_result(result)]


def private_draft(repo: Path, result) -> Path:
    return LEDGER_MODULE.validate_private_draft_path(repo, session_record(repo, result)["draft"])


def publish_target(repo: Path, result) -> Path:
    return repo / session_record(repo, result)["publish_path"]


class LedgerFlowTests(unittest.TestCase):
    def test_empty_metadata_field_does_not_consume_the_next_line(self):
        text = (
            "Checkpointed:\n"
            "Checkpoint actor:\n"
            "Resume summary:\n"
            "Next step:\n"
            "Specs: none\n"
        )
        self.assertEqual("", LEDGER_MODULE.field_value(text, "Checkpointed"))
        self.assertEqual("", LEDGER_MODULE.field_value(text, "Resume summary"))
        self.assertEqual("", LEDGER_MODULE.field_value(text, "Next step"))
        self.assertEqual("none", LEDGER_MODULE.field_value(text, "Specs"))
        crlf = text.replace("\n", "\r\n")
        self.assertEqual("", LEDGER_MODULE.field_value(crlf, "Resume summary"))
        self.assertEqual("none", LEDGER_MODULE.field_value(crlf, "Specs"))

    def test_uncheckpointed_owned_session_routes_as_guided_not_ready(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            self.run_git(repo, "config", "repo-context-ledger.principal", "alice-profile")
            started = self.run_ledger(
                repo,
                "start", "--title", "Announcement rate limiting",
                "--feature", "announcement-rate-limit", "--tool", "codex",
            )
            plan = json.loads(self.run_ledger(
                repo,
                "context", "--query", "continue announcement rate limiting",
                "--tool", "cursor", "--format", "json",
            ).stdout)
            capsule = plan["resume"]["capsule"]
            self.assertEqual(session_from_result(started), capsule["session_id"])
            self.assertEqual("guided", plan["resume"]["mode"])
            self.assertEqual("", capsule["summary"])
            self.assertEqual("", capsule["next_step"])
            self.assertIn("the task has no checkpoint resume summary", capsule["unknowns"])

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
            errors="replace",
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
            errors="replace",
        )
        if result.returncode != expected:
            self.fail(
                f"git returned {result.returncode}, expected {expected}\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        return result

    def repository_snapshot(self, repo: Path) -> dict[str, bytes]:
        return {
            path.relative_to(repo).as_posix(): path.read_bytes()
            for path in sorted(repo.rglob("*"))
            if path.is_file()
        }

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
        text = text.replace("Language: auto", "Language: en")
        replacements = [
            "Keeps authentication behavior understandable across fresh AI sessions.",
            "Read `docs/specs/authentication.md` followed by `src/auth.py`.",
            "Read `src/auth.py` only when authentication implementation details are required.",
            "Do not load unrelated payment modules for authentication work.",
            "src/auth.py", "Provides the public authentication service entry point.",
            "Preserve credential validation, permissions, and existing failure behavior.",
            "Authentication failures remain explicit and callers retry through the existing flow.",
            "Payment processing and unrelated authorization policy remain out of scope.",
            "Run `python -m unittest` to verify authentication behavior without claiming a result.",
        ]
        for replacement in replacements:
            text = re.sub(r"TODO:[^|`\r\n]*", replacement, text, count=1)
        path.write_text(text, encoding="utf-8")

    def fill_handoff(self, path: Path, code_path: str, docs_path: str):
        text = path.read_text(encoding="utf-8")
        text = text.replace("Language: auto", "Language: en")
        replacements = [
            "Deliver the requested behavior and make its acceptance result observable to callers.",
            "The previous behavior returned the uncorrected result for the affected request.",
            "The corrected behavior now returns the expected result while preserving compatibility.",
            code_path,
            "Owns the affected request path and its behavior.",
            "Applies the focused behavior correction without unrelated refactoring.",
            "Existing public contracts and authorization rules remain unchanged.",
            "Failures keep the existing error contract and recovery remains retry-safe.",
            "Unrelated modules, persistence schemas, and public routes are not changed.",
            f"`{docs_path}`",
            "The stable specification records the current behavior and links this change.",
            "None.",
        ]
        for replacement in replacements:
            text = re.sub(r"TODO:[^|`\r\n]*", replacement, text, count=1)
        path.write_text(text, encoding="utf-8")

    def fill_spec(self, path: Path):
        text = path.read_text(encoding="utf-8")
        text = text.replace("{{TITLE}}", "Validation behavior")
        text = text.replace("{{LANGUAGE}}", "en")
        text = text.replace("{{DETAIL}}", "standard")
        text = text.replace("{{DATE}}", "2026-08-11")
        replacements = [
            "Validation returns explicit errors for unsupported requests and preserves accepted behavior.",
            "src/validation.py",
            "Owns request validation and the public error mapping.",
            "Requests contain validated fields and reject unsupported values before processing.",
            "The validator applies ordered rules before calling downstream dependencies.",
            "No durable state is written and dependency errors preserve their existing contract.",
            "Callers receive the accepted value or an explicit validation error.",
            "Accepted requests preserve their existing validation invariants.",
            "Authorization remains upstream and validation is deterministic under concurrent calls.",
            "Invalid requests fail before side effects and callers can correct then retry.",
            "Persistence and unrelated request routing remain outside this feature.",
            "Run `python -m unittest` to verify the validation contract.",
        ]
        for replacement in replacements:
            text = re.sub(r"TODO:[^|`\r\n]*", replacement, text, count=1)
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
            self.assertTrue((repo / ".github/copilot-instructions.md").exists())

            self.assertTrue((repo / "docs/ai/context-manifest.json").exists())
            self.assertTrue((repo / ".context-ledger/context-state.json").exists())
            self.assertTrue((repo / ".context-ledger/templates/context-pack-template.md").exists())
            self.assertTrue((repo / ".context-ledger/writing-quality.md").exists())
            self.assertEqual(
                8,
                json.loads((repo / ".context-ledger/config.json").read_text(encoding="utf-8"))["schema_version"],
            )
            quality = json.loads(
                (repo / ".context-ledger/config.json").read_text(encoding="utf-8")
            )["quality"]
            self.assertEqual("auto", quality["language"])
            self.assertEqual("standard", quality["detail"])
            self.assertIn("Keep this text.", (repo / "AGENTS.md").read_text(encoding="utf-8"))

            # Re-initializing from the repository-local runtime is safe and idempotent.
            self.run_ledger(repo, "init")
            self.assertEqual(1, (repo / "AGENTS.md").read_text(encoding="utf-8").count("<!-- repo-context-ledger:rules:start -->"))

            start = self.run_ledger(repo, "start", "--title", "Repair payment status")
            handoff = private_draft(repo, start)
            final_handoff = publish_target(repo, start)
            self.assertTrue(handoff.exists())
            self.assertFalse(final_handoff.exists())

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
            self.fill_handoff(handoff, "apps/payments/status.ts", "docs/specs/payment-status.md")
            self.run_ledger(repo, "verify", "--", sys.executable, "-c", "print('payment verification passed')")
            self.run_ledger(repo, "finish", "--spec", "docs/specs/payment-status.md")
            completed_state = json.loads(
                (repo / ".context-ledger/context-state.json").read_text(encoding="utf-8")
            )
            self.assertEqual({}, completed_state["task_sessions"])
            self.assertFalse((repo / "docs/changes/.active-handoff").exists())
            self.assertTrue(final_handoff.exists())
            self.assertFalse(handoff.exists())
            self.assertIn("Repair payment status", spec.read_text(encoding="utf-8"))
            self.assertIn("Latest recorded change", (module / "README.md").read_text(encoding="utf-8"))
            self.assertIn("Human root text.", (repo / "README.md").read_text(encoding="utf-8"))
            month_index = final_handoff.parent / "README.md"
            self.assertTrue(month_index.exists())
            self.assertIn("Repair payment status", month_index.read_text(encoding="utf-8"))
            root_change_index = (repo / "docs/changes/README.md").read_text(encoding="utf-8")
            self.assertIn(month_index.parent.relative_to(repo / "docs/changes").as_posix(), root_change_index)
            self.assertNotIn(final_handoff.name, root_change_index)
            self.run_ledger(repo, "check", "--strict")

            status_file = repo / "apps/payments/status.ts"
            status_file.write_text("export const status = 'ok'\n", encoding="utf-8")
            self.run_ledger(
                repo,
                "pack",
                "--feature",
                "payment-status",
                "--title",
                "Payment status",
                "--file",
                "apps/payments/status.ts",
                "--spec",
                "docs/specs/payment-status.md",
            )
            context = self.run_ledger(repo, "context", "--query", "payment status")
            self.assertIn("Primary pack: docs/ai/context-packs/payment-status.md", context.stdout)
            self.assertIn("docs/specs/payment-status.md", context.stdout)

    def test_init_dry_run_is_read_only_and_matches_real_init_plan(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            (repo / "README.md").write_text("# Demo\n\nHuman root text.\n", encoding="utf-8")
            (repo / "AGENTS.md").write_text("# Existing rules\n\nKeep this text.\n", encoding="utf-8")
            module = repo / "apps" / "payments"
            module.mkdir(parents=True)
            (module / "package.json").write_text('{"name":"payments"}\n', encoding="utf-8")
            before = self.repository_snapshot(repo)

            preview = self.run_ledger(repo, "init", "--dry-run")

            self.assertEqual(before, self.repository_snapshot(repo))
            self.assertFalse((repo / ".context-ledger").exists())
            self.assertIn("Repo Context Ledger init plan", preview.stdout)
            self.assertIn("CREATE .context-ledger/ledger.py", preview.stdout)
            self.assertIn("UPDATE AGENTS.md [managed block]", preview.stdout)
            self.assertIn("Detected modules: 1", preview.stdout)
            self.assertIn("Modules:\n- apps/payments (auto)", preview.stdout)
            self.assertIn("Dry run only. No files were written.", preview.stdout)

            applied = self.run_ledger(repo, "init")
            preview_operations = [
                line for line in preview.stdout.splitlines()
                if line.startswith(("CREATE ", "UPDATE ", "DELETE ", "MIGRATE "))
            ]
            applied_operations = [
                line for line in applied.stdout.splitlines()
                if line.startswith(("CREATE ", "UPDATE ", "DELETE ", "MIGRATE "))
            ]
            self.assertEqual(preview_operations, applied_operations)
            self.assertTrue((repo / ".context-ledger" / "ledger.py").is_file())
            self.assertIn("Human root text.", (repo / "README.md").read_text(encoding="utf-8"))

    def test_init_dry_run_on_current_repository_plans_no_file_changes(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            before = self.repository_snapshot(repo)

            preview = self.run_ledger(repo, "init", "--dry-run")

            self.assertEqual(before, self.repository_snapshot(repo))
            self.assertIn("No file changes planned.", preview.stdout)
            self.assertIn("Dry run only. No files were written.", preview.stdout)

    def test_init_dry_run_does_not_acquire_repository_write_lock(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            output = io.StringIO()
            with mock.patch.object(
                LEDGER_MODULE,
                "repo_lock",
                side_effect=AssertionError("dry-run attempted to acquire the write lock"),
            ):
                with redirect_stdout(output):
                    result = LEDGER_MODULE.main(["--repo", str(repo), "init", "--dry-run"])

            self.assertEqual(0, result)
            self.assertIn("Dry run only. No files were written.", output.getvalue())
            self.assertFalse((repo / ".context-ledger").exists())

    def test_native_adapters_preserve_copilot_prose_and_detect_drift(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            copilot = repo / ".github/copilot-instructions.md"
            copilot.parent.mkdir(parents=True)
            copilot.write_text("# Existing Copilot guidance\n\nKeep this prose.\n", encoding="utf-8")

            self.run_ledger(repo, "init")
            config = json.loads((repo / ".context-ledger/config.json").read_text(encoding="utf-8"))
            self.assertEqual(8, config["schema_version"])
            self.assertEqual(
                {"agents": True, "claude": True, "cursor": True, "copilot": True},
                config["adapters"],
            )
            self.assertEqual(["**"], config["coverage"]["implementation_globs"])
            self.assertEqual(
                {
                    "max_required_files": 3,
                    "max_linked_specs": 2,
                    "max_change_summaries": 3,
                    "max_total_characters": 30000,
                    "show_close_candidates": 0,
                },
                config["context"],
            )
            self.assertIn(
                "Never message or steer another user-owned task",
                (repo / ".cursor/rules/repo-context-ledger.mdc").read_text(encoding="utf-8"),
            )
            self.assertIn(
                "Never send a message, delegation",
                (repo / "AGENTS.md").read_text(encoding="utf-8"),
            )
            adapter_paths = [
                repo / "AGENTS.md",
                repo / "CLAUDE.md",
                repo / ".cursor/rules/repo-context-ledger.mdc",
                repo / ".github/copilot-instructions.md",
            ]
            policy_phrases = [
                "context --query",
                "Required reads",
                "Never recursively read",
                "Do not open completed Change bodies unless",
                "Expand context only after stating the unresolved question",
            ]
            for adapter_path in adapter_paths:
                adapter_text = adapter_path.read_text(encoding="utf-8")
                for phrase in policy_phrases:
                    self.assertIn(phrase, adapter_text, f"{phrase!r} missing from {adapter_path}")
            self.assertIn("tests/**", config["coverage"]["test_globs"])
            self.assertIn("Keep this prose.", copilot.read_text(encoding="utf-8"))
            checked = self.run_ledger(repo, "adapters", "check")
            self.assertIn("copilot: current", checked.stdout)

            cursor = repo / ".cursor/rules/repo-context-ledger.mdc"
            cursor.write_text(cursor.read_text(encoding="utf-8") + "drift\n", encoding="utf-8")
            drifted = self.run_ledger(repo, "adapters", "check", expected=2)
            self.assertIn("missing-or-drifted", drifted.stdout)
            self.run_ledger(repo, "adapters", "sync")
            self.run_ledger(repo, "adapters", "check")
            self.assertIn("Keep this prose.", copilot.read_text(encoding="utf-8"))

    def test_context_manifest_indexes_feature_routes(self):
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
                "--file",
                "src/auth.py",
                "--spec",
                "docs/specs/authentication.md",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_ledger(repo, "manifest", "sync")

            manifest = json.loads((repo / "docs/ai/context-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(1, manifest["manifest_version"])
            self.assertEqual("0.6.0", manifest["tool_version"])
            route = manifest["features"][0]
            self.assertEqual("authentication", route["feature"])
            self.assertEqual("docs/ai/context-packs/authentication.md", route["context_pack"])
            self.assertEqual(["docs/specs/authentication.md"], route["stable_specs"])
            self.assertEqual(["src/auth.py"], route["tracked_files"])
            self.run_ledger(repo, "manifest", "check")

    def test_checkpoint_keeps_handoff_active_and_records_resume_evidence(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            started = self.run_ledger(
                repo, "start", "--title", "Repair service", "--feature", "service"
            )
            handoff = private_draft(repo, started)
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.run_ledger(
                repo,
                "checkpoint",
                "--summary",
                "Service behavior is implemented and focused verification remains.",
                "--next",
                "Run the focused service test.",
            )
            text = handoff.read_text(encoding="utf-8")
            self.assertEqual("active", field_from_file(handoff, "Status"))
            self.assertEqual("Alice", field_from_file(handoff, "Checkpoint actor"))
            self.assertIn("implemented", field_from_file(handoff, "Resume summary"))
            self.assertIn("src/service.py", text)

    def test_coverage_requires_handoff_spec_and_context_pack(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            source = repo / "src/service.py"
            source.write_text("VALUE = 2\n", encoding="utf-8")
            missing = self.run_ledger(repo, "check", "--coverage", expected=2)
            self.assertIn("no changed record or active private handoff", missing.stderr)

            started = self.run_ledger(
                repo, "start", "--title", "Change service behavior", "--feature", "service"
            )
            self.assertTrue(private_draft(repo, started).is_file())
            self.assertFalse(publish_target(repo, started).exists())
            spec = repo / "docs/specs/service.md"
            spec.write_text(
                "# Service behavior\n\nStatus: current\n\n"
                "The service exposes the tested value contract.\n",
                encoding="utf-8",
            )
            created = self.run_ledger(
                repo,
                "pack",
                "--feature",
                "service",
                "--file",
                "src/service.py",
                "--spec",
                "docs/specs/service.md",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_ledger(repo, "evidence")
            self.run_ledger(repo, "manifest", "sync")
            self.run_ledger(repo, "check", "--coverage")

    def test_coverage_classifies_tests_ci_config_and_managed_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            config = LEDGER_MODULE.load_config(repo)
            self.assertEqual("implementation", LEDGER_MODULE.coverage_path_kind(config, "src/service.py"))
            self.assertEqual("test", LEDGER_MODULE.coverage_path_kind(config, "tests/test_service.py"))
            self.assertEqual("test", LEDGER_MODULE.coverage_path_kind(config, "src/service.test.ts"))
            self.assertEqual("ci", LEDGER_MODULE.coverage_path_kind(config, ".github/workflows/test.yml"))
            self.assertEqual("config", LEDGER_MODULE.coverage_path_kind(config, "pyproject.toml"))
            self.assertEqual("generated", LEDGER_MODULE.coverage_path_kind(config, "dist/app.js"))
            self.assertEqual("managed", LEDGER_MODULE.coverage_path_kind(config, ".context-ledger/config.json"))
            self.assertEqual("managed", LEDGER_MODULE.coverage_path_kind(config, "README.zh-CN.md"))
            config["modules"] = [{"path": "apps/api", "readme": "apps/api/README.md", "source": "manual"}]
            self.assertEqual("managed", LEDGER_MODULE.coverage_path_kind(config, "apps/api/README.md"))
            config["coverage"]["ignore_globs"] = ["scratch/**"]
            self.assertEqual("ignored", LEDGER_MODULE.coverage_path_kind(config, "scratch/note.txt"))

    def test_coverage_allows_test_and_ci_only_changes_without_handoff(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            test_file = repo / "tests/test_service.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("def test_service():\n    assert True\n", encoding="utf-8")
            workflow = repo / ".github/workflows/test.yml"
            workflow.parent.mkdir(parents=True)
            workflow.write_text("name: test\n", encoding="utf-8")
            self.run_ledger(repo, "check", "--coverage")

    def test_coverage_rejects_an_unrelated_changed_context_pack(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            other = repo / "src/other.py"
            other.write_text("OTHER = 1\n", encoding="utf-8")
            self.run_git(repo, "add", "src/other.py")
            self.run_git(repo, "commit", "-m", "Add other source")

            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.run_ledger(repo, "start", "--title", "Change service", "--feature", "service")
            spec = repo / "docs/specs/service.md"
            spec.write_text("# Service\n\nStatus: current\n\nCurrent service behavior.\n", encoding="utf-8")
            created = self.run_ledger(
                repo, "pack", "--feature", "other", "--file", "src/other.py",
                "--spec", "docs/specs/service.md",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_ledger(repo, "evidence")

            result = self.run_ledger(repo, "check", "--coverage", expected=2)
            self.assertIn(
                "Behavior-changing path has no related Context Pack tracked file: src/service.py",
                result.stderr,
            )

    def test_coverage_requires_the_related_context_pack_to_change(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            spec = repo / "docs/specs/service.md"
            spec.write_text("# Service\n\nStatus: current\n\nThe service returns its configured value.\n", encoding="utf-8")
            created = self.run_ledger(
                repo, "pack", "--feature", "service", "--file", "src/service.py",
                "--spec", "docs/specs/service.md",
            )
            pack = repo / created.stdout.splitlines()[0]
            self.fill_context_pack(pack)
            self.run_ledger(repo, "manifest", "sync")
            self.run_git(repo, "add", "-A")
            self.run_git(repo, "commit", "-m", "Document service context")

            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            self.run_ledger(repo, "start", "--title", "Change service", "--feature", "service")
            spec.write_text(spec.read_text(encoding="utf-8") + "The updated value remains observable.\n", encoding="utf-8")
            self.run_ledger(repo, "evidence")

            missing = self.run_ledger(repo, "check", "--coverage", expected=2)
            self.assertIn("Related Context Pack was not changed", missing.stderr)

            self.run_ledger(
                repo, "pack", "--feature", "service", "--file", "src/service.py",
                "--spec", "docs/specs/service.md",
            )
            self.run_ledger(repo, "check", "--coverage")

    def test_coverage_ignores_spec_exception_from_an_unrelated_private_session(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            other = repo / "src/other.py"
            other.write_text("OTHER = 1\n", encoding="utf-8")
            self.run_git(repo, "add", "src/other.py")
            self.run_git(repo, "commit", "-m", "Add unrelated source")

            other.write_text("OTHER = 2\n", encoding="utf-8")
            foreign = self.run_ledger(
                repo, "start", "--title", "Change other", "--feature", "other"
            )
            foreign_session = session_from_result(foreign)
            self.run_ledger(repo, "evidence", "--session", foreign_session)
            foreign_draft = private_draft(repo, foreign)
            foreign_text = foreign_draft.read_text(encoding="utf-8").replace(
                "Spec exception:",
                "Spec exception: This unrelated task has no durable stable behavior to specify.",
            )
            foreign_draft.write_text(foreign_text, encoding="utf-8")
            self.run_git(repo, "restore", "--", "src/other.py")

            service = repo / "src/service.py"
            service.write_text("VALUE = 2\n", encoding="utf-8")
            current = self.run_ledger(
                repo, "start", "--title", "Change service", "--feature", "service"
            )
            current_session = session_from_result(current)
            created = self.run_ledger(
                repo, "pack", "--feature", "service", "--file", "src/service.py"
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_ledger(
                repo,
                "evidence",
                "--session",
                current_session,
                "--path",
                "src/service.py",
            )

            result = self.run_ledger(repo, "check", "--coverage", expected=2)
            self.assertIn(
                "Behavior-changing paths require a changed stable spec or a completed spec exception.",
                result.stderr,
            )

    def test_parallel_task_sessions_are_isolated_and_ambiguous_commands_fail_closed(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            first = self.run_ledger(repo, "start", "--title", "First task")
            second = self.run_ledger(repo, "start", "--title", "Second task")
            first_session = session_from_result(first)
            second_session = session_from_result(second)
            self.assertNotEqual(first_session, second_session)
            state = json.loads((repo / ".context-ledger/context-state.json").read_text(encoding="utf-8"))
            self.assertEqual({first_session, second_session}, set(state["task_sessions"]))
            self.assertTrue(private_draft(repo, first).is_file())
            self.assertTrue(private_draft(repo, second).is_file())
            self.assertFalse(publish_target(repo, first).exists())
            self.assertFalse(publish_target(repo, second).exists())
            self.assertEqual([], [
                path for path in (repo / "docs/changes").rglob("*.md")
                if path.name != "README.md"
            ])
            ambiguous = self.run_ledger(repo, "evidence", expected=2)
            self.assertIn("Multiple active task sessions exist", ambiguous.stderr)
            first_evidence = self.run_ledger(repo, "evidence", "--session", first_session)
            self.assertIn(first_session, first_evidence.stdout)

    def test_parallel_evidence_requires_explicit_session_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            first = self.run_ledger(repo, "start", "--title", "First scoped task")
            second = self.run_ledger(repo, "start", "--title", "Second scoped task")
            first_session = session_from_result(first)

            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            blocked = self.run_ledger(
                repo, "evidence", "--session", first_session, expected=2
            )
            self.assertIn("pass --path for only this task", blocked.stderr)

            captured = self.run_ledger(
                repo,
                "evidence",
                "--session",
                first_session,
                "--path",
                "src/service.py",
            )
            self.assertIn("src/service.py", captured.stdout)
            evidence = LEDGER_MODULE.managed_text(
                private_draft(repo, first).read_text(encoding="utf-8"),
                LEDGER_MODULE.EVIDENCE_START,
                LEDGER_MODULE.EVIDENCE_END,
            )
            self.assertIn("`src/service.py`", evidence)
            self.assertNotIn(session_from_result(second), evidence)

    def test_finish_ignores_foreign_session_dirty_paths_and_stale_pack(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            first_source = repo / "src/first.py"
            foreign_source = repo / "src/foreign.py"
            first_source.write_text("VALUE = 1\n", encoding="utf-8")
            foreign_source.write_text("VALUE = 1\n", encoding="utf-8")

            first_pack_result = self.run_ledger(
                repo, "pack", "--feature", "first-task", "--file", "src/first.py"
            )
            first_pack = repo / first_pack_result.stdout.splitlines()[0]
            self.fill_context_pack(first_pack)
            foreign_pack_result = self.run_ledger(
                repo, "pack", "--feature", "foreign-task", "--file", "src/foreign.py"
            )
            foreign_pack = repo / foreign_pack_result.stdout.splitlines()[0]
            self.fill_context_pack(foreign_pack)
            self.run_git(repo, "add", "-A")
            self.run_git(repo, "commit", "-m", "Add parallel task fixtures")

            first = self.run_ledger(
                repo, "start", "--title", "Finish first task", "--language", "en"
            )
            second = self.run_ledger(
                repo, "start", "--title", "Keep foreign task active", "--language", "en"
            )
            first_session = session_from_result(first)
            second_session = session_from_result(second)
            first_draft = private_draft(repo, first)
            second_draft = private_draft(repo, second)
            second_before = second_draft.read_bytes()

            first_source.write_text("VALUE = 2\n", encoding="utf-8")
            foreign_source.write_text("VALUE = 2\n", encoding="utf-8")
            self.run_ledger(repo, "pack", "--feature", "first-task")
            self.fill_handoff(first_draft, "src/first.py", "docs/ai/context-packs/first-task.md")
            self.run_ledger(
                repo,
                "verify",
                "--session",
                first_session,
                "--",
                sys.executable,
                "-c",
                "print('first scoped task passed')",
            )
            self.run_ledger(
                repo,
                "evidence",
                "--session",
                first_session,
                "--path",
                "src/first.py",
                "--path",
                "docs/ai/context-packs/first-task.md",
            )

            completed = self.run_ledger(
                repo,
                "finish",
                "--session",
                first_session,
                "--no-spec",
                "--reason",
                "This isolated fixture has no durable product specification to maintain.",
            )
            self.assertIn("Completed", completed.stdout)
            self.assertEqual(second_before, second_draft.read_bytes())
            state = LEDGER_MODULE.load_context_state(repo)
            self.assertNotIn(first_session, state["task_sessions"])
            self.assertEqual("active", state["task_sessions"][second_session]["status"])
            self.assertIn(
                "tracked file changed: src/foreign.py",
                self.run_ledger(repo, "check", "--strict", expected=2).stderr,
            )

    def test_finish_still_rejects_the_current_sessions_stale_pack(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            source = repo / "src/current.py"
            source.write_text("VALUE = 1\n", encoding="utf-8")
            pack_result = self.run_ledger(
                repo, "pack", "--feature", "current-task", "--file", "src/current.py"
            )
            pack = repo / pack_result.stdout.splitlines()[0]
            self.fill_context_pack(pack)
            self.run_git(repo, "add", "-A")
            self.run_git(repo, "commit", "-m", "Add current task fixture")

            started = self.run_ledger(
                repo, "start", "--title", "Reject stale current pack", "--language", "en"
            )
            session_id = session_from_result(started)
            draft = private_draft(repo, started)
            source.write_text("VALUE = 2\n", encoding="utf-8")
            pack.write_text(pack.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            self.fill_handoff(draft, "src/current.py", "docs/ai/context-packs/current-task.md")
            self.run_ledger(
                repo,
                "verify",
                "--session",
                session_id,
                "--",
                sys.executable,
                "-c",
                "print('current task passed')",
            )
            self.run_ledger(
                repo,
                "evidence",
                "--session",
                session_id,
                "--path",
                "src/current.py",
                "--path",
                "docs/ai/context-packs/current-task.md",
            )
            blocked = self.run_ledger(
                repo,
                "finish",
                "--session",
                session_id,
                "--no-spec",
                "--reason",
                "This isolated fixture has no durable product specification to maintain.",
                expected=2,
            )
            self.assertIn("tracked file changed: src/current.py", blocked.stderr)
            self.assertTrue(draft.is_file())

    def test_finishing_one_session_publishes_only_its_record(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            first = self.run_ledger(repo, "start", "--title", "First isolated task", "--language", "en")
            second = self.run_ledger(repo, "start", "--title", "Second isolated task", "--language", "en")
            first_session = session_from_result(first)
            second_session = session_from_result(second)
            first_draft = private_draft(repo, first)
            second_draft = private_draft(repo, second)
            second_before = second_draft.read_bytes()
            first_target = publish_target(repo, first)

            self.fill_handoff(first_draft, "src/first.py", "docs/specs/first.md")
            self.run_ledger(
                repo, "verify", "--session", first_session, "--",
                sys.executable, "-c", "print('first session passed')",
            )
            self.run_ledger(
                repo, "finish", "--session", first_session, "--no-spec", "--reason",
                "This isolated fixture has no durable product specification to maintain.",
            )

            self.assertTrue(first_target.is_file())
            self.assertFalse(first_draft.exists())
            self.assertEqual(second_before, second_draft.read_bytes())
            state = LEDGER_MODULE.load_context_state(repo)
            self.assertNotIn(first_session, state["task_sessions"])
            self.assertEqual("active", state["task_sessions"][second_session]["status"])

    def test_interrupted_publish_keeps_draft_and_finish_recovers_idempotently(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            started = self.run_ledger(repo, "start", "--title", "Recover publication", "--language", "en")
            session_id = session_from_result(started)
            draft = private_draft(repo, started)
            target = publish_target(repo, started)
            self.fill_handoff(draft, "src/recovery.py", "docs/specs/recovery.md")
            self.run_ledger(
                repo, "verify", "--session", session_id, "--",
                sys.executable, "-c", "print('recovery passed')",
            )
            with redirect_stdout(io.StringIO()):
                with mock.patch.object(
                    LEDGER_MODULE,
                    "task_session_finish_errors",
                    side_effect=[[], ["Injected post-publication failure."]],
                ):
                    self.assertEqual(
                        2,
                        LEDGER_MODULE.finish_change(
                            repo, [], True,
                            "This recovery fixture has no durable product specification to maintain.",
                            session_id,
                        ),
                    )
            self.assertTrue(target.is_file())
            self.assertTrue(draft.is_file())
            self.assertIn(session_id, LEDGER_MODULE.load_context_state(repo)["task_sessions"])

            with redirect_stdout(io.StringIO()):
                with mock.patch.object(
                    LEDGER_MODULE,
                    "task_session_finish_errors",
                    side_effect=[[], []],
                ):
                    self.assertEqual(
                        0,
                        LEDGER_MODULE.finish_change(
                            repo, [], True,
                            "This recovery fixture has no durable product specification to maintain.",
                            session_id,
                        ),
                    )
            self.assertTrue(target.is_file())
            self.assertFalse(draft.exists())
            self.assertNotIn(session_id, LEDGER_MODULE.load_context_state(repo)["task_sessions"])

    def test_long_verification_releases_repo_lock_and_records_only_its_session(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            first = self.run_ledger(repo, "start", "--title", "Slow verification")
            second = self.run_ledger(repo, "start", "--title", "Concurrent evidence")
            first_session = session_from_result(first)
            second_session = session_from_result(second)
            first_handoff = private_draft(repo, first)
            second_handoff = private_draft(repo, second)

            process = subprocess.Popen(
                [
                    sys.executable, str(LEDGER), "--repo", str(repo), "verify",
                    "--timeout", "10", "--session", first_session, "--",
                    sys.executable, "-c", "import time; time.sleep(2); print('slow check passed')",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
            )
            time.sleep(0.4)
            started = time.monotonic()
            evidence = self.run_ledger(repo, "evidence", "--session", second_session)
            elapsed = time.monotonic() - started
            stdout, stderr = process.communicate(timeout=8)

            self.assertEqual(0, process.returncode, stderr)
            self.assertLess(elapsed, 1.3)
            self.assertIn(second_session, evidence.stdout)
            self.assertIn("slow check passed", stdout)
            self.assertIn("Status: passed", first_handoff.read_text(encoding="utf-8"))
            self.assertNotIn("Status: passed", second_handoff.read_text(encoding="utf-8"))

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
            self.assertEqual("authentication", state["recent_features"][0])
            self.run_ledger(repo, "check", "--strict")

            source.write_text("def authenticate():\n    return False\n", encoding="utf-8")
            stale = self.run_ledger(repo, "focus", "--feature", "authentication", expected=2)
            self.assertIn("tracked file changed: src/auth.py", stale.stderr)
            strict = self.run_ledger(repo, "check", "--strict", expected=2)
            self.assertIn("Context pack is stale", strict.stderr)

            self.run_ledger(repo, "pack", "--feature", "authentication")
            self.run_ledger(repo, "focus", "--feature", "authentication")
            self.run_ledger(repo, "check", "--strict")

    def test_context_pack_text_fingerprints_ignore_checkout_line_endings(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            source = repo / "src/auth.py"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"def authenticate():\n    return True\n")
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
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_ledger(repo, "check", "--strict")

            source.write_bytes(b"def authenticate():\r\n    return True\r\n")
            self.run_ledger(repo, "check", "--strict")

            source.write_bytes(b"def authenticate():\r\n    return False\r\n")
            stale = self.run_ledger(repo, "check", "--strict", expected=2)
            self.assertIn("Context pack is stale", stale.stderr)

    def test_context_pack_binary_fingerprints_remain_byte_sensitive(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            source = repo / "assets/payload.bin"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"\x00payload\r\n")
            self.run_ledger(repo, "init")
            created = self.run_ledger(
                repo,
                "pack",
                "--feature",
                "binary-payload",
                "--title",
                "Binary payload",
                "--file",
                "assets/payload.bin",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_ledger(repo, "check", "--strict")

            source.write_bytes(b"\x00payload\n")
            stale = self.run_ledger(repo, "check", "--strict", expected=2)
            self.assertIn("Context pack is stale", stale.stderr)

    def test_context_pack_fingerprints_respect_git_binary_attributes(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            attributes = repo / ".gitattributes"
            attributes.write_text("assets/*.bin -text\n", encoding="utf-8")
            source = repo / "assets/payload.bin"
            source.parent.mkdir(parents=True)
            source.write_bytes(b"payload\r\n")
            created = self.run_ledger(
                repo,
                "pack",
                "--feature",
                "binary-payload",
                "--title",
                "Binary payload",
                "--file",
                "assets/payload.bin",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_ledger(repo, "check", "--strict")

            source.write_bytes(b"payload\n")
            stale = self.run_ledger(repo, "check", "--strict", expected=2)
            self.assertIn("Context pack is stale", stale.stderr)

    def test_pause_stack_and_selected_resume(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            first = self.run_ledger(
                repo, "start", "--title", "Repair withdrawals", "--feature", "withdrawals"
            )
            first_path = private_draft(repo, first)
            first_session = session_from_result(first)
            self.run_ledger(
                repo,
                "pause",
                "--summary",
                "Withdrawal behavior has been inspected and no code is changed yet.",
                "--next",
                "Update the withdrawal service and its tests.",
                "--session",
                first_session,
            )
            paused_state = json.loads(
                (repo / ".context-ledger/context-state.json").read_text(encoding="utf-8")
            )
            self.assertEqual("paused", paused_state["task_sessions"][first_session]["status"])
            self.assertFalse((repo / "docs/changes/.active-handoff").exists())
            self.assertEqual("paused", field_from_file(first_path, "Status"))
            self.assertNotIn(".write.lock", field_from_file(first_path, "Dirty paths"))

            second = self.run_ledger(
                repo, "start", "--title", "Repair authentication", "--feature", "authentication"
            )
            second_path = private_draft(repo, second)
            second_session = session_from_result(second)
            self.run_ledger(
                repo,
                "pause",
                "--summary",
                "Authentication timeout behavior and tests have been located.",
                "--next",
                "Implement the timeout fix and run focused tests.",
                "--session",
                second_session,
            )
            state = json.loads((repo / ".context-ledger/context-state.json").read_text(encoding="utf-8"))
            self.assertEqual("paused", state["task_sessions"][first_session]["status"])
            self.assertEqual("paused", state["task_sessions"][second_session]["status"])

            ambiguous = self.run_ledger(repo, "resume", expected=2)
            self.assertIn("Multiple resumable task sessions exist", ambiguous.stderr)
            resumed_second = self.run_ledger(repo, "resume", "--session", second_session)
            self.assertIn(second_session, resumed_second.stdout)
            self.assertEqual("active", field_from_file(second_path, "Status"))
            self.run_ledger(
                repo,
                "pause",
                "--summary",
                "Authentication remains paused after confirming the intended timeout fix.",
                "--next",
                "Apply the timeout change when this task becomes active again.",
                "--session",
                second_session,
                "--epoch",
                "2",
            )
            resumed_first = self.run_ledger(repo, "resume", "--session", first_session)
            self.assertIn(first_session, resumed_first.stdout)
            final_state = json.loads((repo / ".context-ledger/context-state.json").read_text(encoding="utf-8"))
            self.assertEqual("active", final_state["task_sessions"][first_session]["status"])
            self.assertEqual(
                LEDGER_MODULE.session_draft_ref(repo, first_path),
                final_state["task_sessions"][first_session]["draft"],
            )
            self.assertEqual("paused", final_state["task_sessions"][second_session]["status"])

    def test_owned_session_routes_across_agents_and_requires_new_epoch(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            self.run_git(repo, "config", "repo-context-ledger.principal", "alice-profile")
            started = self.run_ledger(
                repo,
                "start", "--title", "Announcement rate limiting",
                "--feature", "announcement-rate-limit", "--tool", "codex",
            )
            session_id = session_from_result(started)
            source = repo / "src/service.py"
            source.write_text("VALUE = 2\n", encoding="utf-8")
            created = self.run_ledger(
                repo,
                "pack", "--feature", "announcement-rate-limit",
                "--title", "Announcement Rate Limiting", "--file", "src/service.py",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_ledger(
                repo,
                "checkpoint", "--session", session_id,
                "--summary", "Measured announcement request latency and refreshed the focused Pack.",
                "--next", "Add bounded concurrency to detail hydration.",
            )

            plan = json.loads(self.run_ledger(
                repo,
                "context", "--query", "continue announcement rate limiting",
                "--tool", "cursor", "--format", "json",
            ).stdout)

            self.assertEqual("context-bundle-v1", plan["schema"])
            self.assertEqual("ready", plan["resume"]["mode"])
            capsule = plan["resume"]["capsule"]
            self.assertEqual(session_id, capsule["session_id"])
            self.assertEqual(["src/service.py"], capsule["evidence_paths"])
            self.assertLessEqual(
                capsule["budget"]["used_characters"], capsule["budget"]["max_characters"]
            )
            serialized_capsule = json.dumps(capsule, ensure_ascii=False, sort_keys=True)
            self.assertEqual(len(serialized_capsule), capsule["budget"]["used_characters"])
            self.assertLessEqual(len(serialized_capsule), capsule["budget"]["max_characters"])
            self.assertTrue(any(
                "not as a maximum" in instruction for instruction in plan["instructions"]
            ))
            self.assertNotIn(str(repo), json.dumps(plan))

            resumed = self.run_ledger(
                repo,
                "resume", "--query", "continue announcement rate limiting", "--tool", "cursor",
            )
            self.assertIn("Continuation epoch: 2", resumed.stdout)
            state = LEDGER_MODULE.load_context_state(repo)
            self.assertEqual({session_id}, set(state["task_sessions"]))
            record = state["task_sessions"][session_id]
            self.assertEqual(2, record["resume_epoch"])
            self.assertEqual("cursor", record["continuation_tool"])
            self.assertTrue(record["epoch_required"])

            stale = self.run_ledger(
                repo,
                "checkpoint", "--session", session_id,
                "--summary", "The stale Agent window attempted to overwrite the checkpoint.",
                "--next", "This write must be rejected.",
                expected=2,
            )
            self.assertIn("rerun with --epoch 2", stale.stderr)
            self.run_ledger(
                repo,
                "checkpoint", "--session", session_id, "--epoch", "2",
                "--summary", "Cursor revalidated the resumed task against the current code paths.",
                "--next", "Continue through every behavior-relevant caller and boundary.",
            )

    def test_foreign_principal_cannot_read_or_mutate_private_resume_capsule(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            self.run_git(repo, "config", "repo-context-ledger.principal", "alice-profile")
            created = self.run_ledger(
                repo,
                "pack", "--feature", "announcement-rate-limit",
                "--title", "Announcement Rate Limiting", "--file", "src/service.py",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            started = self.run_ledger(
                repo,
                "start", "--title", "Announcement rate limiting",
                "--feature", "announcement-rate-limit", "--tool", "codex",
            )
            session_id = session_from_result(started)
            self.run_ledger(
                repo,
                "checkpoint", "--session", session_id,
                "--summary", "Alice recorded a private announcement throttling checkpoint.",
                "--next", "Alice will inspect the shared HTTP client boundary.",
            )
            owner_before = LEDGER_MODULE.load_context_state(repo)["task_sessions"][session_id]

            self.run_git(repo, "config", "repo-context-ledger.principal", "bob-profile")
            with mock.patch.object(
                LEDGER_MODULE,
                "resume_session_view",
                side_effect=AssertionError("foreign private draft must not be loaded"),
            ):
                private_route, private_selected = LEDGER_MODULE.route_resume_sessions(
                    repo,
                    LEDGER_MODULE.load_config(repo),
                    "continue announcement rate limiting",
                    LEDGER_MODULE.load_live_context_packs(repo, LEDGER_MODULE.load_config(repo)),
                )
            self.assertTrue(private_route["foreign_overlap"])
            self.assertIsNone(private_selected)
            plan = json.loads(self.run_ledger(
                repo,
                "context", "--query", "continue announcement rate limiting", "--format", "json",
            ).stdout)
            self.assertEqual("guided", plan["resume"]["mode"])
            self.assertTrue(plan["resume"]["foreign_overlap"])
            self.assertIsNone(plan["resume"]["capsule"])
            self.assertNotIn("Alice recorded", json.dumps(plan))

            denied = self.run_ledger(repo, "resume", "--session", session_id, expected=2)
            self.assertIn("owned by another principal", denied.stderr)
            denied = self.run_ledger(
                repo,
                "pause", "--session", session_id,
                "--summary", "Bob must not pause Alice's private task session.",
                "--next", "Use only Git-tracked context instead.",
                expected=2,
            )
            self.assertIn("owned by another principal", denied.stderr)
            owner_after = LEDGER_MODULE.load_context_state(repo)["task_sessions"][session_id]
            self.assertEqual(owner_before, owner_after)
            status = self.run_ledger(repo, "status")
            self.assertIn("Active task sessions: 0", status.stdout)
            self.assertIn("Foreign task sessions: 1", status.stdout)

    def test_resume_query_fails_closed_for_multiple_owned_matches(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            self.run_git(repo, "config", "repo-context-ledger.principal", "alice-profile")
            created = self.run_ledger(
                repo,
                "pack", "--feature", "announcement-rate-limit",
                "--title", "Announcement Rate Limiting", "--file", "src/service.py",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            sessions = []
            for venue in ("OKX", "Gate"):
                started = self.run_ledger(
                    repo,
                    "start", "--title", f"Announcement rate limiting {venue}",
                    "--feature", "announcement-rate-limit", "--tool", "codex",
                )
                session_id = session_from_result(started)
                sessions.append(session_id)
                self.run_ledger(
                    repo,
                    "checkpoint", "--session", session_id,
                    "--summary", f"Measured the {venue} announcement request path and latency.",
                    "--next", f"Apply the {venue} detail request concurrency boundary.",
                )

            plan = json.loads(self.run_ledger(
                repo,
                "context", "--query", "continue announcement rate limiting", "--format", "json",
            ).stdout)
            self.assertEqual("blocked", plan["resume"]["mode"])
            self.assertEqual(set(sessions), {
                candidate["session_id"] for candidate in plan["resume"]["candidates"]
            })
            ambiguous = self.run_ledger(
                repo,
                "resume", "--query", "continue announcement rate limiting", expected=2,
            )
            self.assertIn("Resume query is ambiguous", ambiguous.stderr)

    def test_explicit_session_grants_are_bounded_and_do_not_mutate_owner_by_default(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            self.run_git(repo, "config", "repo-context-ledger.principal", "alice-profile")
            created = self.run_ledger(
                repo,
                "pack", "--feature", "announcement-rate-limit",
                "--title", "Announcement Rate Limiting", "--file", "src/service.py",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            started = self.run_ledger(
                repo,
                "start", "--title", "Announcement rate limiting",
                "--feature", "announcement-rate-limit", "--tool", "codex",
            )
            source_session = session_from_result(started)
            self.run_ledger(
                repo,
                "checkpoint", "--session", source_session,
                "--summary", "Alice checkpointed the announcement request throttling boundary.",
                "--next", "Revalidate the shared HTTP client before changing concurrency.",
            )

            self.run_git(repo, "config", "repo-context-ledger.principal", "bob-profile")
            bob_principal = LEDGER_MODULE.current_principal(repo)
            self.run_git(repo, "config", "repo-context-ledger.principal", "alice-profile")
            source_draft = LEDGER_MODULE.resolve_session_draft(
                repo,
                LEDGER_MODULE.load_config(repo),
                source_session,
                LEDGER_MODULE.load_context_state(repo)["task_sessions"][source_session],
            )
            source_before_fork = source_draft.read_bytes()
            self.run_ledger(
                repo,
                "share", "--session", source_session, "--to", bob_principal,
                "--mode", "read-only", "--expires-hours", "2",
            )

            self.run_git(repo, "config", "repo-context-ledger.principal", "bob-profile")
            read_plan = json.loads(self.run_ledger(
                repo,
                "context", "--query", "continue announcement rate limiting", "--format", "json",
            ).stdout)
            self.assertEqual("read-only", read_plan["resume"]["capsule"]["access"])
            self.assertIn("Alice checkpointed", read_plan["resume"]["capsule"]["summary"])
            denied = self.run_ledger(repo, "resume", "--session", source_session, expected=2)
            self.assertIn("read-only", denied.stderr)
            status = self.run_ledger(repo, "status")
            self.assertIn("Shared task sessions: 1", status.stdout)
            self.assertIn("access=read-only", status.stdout)

            expired = LEDGER_MODULE.load_context_state(repo)
            expired["task_sessions"][source_session]["grants"][0]["expires_at"] = (
                LEDGER_MODULE.now() - dt.timedelta(seconds=1)
            ).isoformat(timespec="seconds")
            LEDGER_MODULE.save_context_state(repo, expired)
            expired_plan = json.loads(self.run_ledger(
                repo,
                "context", "--query", "continue announcement rate limiting", "--format", "json",
            ).stdout)
            self.assertTrue(expired_plan["resume"]["foreign_overlap"])
            self.assertIsNone(expired_plan["resume"]["capsule"])

            self.run_git(repo, "config", "repo-context-ledger.principal", "alice-profile")
            self.run_ledger(
                repo,
                "share", "--session", source_session, "--to", bob_principal,
                "--mode", "fork", "--expires-hours", "2",
            )
            self.run_git(repo, "config", "repo-context-ledger.principal", "bob-profile")
            forked = self.run_ledger(
                repo, "resume", "--session", source_session, "--tool", "cursor"
            )
            self.assertIn(f"Forked session {source_session} ->", forked.stdout)
            state = LEDGER_MODULE.load_context_state(repo)
            self.assertEqual(2, len(state["task_sessions"]))
            source = state["task_sessions"][source_session]
            self.assertNotEqual(bob_principal, source["owner_principal"])
            child_id = next(item for item in state["task_sessions"] if item != source_session)
            child = state["task_sessions"][child_id]
            self.assertEqual(bob_principal, child["owner_principal"])
            self.assertEqual("cursor", child["continuation_tool"])
            self.assertEqual(source_before_fork, source_draft.read_bytes())
            child_draft = LEDGER_MODULE.resolve_session_draft(
                repo, LEDGER_MODULE.load_config(repo), child_id, child
            )
            self.assertEqual(source_session, field_from_file(child_draft, "Parent session"))

            self.run_git(repo, "config", "repo-context-ledger.principal", "alice-profile")
            rejected_transfer = self.run_ledger(
                repo,
                "share", "--session", source_session, "--to", bob_principal,
                "--mode", "transfer", "--expires-hours", "2",
                expected=2,
            )
            self.assertIn("Pause the task session", rejected_transfer.stderr)
            self.run_ledger(
                repo,
                "pause", "--session", source_session,
                "--summary", "Alice paused the source task before transferring ownership to Bob.",
                "--next", "Bob must accept the transfer and revalidate current code.",
            )
            self.run_ledger(
                repo,
                "share", "--session", source_session, "--to", bob_principal,
                "--mode", "transfer", "--expires-hours", "2",
            )
            self.run_git(repo, "config", "repo-context-ledger.principal", "bob-profile")
            transferred = self.run_ledger(
                repo, "resume", "--session", source_session, "--tool", "cursor"
            )
            self.assertIn("Continuation epoch: 2", transferred.stdout)
            state = LEDGER_MODULE.load_context_state(repo)
            self.assertEqual(bob_principal, state["task_sessions"][source_session]["owner_principal"])

            self.run_git(repo, "config", "repo-context-ledger.principal", "alice-profile")
            denied = self.run_ledger(
                repo,
                "pause", "--session", source_session,
                "--summary", "Alice must not mutate the task after transferring ownership.",
                "--next", "Use the forked or Git-tracked context instead.",
                expected=2,
            )
            self.assertIn("owned by another principal", denied.stderr)

    def test_git_workspace_state_is_private_and_handoff_has_identity(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            started = self.run_ledger(
                repo, "start", "--title", "Repair authentication", "--feature", "authentication"
            )
            handoff = private_draft(repo, started)
            final_handoff = publish_target(repo, started)
            state_path = LEDGER_MODULE.context_state_path(repo)
            self.assertTrue(state_path.exists())
            self.assertIn(".git", state_path.parts)
            self.assertFalse((repo / ".context-ledger/context-state.json").exists())
            self.assertFalse((repo / "docs/changes/.active-handoff").exists())
            status = self.run_git(repo, "status", "--porcelain").stdout
            self.assertNotIn("context-state.json", status)
            self.assertNotIn(".active-handoff", status)
            self.assertNotIn(final_handoff.relative_to(repo).as_posix(), status.replace("\\", "/"))
            text = handoff.read_text(encoding="utf-8")
            self.assertEqual("Alice", LEDGER_MODULE.field_value(text, "Actor"))
            self.assertEqual("main", LEDGER_MODULE.field_value(text, "Branch"))
            self.assertRegex(LEDGER_MODULE.field_value(text, "Handoff ID"), r"^\d{14}-alice-[0-9a-f]{10}$")
            self.assertIn("-alice-", final_handoff.name)

    def test_evidence_quality_records_git_paths_and_real_verification(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            started = self.run_ledger(
                repo,
                "start",
                "--title",
                "Repair service behavior",
                "--feature",
                "service",
                "--language",
                "zh-CN",
            )
            handoff = private_draft(repo, started)
            final_handoff = publish_target(repo, started)
            source = repo / "src/service.py"
            source.write_text("VALUE = 2\n", encoding="utf-8")
            self.fill_handoff(handoff, "src/service.py", "docs/specs/service.md")

            verified = self.run_ledger(
                repo,
                "verify",
                "--",
                sys.executable,
                "-c",
                "import sys; print(sys.argv[-1])",
                "--token",
                "super-secret-value",
            )
            self.assertIn("Recorded passed verification", verified.stdout)
            captured = self.run_ledger(repo, "evidence")
            self.assertIn("src/service.py", captured.stdout)
            text = handoff.read_text(encoding="utf-8")
            self.assertEqual("zh-CN", LEDGER_MODULE.field_value(text, "Language"))
            self.assertIn("- Status: passed", text)
            self.assertIn("<redacted>", text)
            self.assertNotIn("super-secret-value", text)
            self.assertIn("content not persisted", text)
            self.assertIn("`src/service.py`", LEDGER_MODULE.managed_text(
                text, LEDGER_MODULE.EVIDENCE_START, LEDGER_MODULE.EVIDENCE_END
            ))

            self.run_ledger(
                repo,
                "finish",
                "--no-spec",
                "--reason",
                "This focused test fixture has no durable product specification to maintain.",
            )
            self.assertFalse(handoff.exists())
            self.assertEqual("completed", field_from_file(final_handoff, "Status"))
            degraded = re.sub(
                r"(?m)^Before:.*$", "Before: vague", final_handoff.read_text(encoding="utf-8"), count=1
            )
            final_handoff.write_text(degraded, encoding="utf-8")
            strict = self.run_ledger(repo, "check", "--strict", expected=2)
            self.assertIn("requires a substantive Before", strict.stderr)

    def test_failed_verification_blocks_quality_handoff_until_a_check_passes(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            started = self.run_ledger(
                repo, "start", "--title", "Repair validation", "--language", "en"
            )
            handoff = private_draft(repo, started)
            self.fill_handoff(handoff, "src/validation.py", "docs/specs/validation.md")
            self.run_ledger(
                repo, "verify", "--", sys.executable, "-c", "raise SystemExit(3)", expected=1
            )
            blocked = self.run_ledger(
                repo,
                "finish",
                "--no-spec",
                "--reason",
                "This fixture intentionally has no durable product specification.",
                expected=2,
            )
            self.assertIn("failed verification", blocked.stderr)
            self.run_ledger(repo, "verify", "--", sys.executable, "-c", "print('passed')")
            self.run_ledger(
                repo,
                "finish",
                "--no-spec",
                "--reason",
                "This fixture intentionally has no durable product specification.",
            )

    def test_quality_handoff_accepts_substantive_verification_exception(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            started = self.run_ledger(
                repo, "start", "--title", "Document external behavior", "--language", "en"
            )
            handoff = private_draft(repo, started)
            self.fill_handoff(handoff, "config/external-service.json", "docs/specs/external-service.md")
            self.run_ledger(
                repo,
                "verify",
                "--not-run",
                "--reason",
                "The external sandbox is unavailable in this isolated test environment.",
            )
            self.run_ledger(
                repo,
                "finish",
                "--no-spec",
                "--reason",
                "This fixture intentionally has no durable product specification.",
            )

    def test_quality_handoff_rejects_auto_language_and_vague_claims(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            started = self.run_ledger(repo, "start", "--title", "Repair vague behavior")
            handoff = private_draft(repo, started)
            text = handoff.read_text(encoding="utf-8")
            text = re.sub(r"TODO:[^|`\r\n]*", "updated relevant files", text)
            handoff.write_text(text, encoding="utf-8")
            blocked = self.run_ledger(
                repo,
                "finish",
                "--no-spec",
                "--reason",
                "This fixture intentionally has no durable product specification.",
                expected=2,
            )
            self.assertIn("Language must resolve", blocked.stderr)
            self.assertIn("vague standalone claim", blocked.stderr)

    def test_evidence_quality_validates_specs_and_context_pack_size(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            source = repo / "src/validation.py"
            source.parent.mkdir(parents=True)
            source.write_text("ENABLED = True\n", encoding="utf-8")
            self.run_ledger(repo, "init")

            spec = repo / "docs/specs/validation.md"
            shutil.copy2(repo / ".context-ledger/templates/spec-template.md", spec)
            invalid = self.run_ledger(repo, "check", "--strict", expected=2)
            self.assertIn("Stable spec still contains template placeholders", invalid.stderr)
            self.fill_spec(spec)
            self.run_ledger(repo, "check", "--strict")

            created = self.run_ledger(
                repo,
                "pack",
                "--feature",
                "validation",
                "--language",
                "en",
                "--file",
                "src/validation.py",
                "--spec",
                "docs/specs/validation.md",
            )
            pack = repo / created.stdout.splitlines()[0]
            self.fill_context_pack(pack)
            config_path = repo / ".context-ledger/config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["quality"]["max_context_pack_lines"] = 60
            config_path.write_text(json.dumps(config), encoding="utf-8")
            pack.write_text(
                pack.read_text(encoding="utf-8") + "\n".join("Extra evidence line." for _ in range(30)) + "\n",
                encoding="utf-8",
            )
            oversized = self.run_ledger(repo, "focus", "--feature", "validation", expected=2)
            self.assertIn("configured maximum is 60", oversized.stderr)

    def test_v2_git_state_and_active_pointer_migrate_to_private_v8_draft(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            started = self.run_ledger(
                repo, "start", "--title", "Repair authentication", "--feature", "authentication"
            )
            original_draft = private_draft(repo, started)
            legacy_handoff = publish_target(repo, started)
            legacy_handoff.parent.mkdir(parents=True, exist_ok=True)
            legacy_handoff.write_text(original_draft.read_text(encoding="utf-8"), encoding="utf-8")
            original_draft.unlink()
            handoff_rel = legacy_handoff.relative_to(repo).as_posix()
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

            before_preview = self.repository_snapshot(repo)
            preview = self.run_ledger(repo, "init", "--dry-run")
            self.assertEqual(before_preview, self.repository_snapshot(repo))
            self.assertIn("MIGRATE configuration schema v2 to v8", preview.stdout)
            self.assertIn("MIGRATE workspace state to session-isolated storage", preview.stdout)
            self.assertTrue(legacy_handoff.exists())
            self.assertTrue(legacy_state.exists())
            self.assertTrue(legacy_pointer.exists())

            migrated = self.run_ledger(repo, "init")
            preview_operations = [
                line for line in preview.stdout.splitlines()
                if line.startswith(("CREATE ", "UPDATE ", "DELETE ", "MIGRATE "))
            ]
            migrated_operations = [
                line for line in migrated.stdout.splitlines()
                if line.startswith(("CREATE ", "UPDATE ", "DELETE ", "MIGRATE "))
            ]
            self.assertEqual(preview_operations, migrated_operations)
            self.assertIn("Migrated shared pre-v0.3 state to workspace-local state", migrated.stdout)
            state = json.loads(LEDGER_MODULE.context_state_path(repo).read_text(encoding="utf-8"))
            sessions = list(state["task_sessions"].values())
            self.assertEqual(1, len(sessions))
            migrated_draft = LEDGER_MODULE.validate_private_draft_path(repo, sessions[0]["draft"])
            self.assertTrue(migrated_draft.is_file())
            self.assertEqual(handoff_rel, sessions[0]["publish_path"])
            self.assertEqual("active", sessions[0]["status"])
            self.assertEqual(LEDGER_MODULE.current_principal(repo), sessions[0]["owner_principal"])
            self.assertEqual([], sessions[0]["grants"])
            self.assertFalse(legacy_handoff.exists())
            self.assertFalse(legacy_state.exists())
            self.assertFalse(legacy_pointer.exists())
            self.assertEqual(8, json.loads(config_path.read_text(encoding="utf-8"))["schema_version"])

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
            main_record = main_state["task_sessions"][session_from_result(main_start)]
            other_record = other_state["task_sessions"][session_from_result(other_start)]
            self.assertTrue(LEDGER_MODULE.validate_private_draft_path(repo, main_record["draft"]).is_file())
            self.assertTrue(LEDGER_MODULE.validate_private_draft_path(worktree, other_record["draft"]).is_file())
            self.assertEqual("withdrawals", main_record["feature"])
            self.assertEqual("authentication", other_record["feature"])

    def test_active_private_draft_never_updates_shared_derived_files(self):
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
            handoff = private_draft(repo, started)
            target = publish_target(repo, started)
            self.assertTrue(handoff.exists())
            self.assertFalse(target.exists())
            self.assertEqual(before_readme, readme.read_text(encoding="utf-8"))
            self.assertEqual(before_index, change_index.read_text(encoding="utf-8"))
            self.assertFalse((target.parent / "README.md").exists())
            skipped = self.run_ledger(repo, "sync")
            self.assertIn("Skipped shared README", skipped.stdout)

            self.run_ledger(repo, "sync", "--derived")
            self.assertFalse((target.parent / "README.md").exists())
            self.assertNotIn("Repair authentication", readme.read_text(encoding="utf-8"))

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
                    state = LEDGER_MODULE.load_context_state(repo)
                    first_session = next(iter(state["task_sessions"]))
                    first_record = state["task_sessions"][first_session]
                    first = LEDGER_MODULE.validate_private_draft_path(repo, first_record["draft"])
                    first_target = repo / first_record["publish_path"]
                    original = first.read_text(encoding="utf-8")
                    self.assertEqual(0, LEDGER_MODULE.start_change(repo, "修复接口"))
                    state = LEDGER_MODULE.load_context_state(repo)
                    second_session = next(item for item in state["task_sessions"] if item != first_session)
                    second_record = state["task_sessions"][second_session]
                    second = LEDGER_MODULE.validate_private_draft_path(repo, second_record["draft"])
                    second_target = repo / second_record["publish_path"]
            self.assertNotEqual(first, second)
            self.assertNotEqual(first_target, second_target)
            self.assertEqual(original, first.read_text(encoding="utf-8"))

    def test_finish_requires_content_and_explicit_spec_exception(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            start = self.run_ledger(repo, "start", "--title", "No stable spec change")
            handoff = private_draft(repo, start)
            session_id = session_from_result(start)
            handoff.write_text(
                f"# No stable spec change\n\nStatus: active\nHandoff ID: {session_id}\nStarted: 2026-08-11\nCompleted:\nSpecs: none\n\n"
                "## Intent\n\n\n## Changed behavior\n\n\n## Code paths\n\n\n"
                "## Boundaries and risks\n\n\n## Verification\n\n\n## Documentation updates\n",
                encoding="utf-8",
            )
            self.run_ledger(repo, "finish", expected=2)
            valid = (
                f"# No stable spec change\n\nStatus: active\nHandoff ID: {session_id}\nStarted: 2026-08-11\nCompleted:\nSpecs: none\n\n"
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

    def test_coverage_globs_are_validated_as_repository_relative(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            config_path = repo / ".context-ledger/config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["coverage"]["ignore_globs"] = ["../outside/**"]
            config_path.write_text(json.dumps(config), encoding="utf-8")
            result = self.run_ledger(repo, "check", expected=2)
            self.assertIn("cannot escape the repository", result.stderr)

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

    def test_legacy_repository_migrates_to_v8_without_losing_docs(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            project_context = repo / "docs/ai/project-context.md"
            project_context.write_text(
                re.sub(
                    r"TODO: Summarize what this repository delivers and who uses it[^\n]*",
                    "Preserved project purpose.",
                    project_context.read_text(encoding="utf-8"),
                    count=1,
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
            self.assertEqual(8, migrated["schema_version"])
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

    def test_nested_git_repositories_and_worktrees_are_not_modules(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            module = repo / "apps/primary"
            module.mkdir(parents=True)
            (module / "package.json").write_text('{"name":"primary"}\n', encoding="utf-8")

            nested_repo = repo / "checkouts/source-checkout"
            nested_repo.mkdir(parents=True)
            (nested_repo / ".git").mkdir()
            (nested_repo / "package.json").write_text('{"name":"nested"}\n', encoding="utf-8")

            nested_worktree = repo / "worktrees/task"
            nested_module = nested_worktree / "apps/duplicate"
            nested_module.mkdir(parents=True)
            (nested_worktree / ".git").write_text("gitdir: C:/tmp/worktree\n", encoding="utf-8")
            (nested_worktree / "package.json").write_text('{"name":"worktree"}\n', encoding="utf-8")
            (nested_module / "package.json").write_text('{"name":"duplicate"}\n', encoding="utf-8")

            self.run_ledger(repo, "init")
            config = json.loads((repo / ".context-ledger/config.json").read_text(encoding="utf-8"))
            self.assertEqual(["apps/primary"], [item["path"] for item in config["modules"]])
            self.assertFalse((nested_repo / "README.md").exists())
            self.assertFalse((nested_module / "README.md").exists())

    def test_legacy_month_layout_reuses_index_and_removes_leaf_indexes(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            month = repo / "docs/changes/2026-07"
            first = month / "2026-07-14/data-import/handoff.md"
            second = month / "2026-07-15/repair-cache.md"
            first.parent.mkdir(parents=True)
            second.parent.mkdir(parents=True)
            first.write_text("# Import data\n\nStatus: completed\n", encoding="utf-8")
            second.write_text("# Repair cache\n\nStatus: completed\n", encoding="utf-8")
            legacy_index = month / "index.md"
            legacy_index.write_text("# Existing July index\n\nHuman-maintained history.\n", encoding="utf-8")

            generated = (
                "# Changes in 2026-07-2026-07-14-data-import\n\n"
                "<!-- repo-context-ledger:start -->\n"
                "## Changes in 2026-07-2026-07-14-data-import\n\n"
                "- [Import data](handoff.md) — completed\n"
                "<!-- repo-context-ledger:end -->\n"
            )
            stale_leaf = first.parent / "README.md"
            stale_leaf.write_text(generated, encoding="utf-8")
            human_readme = second.parent / "README.md"
            human_readme.write_text("# Human notes\n\nKeep this file.\n", encoding="utf-8")
            marked_human_readme = month / "2026-07-16/README.md"
            marked_human_readme.parent.mkdir(parents=True)
            marked_human_readme.write_text(
                "# Changes in 2026-07-2026-07-16\n\n"
                "<!-- repo-context-ledger:start -->\n"
                "Human-maintained history inside markers.\n"
                "<!-- repo-context-ledger:end -->\n",
                encoding="utf-8",
            )
            changed_source = month / "2026-07-17/change.md"
            changed_source.parent.mkdir(parents=True)
            changed_source.write_text("# Renamed change\n\nStatus: completed\n", encoding="utf-8")
            changed_generated_readme = changed_source.parent / "README.md"
            changed_generated_readme.write_text(
                "# Changes in 2026-07-2026-07-17\n\n"
                "<!-- repo-context-ledger:start -->\n"
                "## Changes in 2026-07-2026-07-17\n\n"
                "- [Old change name](change.md) — completed\n"
                "<!-- repo-context-ledger:end -->\n",
                encoding="utf-8",
            )

            result = self.run_ledger(repo, "init")
            self.assertIn("Removed obsolete generated change indexes: 1", result.stdout)
            self.assertFalse(stale_leaf.exists())
            self.assertEqual("# Human notes\n\nKeep this file.\n", human_readme.read_text(encoding="utf-8"))
            self.assertTrue(marked_human_readme.exists())
            self.assertTrue(changed_generated_readme.exists())
            self.assertEqual(
                "# Existing July index\n\nHuman-maintained history.\n",
                legacy_index.read_text(encoding="utf-8"),
            )
            self.assertFalse((month / "README.md").exists())
            root_index = (repo / "docs/changes/README.md").read_text(encoding="utf-8")
            self.assertIn("[2026-07](2026-07/index.md) — 3 changes", root_index)

    def test_mixed_month_layouts_share_one_existing_month_index(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            legacy_change = repo / "docs/changes/2026-07/2026-07-14/legacy.md"
            native_change = repo / "docs/changes/2026/07/native.md"
            legacy_change.parent.mkdir(parents=True)
            native_change.parent.mkdir(parents=True)
            legacy_change.write_text("# Legacy\n\nStatus: completed\n", encoding="utf-8")
            native_change.write_text("# Native\n\nStatus: completed\n", encoding="utf-8")
            legacy_index = repo / "docs/changes/2026-07/index.md"
            legacy_index.write_text("# Existing index\n", encoding="utf-8")

            self.run_ledger(repo, "init")
            root_index = (repo / "docs/changes/README.md").read_text(encoding="utf-8")
            self.assertEqual(1, root_index.count("[2026-07]"))
            self.assertIn("[2026-07](2026-07/index.md) — 2 changes", root_index)
            self.assertFalse((repo / "docs/changes/2026/07/README.md").exists())
            self.assertEqual("# Existing index\n", legacy_index.read_text(encoding="utf-8"))

    def test_non_month_directories_keep_their_leaf_indexes(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            change = repo / "docs/changes/releases/v1/change.md"
            change.parent.mkdir(parents=True)
            change.write_text("# Release change\n\nStatus: completed\n", encoding="utf-8")

            self.run_ledger(repo, "init")
            self.assertTrue((change.parent / "README.md").exists())
            self.assertFalse((repo / "docs/changes/releases/README.md").exists())

    def test_native_month_layout_still_uses_one_managed_readme(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            first = repo / "docs/changes/2026/07/task/handoff.md"
            second = repo / "docs/changes/2026/07/repair.md"
            first.parent.mkdir(parents=True)
            second.parent.mkdir(parents=True, exist_ok=True)
            first.write_text("# Task\n\nStatus: completed\n", encoding="utf-8")
            second.write_text("# Repair\n\nStatus: completed\n", encoding="utf-8")

            self.run_ledger(repo, "init")
            month_index = repo / "docs/changes/2026/07/README.md"
            self.assertTrue(month_index.exists())
            self.assertIn("Task", month_index.read_text(encoding="utf-8"))
            self.assertIn("Repair", month_index.read_text(encoding="utf-8"))
            self.assertFalse((first.parent / "README.md").exists())
            root_index = (repo / "docs/changes/README.md").read_text(encoding="utf-8")
            self.assertIn("[2026-07](2026/07/README.md) — 2 changes", root_index)

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

    def test_context_plan_bounds_required_reads(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            (repo / "src").mkdir()
            source = repo / "src/router.py"
            source.write_text("def route():\n    return 'ok'\n", encoding="utf-8")
            spec_paths = []
            for index in range(1, 5):
                relative = f"docs/specs/router-{index}.md"
                path = repo / relative
                path.write_text(
                    f"# Router contract {index}\n\nStable routing contract {index}.\n",
                    encoding="utf-8",
                )
                spec_paths.append(relative)
            command = [
                "pack", "--feature", "bounded-router", "--title", "Bounded Router",
                "--file", "src/router.py",
            ]
            for relative in spec_paths:
                command.extend(["--spec", relative])
            self.run_ledger(repo, *command)

            result = self.run_ledger(repo, "context", "--query", "bounded router")

            self.assertIn("Context Bundle: context-bundle-v1", result.stdout)
            required = result.stdout.split("Required reads:\n", 1)[1].split("Change summaries:\n", 1)[0]
            self.assertIn("- pack: docs/ai/context-packs/bounded-router.md", required)
            self.assertIn("- spec: docs/specs/router-1.md", required)
            self.assertIn("- spec: docs/specs/router-2.md", required)
            self.assertNotIn("docs/specs/router-3.md", required)
            self.assertNotIn("docs/specs/router-4.md", required)
            self.assertIn("Budget: files 3/3", result.stdout)

    def test_context_plan_json_is_stable_and_repository_relative(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            (repo / "src").mkdir()
            (repo / "src/router.py").write_text("def route():\n    return 'ok'\n", encoding="utf-8")
            spec = repo / "docs/specs/router.md"
            spec.write_text("# Router\n\nStable routing contract.\n", encoding="utf-8")
            self.run_ledger(
                repo,
                "pack", "--feature", "bounded-router", "--title", "Bounded Router",
                "--file", "src/router.py", "--spec", "docs/specs/router.md",
            )

            result = self.run_ledger(
                repo, "context", "--query", "bounded router", "--format", "json"
            )
            plan = json.loads(result.stdout)

            self.assertEqual("context-bundle-v1", plan["schema"])
            self.assertEqual("bounded router", plan["query"])
            self.assertEqual("docs/ai/context-packs/bounded-router.md", plan["primary_pack"])
            self.assertEqual(
                ["pack", "spec"],
                [item["kind"] for item in plan["required_reads"]],
            )
            self.assertEqual(
                [
                    "docs/ai/context-packs/bounded-router.md",
                    "docs/specs/router.md",
                ],
                [item["path"] for item in plan["required_reads"]],
            )
            self.assertEqual(2, plan["budget"]["used_files"])
            self.assertEqual(3, plan["budget"]["max_files"])
            self.assertFalse(plan["budget"]["truncated"])
            self.assertEqual(1, plan["metrics"]["packs_considered"])
            self.assertEqual(2, plan["metrics"]["required_files"])
            self.assertGreaterEqual(plan["metrics"]["elapsed_ms"], 0)
            self.assertNotIn(str(repo), result.stdout)

    def test_context_router_private_cache_reuses_and_invalidates_entries(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            created = self.run_ledger(
                repo,
                "pack", "--feature", "service-route", "--title", "Service Route",
                "--file", "src/service.py",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])

            cold = json.loads(self.run_ledger(
                repo, "context", "--query", "service route", "--format", "json"
            ).stdout)
            cache = LEDGER_MODULE.router_cache_path(repo)
            self.assertIsNotNone(cache)
            self.assertTrue(cache.is_file())
            self.assertEqual("cold", cold["metrics"]["cache"]["state"])
            self.assertTrue(cold["metrics"]["cache"]["written"])
            self.assertNotIn(
                "repo-context-ledger/cache",
                self.run_git(repo, "status", "--porcelain").stdout.replace("\\", "/"),
            )

            warm = json.loads(self.run_ledger(
                repo, "context", "--query", "service route", "--format", "json"
            ).stdout)
            self.assertEqual(cold["primary_pack"], warm["primary_pack"])
            self.assertEqual(cold["required_reads"], warm["required_reads"])
            self.assertEqual("warm", warm["metrics"]["cache"]["state"])
            self.assertGreaterEqual(warm["metrics"]["cache"]["pack_hits"], 1)
            self.assertGreaterEqual(warm["metrics"]["cache"]["digest_hits"], 1)

            cache.write_text("{broken cache", encoding="utf-8")
            rebuilt = json.loads(self.run_ledger(
                repo, "context", "--query", "service route", "--format", "json"
            ).stdout)
            self.assertEqual(cold["primary_pack"], rebuilt["primary_pack"])
            self.assertEqual("rebuilt", rebuilt["metrics"]["cache"]["state"])

            (repo / "src/service.py").write_text("VALUE = 200\n", encoding="utf-8")
            invalidated = json.loads(self.run_ledger(
                repo, "context", "--query", "service route", "--format", "json"
            ).stdout)
            self.assertEqual("stale", invalidated["selection"]["fingerprints"])
            self.assertGreaterEqual(invalidated["metrics"]["cache"]["digest_misses"], 1)

    def test_context_baseline_boosts_the_pack_changed_since_merge_base(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            alpha = repo / "src/alpha.py"
            beta = repo / "src/beta.py"
            alpha.write_text("VALUE = 'alpha'\n", encoding="utf-8")
            beta.write_text("VALUE = 'beta'\n", encoding="utf-8")
            for feature, title, source in (
                ("alpha-route", "Alpha Route", "src/alpha.py"),
                ("beta-route", "Beta Route", "src/beta.py"),
            ):
                created = self.run_ledger(
                    repo, "pack", "--feature", feature, "--title", title, "--file", source
                )
                self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_git(repo, "add", "-A")
            self.run_git(repo, "commit", "-m", "Add two synthetic routes")
            self.run_git(repo, "switch", "-c", "feature/beta-maintenance")
            beta.write_text("VALUE = 'beta-2'\n", encoding="utf-8")
            self.run_git(repo, "add", "src/beta.py")
            self.run_git(repo, "commit", "-m", "Change beta route")

            plan = json.loads(self.run_ledger(
                repo,
                "context", "--query", "maintenance request", "--baseline", "main",
                "--format", "json",
            ).stdout)
            self.assertEqual("docs/ai/context-packs/beta-route.md", plan["primary_pack"])
            self.assertIn("pr-baseline-overlap", plan["selection"]["reasons"])
            self.assertEqual("resolved", plan["baseline"]["status"])
            self.assertEqual(["src/beta.py"], plan["baseline"]["relevant_paths"])
            self.assertEqual(1, plan["baseline"]["changed_path_count"])

            unresolved = json.loads(self.run_ledger(
                repo,
                "context", "--query", "beta route", "--baseline", "missing/ref",
                "--format", "json",
            ).stdout)
            self.assertEqual("unresolved", unresolved["baseline"]["status"])
            self.assertTrue(unresolved["baseline"]["warnings"])
            self.assertNotIn(str(repo), json.dumps(unresolved))

    def test_resume_capsule_omits_legacy_evidence_outside_selected_pack_scope(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            self.run_git(repo, "config", "repo-context-ledger.principal", "alice-profile")
            relevant = repo / "src/announcements/worker.py"
            unrelated = repo / "src/assets/registry.py"
            relevant.parent.mkdir(parents=True)
            unrelated.parent.mkdir(parents=True)
            relevant.write_text("LIMIT = 1\n", encoding="utf-8")
            unrelated.write_text("ASSETS = 1\n", encoding="utf-8")
            self.run_git(repo, "add", "src/announcements/worker.py", "src/assets/registry.py")
            self.run_git(repo, "commit", "-m", "Add synthetic feature files")
            started = self.run_ledger(
                repo,
                "start", "--title", "Announcement throttling",
                "--feature", "announcement-throttling", "--tool", "codex",
            )
            session = session_from_result(started)
            relevant.write_text("LIMIT = 2\n", encoding="utf-8")
            unrelated.write_text("ASSETS = 2\n", encoding="utf-8")
            created = self.run_ledger(
                repo,
                "pack", "--feature", "announcement-throttling",
                "--title", "Announcement Throttling",
                "--file", "src/announcements/worker.py",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_ledger(
                repo,
                "evidence", "--session", session,
                "--path", "src/announcements/worker.py",
                "--path", "src/assets/registry.py",
            )
            self.run_ledger(
                repo,
                "checkpoint", "--session", session,
                "--summary", "Synthetic announcement throttling change is ready for focused review.",
                "--next", "Verify the announcement worker boundary.",
            )

            plan = json.loads(self.run_ledger(
                repo,
                "context", "--query", "continue announcement throttling",
                "--tool", "cursor", "--format", "json",
            ).stdout)
            capsule = plan["resume"]["capsule"]
            self.assertEqual(["src/announcements/worker.py"], capsule["evidence_paths"])
            self.assertEqual(1, capsule["omitted_evidence_paths"])
            self.assertNotIn("src/assets/registry.py", json.dumps(capsule))
            self.assertTrue(any("omitted" in item for item in capsule["warnings"]))

    def test_context_plan_uses_change_metadata_without_loading_change_bodies(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            (repo / "src").mkdir()
            (repo / "src/router.py").write_text("def route():\n    return 'ok'\n", encoding="utf-8")
            self.run_ledger(
                repo,
                "pack", "--feature", "bounded-router", "--title", "Bounded Router",
                "--file", "src/router.py",
            )
            change = repo / "docs/changes/2026/08/20260801-router.md"
            change.parent.mkdir(parents=True, exist_ok=True)
            change.write_text(
                "# 修复历史路由\n\n"
                "Status: completed\n"
                "Feature: bounded-router\n"
                "Quality profile: evidence-v1\n"
                "Handoff ID: 20260801-router\n"
                "Completed: 2026-08-01T12:30:00+08:00\n\n"
                "## Changed behavior\n\n"
                "After: Routes now preserve the bounded selection contract.\n\n"
                "BODY_MUST_STAY_COLD\n\n"
                "<!-- repo-context-ledger:evidence:start -->\n"
                "## Git change evidence\n\n"
                "- Changed paths:\n"
                "  - `src/router.py`\n"
                "<!-- repo-context-ledger:evidence:end -->\n",
                encoding="utf-8",
            )
            self.run_ledger(repo, "manifest", "sync")

            result = self.run_ledger(
                repo, "context", "--query", "bounded router", "--format", "json"
            )
            plan = json.loads(result.stdout)

            self.assertEqual(
                [
                    {
                        "id": "20260801-router",
                        "path": "docs/changes/2026/08/20260801-router.md",
                        "title": "修复历史路由",
                        "feature": "bounded-router",
                        "date": "2026-08-01",
                        "summary": "Routes now preserve the bounded selection contract.",
                        "evidence_paths": ["src/router.py"],
                        "status": "completed",
                    }
                ],
                plan["change_summaries"],
            )
            self.assertIn("\\u4fee\\u590d", result.stdout)
            self.assertNotIn("BODY_MUST_STAY_COLD", result.stdout)
            self.assertNotIn(
                "docs/changes/2026/08/20260801-router.md",
                [item["path"] for item in plan["required_reads"]],
            )

    def test_context_plan_does_not_grow_with_unrelated_change_history(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            (repo / "src").mkdir()
            (repo / "src/router.py").write_text("def route():\n    return 'ok'\n", encoding="utf-8")
            self.run_ledger(
                repo,
                "pack", "--feature", "bounded-router", "--title", "Bounded Router",
                "--file", "src/router.py",
            )
            before = json.loads(
                self.run_ledger(
                    repo, "context", "--query", "bounded router", "--format", "json"
                ).stdout
            )
            history = repo / "docs/changes/2026/08"
            history.mkdir(parents=True, exist_ok=True)
            for index in range(1000):
                (history / f"historical-{index:04d}.md").write_text(
                    f"# Unrelated historical change {index}\n\nCold body {index}.\n",
                    encoding="utf-8",
                )

            after = json.loads(
                self.run_ledger(
                    repo, "context", "--query", "bounded router", "--format", "json"
                ).stdout
            )

            self.assertEqual(before["primary_pack"], after["primary_pack"])
            self.assertEqual(before["required_reads"], after["required_reads"])
            self.assertEqual(before["change_summaries"], after["change_summaries"])
            self.assertEqual(before["budget"], after["budget"])
            self.assertEqual(
                before["metrics"]["packs_considered"],
                after["metrics"]["packs_considered"],
            )

    def test_context_plan_output_budget_holds_with_one_hundred_unrelated_packs(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            (repo / "src").mkdir()
            (repo / "src/router.py").write_text("def route():\n    return 'ok'\n", encoding="utf-8")
            self.run_ledger(
                repo,
                "pack", "--feature", "bounded-router", "--title", "Bounded Router",
                "--file", "src/router.py",
            )
            target = repo / "docs/ai/context-packs/bounded-router.md"
            template = target.read_text(encoding="utf-8")
            for index in range(100):
                feature = f"unrelated-{index:03d}"
                text = template.replace("bounded-router", feature).replace(
                    "Bounded Router", f"Unrelated Feature {index:03d}"
                )
                (target.parent / f"{feature}.md").write_text(text, encoding="utf-8")

            plan = json.loads(
                self.run_ledger(
                    repo, "context", "--query", "bounded router", "--format", "json"
                ).stdout
            )

            self.assertEqual("docs/ai/context-packs/bounded-router.md", plan["primary_pack"])
            self.assertLessEqual(plan["budget"]["used_files"], plan["budget"]["max_files"])
            self.assertLessEqual(
                plan["budget"]["used_characters"], plan["budget"]["max_characters"]
            )
            self.assertEqual([], plan["optional_candidates"])
            self.assertEqual(101, plan["metrics"]["packs_available"])
            self.assertEqual(101, plan["metrics"]["packs_considered"])

    def test_reverse_index_bounds_fingerprint_checks_for_unique_pack_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            sources = repo / "src/synthetic"
            sources.mkdir(parents=True)
            first = sources / "route_000.py"
            first.write_text("MARKER = '000'\n", encoding="utf-8")
            created = self.run_ledger(
                repo,
                "pack", "--feature", "synthetic-route-000",
                "--title", "Synthetic Marker 000",
                "--file", "src/synthetic/route_000.py",
            )
            first_pack = repo / created.stdout.splitlines()[0]
            template = first_pack.read_text(encoding="utf-8")
            first_digest = LEDGER_MODULE.file_digest(first, repo)
            for index in range(1, 59):
                marker = f"{index:03d}"
                source = sources / f"route_{marker}.py"
                source.write_text(f"MARKER = '{marker}'\n", encoding="utf-8")
                digest = LEDGER_MODULE.file_digest(source, repo)
                text = template.replace("synthetic-route-000", f"synthetic-route-{marker}")
                text = text.replace("Synthetic Marker 000", f"Synthetic Marker {marker}")
                text = text.replace("src/synthetic/route_000.py", f"src/synthetic/route_{marker}.py")
                text = text.replace(first_digest, digest)
                (first_pack.parent / f"synthetic-route-{marker}.md").write_text(
                    text,
                    encoding="utf-8",
                )

            plan = json.loads(self.run_ledger(
                repo,
                "context", "--query", "Synthetic Marker 037", "--format", "json",
            ).stdout)
            self.assertEqual(
                "docs/ai/context-packs/synthetic-route-037.md",
                plan["primary_pack"],
            )
            self.assertEqual(59, plan["metrics"]["packs_available"])
            self.assertLessEqual(plan["metrics"]["packs_considered"], 5)
            self.assertFalse(plan["metrics"]["reverse_index"]["fallback"])

    def test_context_router_prefers_live_pack_feature_and_tracked_path(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            (repo / "src").mkdir()
            authority = repo / "src/authority.go"
            authority.write_text("package authority\n", encoding="utf-8")
            worker = repo / "src/worker.go"
            worker.write_text("package worker\n", encoding="utf-8")
            self.run_ledger(
                repo, "pack", "--feature", "authority", "--title", "Asset Authority",
                "--file", "src/authority.go", "--spec", "docs/specs/README.md",
            )
            self.run_ledger(
                repo, "pack", "--feature", "announcement-worker", "--title", "Announcement Worker",
                "--file", "src/worker.go", "--spec", "docs/specs/README.md",
            )
            long_spec = repo / "docs/specs/market-data-to-spread-pipeline.md"
            long_spec.write_text(
                "# 17 所行情采集与差价计算链路\n\n"
                "This long document mentions Asset Authority many times. "
                "Asset Authority Asset Authority Asset Authority.\n",
                encoding="utf-8",
            )
            result = self.run_ledger(repo, "context", "--query", "Asset Authority")
            self.assertIn("Primary pack: docs/ai/context-packs/authority.md", result.stdout)
            self.assertIn("Feature: authority", result.stdout)
            self.assertIn("Why:", result.stdout)
            self.assertNotIn("market-data-to-spread-pipeline.md", result.stdout)
            self.assertNotIn("\tscore=", result.stdout)

    def test_context_router_prefers_current_pack_over_superseded_pack(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            (repo / "src").mkdir()
            source = repo / "src/authority.go"
            source.write_text("package authority\n", encoding="utf-8")
            self.run_ledger(
                repo, "pack", "--feature", "legacy-authority", "--title", "Legacy Authority",
                "--file", "src/authority.go",
            )
            self.run_ledger(
                repo, "pack", "--feature", "authority", "--title", "Asset Authority",
                "--file", "src/authority.go",
            )
            legacy = repo / "docs/ai/context-packs/legacy-authority.md"
            text = legacy.read_text(encoding="utf-8")
            text = text.replace("Status: current", "Status: superseded")
            if "Superseded by:" not in text:
                text = text.replace("Status: superseded", "Status: superseded\nSuperseded by: authority")
            legacy.write_text(text, encoding="utf-8")
            result = self.run_ledger(repo, "context", "--query", "authority")
            self.assertIn("Primary pack: docs/ai/context-packs/authority.md", result.stdout)
            self.assertNotIn("Primary pack: docs/ai/context-packs/legacy-authority.md", result.stdout)

    def test_context_router_never_selects_a_superseded_pack(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            (repo / "src").mkdir()
            (repo / "src/legacy.py").write_text("VALUE = 1\n", encoding="utf-8")
            created = self.run_ledger(
                repo, "pack", "--feature", "legacy-only", "--file", "src/legacy.py"
            )
            legacy = repo / created.stdout.splitlines()[0]
            legacy.write_text(
                legacy.read_text(encoding="utf-8").replace(
                    "Status: current", "Status: superseded\nSuperseded by: replacement"
                ),
                encoding="utf-8",
            )

            result = self.run_ledger(
                repo, "context", "--query", "legacy only", expected=1
            )
            self.assertNotIn("Primary pack:", result.stdout)

    def test_changed_scope_strict_check_ignores_unrelated_existing_debt(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.init_git_repo(repo)
            legacy = repo / "docs/ai/legacy-note.md"
            legacy.write_text(
                "# Legacy note\n\n[Old missing target](missing-old-target.md)\n",
                encoding="utf-8",
            )
            self.run_git(repo, "add", "docs/ai/legacy-note.md")
            self.run_git(repo, "commit", "-m", "Record existing documentation debt")
            base = self.run_git(repo, "rev-parse", "HEAD").stdout.strip()
            readme = repo / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8") + "\nValid branch note.\n", encoding="utf-8")

            changed = self.run_ledger(repo, "check", "--strict", "--changed-since", base)
            self.assertIn("Changed-scope Repo Context Ledger check passed.", changed.stdout)

            full = self.run_ledger(repo, "check", "--strict", expected=2)
            self.assertIn("Broken link in docs/ai/legacy-note.md", full.stderr)

    def test_changed_scope_strict_check_rejects_new_broken_link(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.init_git_repo(repo)
            base = self.run_git(repo, "rev-parse", "HEAD").stdout.strip()
            self.run_git(repo, "switch", "-c", "feature/new-doc")
            new_note = repo / "docs/ai/new-note.md"
            new_note.write_text(
                "# New note\n\n[Missing target](missing-new-target.md)\n",
                encoding="utf-8",
            )

            changed = self.run_ledger(
                repo, "check", "--strict", "--changed-since", base, expected=2
            )
            self.assertIn("Broken link in docs/ai/new-note.md", changed.stderr)

    def test_changed_scope_strict_check_rejects_changed_stale_pack(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.init_git_repo(repo)
            self.run_ledger(
                repo,
                "pack", "--feature", "service", "--title", "Service",
                "--file", "src/service.py",
            )
            pack = repo / "docs/ai/context-packs/service.md"
            self.fill_context_pack(pack)
            self.run_git(repo, "add", "-A")
            self.run_git(repo, "commit", "-m", "Add service context")
            base = self.run_git(repo, "rev-parse", "HEAD").stdout.strip()
            self.run_git(repo, "switch", "-c", "feature/stale-pack")
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")

            changed = self.run_ledger(
                repo, "check", "--strict", "--changed-since", base, expected=2
            )
            self.assertIn("Context pack is stale", changed.stderr)

    def test_discover_repo_finds_ledger_config_and_stops_at_nested_git(self):
        with tempfile.TemporaryDirectory() as raw:
            outer = Path(raw) / "outer"
            self.init_git_repo(outer, "Alice")
            inner = outer / "vendor" / "nested"
            inner.mkdir(parents=True)
            self.run_git(inner, "init", "-b", "main")
            self.assertEqual(inner.resolve(), LEDGER_MODULE.discover_repo(inner).resolve())
            child = outer / "app" / "module"
            child.mkdir(parents=True)
            self.assertEqual(outer.resolve(), LEDGER_MODULE.discover_repo(child).resolve())
            self.assertEqual(
                child.resolve(),
                LEDGER_MODULE.resolve_repo(str(child), explicit=True).resolve(),
            )

    def test_failed_verification_records_redacted_failure_capsule(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw)
            self.run_ledger(repo, "init")
            started = self.run_ledger(
                repo, "start", "--title", "Record failure capsule", "--language", "en"
            )
            handoff = private_draft(repo, started)
            self.fill_handoff(handoff, "src/service.py::Run", "docs/specs/service.md")
            self.run_ledger(
                repo,
                "verify",
                "--",
                sys.executable,
                "-c",
                (
                    "import pathlib, sys, tempfile; "
                    "home = pathlib.Path.home(); "
                    "print(f'ERROR repo={sys.argv[1]} home={home} "
                    "codex={home / \".codex\"} temp={tempfile.gettempdir()}'); "
                    "print('postgres://user:hunter2@db.internal/app'); "
                    "print('password: colon-secret-value'); "
                    "print('\\\"token\\\": \\\"json-secret-value\\\"'); "
                    "raise SystemExit('FAIL api_key whitespace-secret-value')"
                ),
                str(repo.resolve()),
                expected=1,
            )
            text = handoff.read_text(encoding="utf-8")
            self.assertIn("- Status: failed", text)
            self.assertIn("failure=", text)
            self.assertNotIn("hunter2", text)
            self.assertNotIn("colon-secret-value", text)
            self.assertNotIn("json-secret-value", text)
            self.assertNotIn("whitespace-secret-value", text)
            self.assertNotIn(str(repo.resolve()), text)
            self.assertNotIn(str(Path.home()), text)
            self.assertIn("<redacted", text)
            self.assertIn("<REPO_ROOT>", text)
            self.assertIn("<USER_HOME>", text)
            self.assertIn("<CODEX_HOME>", text)
            self.assertIn("<TEMP_DIR>", text)

            escaped = LEDGER_MODULE.verification_output_summary(
                "",
                r'ERROR payload={\"token\": \"escaped-json-secret-value\"}',
                "failed",
            )
            self.assertNotIn("escaped-json-secret-value", escaped)
            self.assertIn("<redacted>", escaped)

    def test_completed_verification_redacts_local_roots_and_escaped_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo, "Alice")
            started = self.run_ledger(
                repo,
                "start",
                "--title",
                "Redact verification paths",
                "--feature",
                "service",
                "--language",
                "en",
            )
            handoff = private_draft(repo, started)
            completed = publish_target(repo, started)
            (repo / "src/service.py").write_text("VALUE = 2\n", encoding="utf-8")
            spec = repo / "docs/specs/service.md"
            shutil.copy2(repo / ".context-ledger/templates/spec-template.md", spec)
            self.fill_spec(spec)
            self.fill_handoff(handoff, "src/service.py::VALUE", "docs/specs/service.md")

            home = Path.home()
            codex = home / ".codex"
            temp_root = Path(tempfile.gettempdir())
            repo_root = repo.resolve()
            script = (
                "import json, pathlib, sys, tempfile; "
                "home = pathlib.Path.home(); "
                "print(json.dumps({'repo': sys.argv[1], 'home': str(home), "
                "'codex': str(home / '.codex'), 'temp': tempfile.gettempdir()}))"
            )
            self.run_ledger(
                repo,
                "verify",
                "--",
                sys.executable,
                "-c",
                script,
                str(repo_root),
            )
            legacy_home = str(home).replace("\\", "\\\\")
            handoff.write_text(
                handoff.read_text(encoding="utf-8").replace(
                    LEDGER_MODULE.CHECKS_END,
                    f"- Legacy output: {legacy_home}\\\\Documents\\\\result.txt\n"
                    f"{LEDGER_MODULE.CHECKS_END}",
                ),
                encoding="utf-8",
            )
            created = self.run_ledger(
                repo,
                "pack",
                "--feature",
                "service",
                "--title",
                "Service",
                "--file",
                "src/service.py",
                "--spec",
                "docs/specs/service.md",
            )
            self.fill_context_pack(repo / created.stdout.splitlines()[0])
            self.run_ledger(repo, "evidence")
            self.run_ledger(repo, "finish", "--spec", "docs/specs/service.md")

            text = completed.read_text(encoding="utf-8")
            self.assertNotIn(str(repo), text)
            self.assertNotIn(str(repo_root), text)
            self.assertNotIn(str(home), text)
            self.assertNotIn(str(home).replace("\\", "\\\\"), text)
            self.assertNotIn(str(codex), text)
            self.assertNotIn(str(temp_root), text)
            self.assertIn("<REPO_ROOT>", text)
            self.assertIn("<USER_HOME>", text)
            self.assertIn("<CODEX_HOME>", text)
            self.assertIn("<TEMP_DIR>", text)

    def test_cited_code_path_strips_symbol_and_matches_evidence(self):
        self.assertEqual("src/service.py", LEDGER_MODULE.cited_code_path("src/service.py::Run"))
        self.assertEqual("engine/foo.go", LEDGER_MODULE.cited_code_path("engine/foo.go:12"))
        self.assertTrue(LEDGER_MODULE.evidence_path_cited("src/service.py", {"src/service.py"}))
        self.assertTrue(
            LEDGER_MODULE.evidence_path_cited("longshort-data/engine/foo.go", {"engine/foo.go"})
        )


if __name__ == "__main__":
    unittest.main()
