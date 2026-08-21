import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
CONTRACT = ROOT / "tests" / "golden" / "v0.6.0-contract.json"
STATUS_TEXT = ROOT / "tests" / "golden" / "v0.6.0-status-text.txt"
LEGACY_STATE = ROOT / "tests" / "fixtures" / "v0.6.0-legacy-context-state.json"
SPEC = importlib.util.spec_from_file_location("repo_context_ledger_baseline_runtime", LEDGER)
RUNTIME = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNTIME)


class BaselineContractTests(unittest.TestCase):
    def run_command(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(args, text=True, capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def initialize_git(self, repo: Path) -> None:
        repo.mkdir(parents=True)
        self.run_command("git", "-C", str(repo), "init", "-b", "main")
        self.run_command("git", "-C", str(repo), "config", "user.name", "Contract Tester")
        self.run_command("git", "-C", str(repo), "config", "user.email", "contract@example.test")
        (repo / "service.py").write_text("VALUE = 1\n", encoding="utf-8")

    def test_v060_command_schema_and_exit_baseline(self):
        golden = json.loads(CONTRACT.read_text(encoding="utf-8"))
        parser = RUNTIME.build_parser()
        choices = next(action.choices for action in parser._actions if action.dest == "command")
        self.assertTrue(set(golden["commands"]).issubset(choices))
        self.assertEqual(golden["config_schema"], RUNTIME.VERSION)
        self.assertEqual(golden["context_schema"], RUNTIME.CONTEXT_BUNDLE_SCHEMA)
        self.assertEqual(golden["exit_codes"]["success"], RUNTIME.EXIT_SUCCESS)
        self.assertEqual(golden["exit_codes"]["no_context_match"], RUNTIME.EXIT_NO_MATCH)
        self.assertEqual(golden["exit_codes"]["invalid_or_unhealthy"], RUNTIME.EXIT_INVALID)

    def test_init_dry_run_preserves_repository_and_private_state(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.initialize_git(repo)
            before = {path.relative_to(repo): path.read_bytes() for path in repo.rglob("*") if path.is_file()}
            private_before = RUNTIME.context_state_path(repo).exists()
            result = self.run_command(sys.executable, str(LEDGER), "--repo", str(repo), "init", "--dry-run")
            self.assertIn("Dry run only", result.stdout)
            after = {path.relative_to(repo): path.read_bytes() for path in repo.rglob("*") if path.is_file()}
            self.assertEqual(before, after)
            self.assertEqual(private_before, RUNTIME.context_state_path(repo).exists())

    def test_legacy_state_migration_and_representative_text_are_stable(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.initialize_git(repo)
            self.run_command(sys.executable, str(LEDGER), "--repo", str(repo), "init")
            state_path = RUNTIME.context_state_path(repo)
            legacy_bytes = LEGACY_STATE.read_bytes()
            state_path.write_bytes(legacy_bytes)
            self.run_command(sys.executable, str(LEDGER), "--repo", str(repo), "init", "--dry-run")
            self.assertEqual(legacy_bytes, state_path.read_bytes())
            self.run_command(sys.executable, str(LEDGER), "--repo", str(repo), "init")
            migrated = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual({
                "schema_version": RUNTIME.VERSION,
                "task_sessions": {},
                "recent_features": ["legacy-feature"],
            }, migrated)
            output = self.run_command(sys.executable, str(LEDGER), "--repo", str(repo), "status").stdout
            lines = []
            for line in output.splitlines():
                if line.startswith("Repository: "):
                    line = "Repository: <REPO_ROOT>"
                elif line.startswith("Principal: "):
                    line = "Principal: <PRINCIPAL>"
                elif line.startswith("Workspace state: "):
                    line = "Workspace state: <PRIVATE_STATE>"
                lines.append(re.sub(r"[A-Fa-f0-9]{16}", "<VOLATILE_ID>", line))
            expected = STATUS_TEXT.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(expected, lines)


if __name__ == "__main__":
    unittest.main()
