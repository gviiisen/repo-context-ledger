import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
GOLDEN = ROOT / "tests" / "golden" / "v0.6.2-cli-contract.json"
WORKFLOW_GOLDEN = ROOT / "tests" / "golden" / "workflow-plan-v1.json"
SPEC = importlib.util.spec_from_file_location("repo_context_ledger_stable_runtime", LEDGER)
RUNTIME = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNTIME)


class ContractStabilityTests(unittest.TestCase):
    def run_ledger(self, repo: Path, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(LEDGER), "--repo", str(repo), *args],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def git(self, repo: Path, *args: str) -> None:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], text=True, capture_output=True, encoding="utf-8"
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def init_repo(self, repo: Path) -> None:
        repo.mkdir(parents=True)
        self.git(repo, "init", "-b", "main")
        self.git(repo, "config", "user.name", "Contract Tester")
        self.git(repo, "config", "user.email", "contract@example.test")
        (repo / "service.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.run_ledger(repo, "init")
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-m", "Initialize fixture")

    def test_versioned_status_json_is_bounded_and_machine_local_paths_are_private(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            result = self.run_ledger(repo, "status", "--format", "json")
            report = json.loads(result.stdout)
            self.assertEqual("status-v1", report["schema"])
            self.assertEqual("main", report["repository"]["branch"])
            self.assertEqual(0, report["sessions"]["active"]["count"])
            self.assertNotIn(str(repo), result.stdout)
            self.assertNotIn("Workspace state", result.stdout)

    def test_versioned_check_json_preserves_exit_class_and_separates_errors(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            healthy = json.loads(self.run_ledger(repo, "check", "--format", "json").stdout)
            self.assertEqual("check-v1", healthy["schema"])
            self.assertTrue(healthy["ok"])
            self.assertEqual(0, healthy["exit_code"])
            self.assertEqual([], healthy["errors"])

            (repo / "docs" / "specs" / "broken.md").write_text(
                "# Broken\n\n[missing](not-here.md)\n", encoding="utf-8"
            )
            failed = self.run_ledger(repo, "check", "--format", "json", expected=2)
            report = json.loads(failed.stdout)
            self.assertFalse(report["ok"])
            self.assertEqual(2, report["exit_code"])
            self.assertTrue(any("Broken link" in item for item in report["errors"]))
            self.assertEqual("", failed.stderr)

    def test_golden_json_contract_fields_and_exit_codes_are_stable(self):
        golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual(golden["schemas"]["context"], RUNTIME.CONTEXT_BUNDLE_SCHEMA)
        self.assertEqual(golden["schemas"]["doctor"], RUNTIME.DOCTOR_SCHEMA)
        self.assertEqual(golden["schemas"]["status"], RUNTIME.STATUS_SCHEMA)
        self.assertEqual(golden["schemas"]["check"], RUNTIME.CHECK_SCHEMA)
        self.assertEqual(golden["exit_codes"]["success"], RUNTIME.EXIT_SUCCESS)
        self.assertEqual(golden["exit_codes"]["no_match"], RUNTIME.EXIT_NO_MATCH)
        self.assertEqual(golden["exit_codes"]["invalid_or_unhealthy"], RUNTIME.EXIT_INVALID)
        self.assertEqual({
            "generic": RUNTIME.ERROR_LEDGER,
            "invalid_argument": RUNTIME.ERROR_INVALID_ARGUMENT,
            "unsupported_schema": RUNTIME.ERROR_UNSUPPORTED_SCHEMA,
            "context_no_match": RUNTIME.ERROR_CONTEXT_NO_MATCH,
            "check_failed": RUNTIME.ERROR_CHECK_FAILED,
            "doctor_failed": RUNTIME.ERROR_DOCTOR_FAILED,
        }, golden["error_codes"])

    def test_all_versioned_json_contracts_publish_required_fields(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
            reports = {
                "context-bundle-v1": json.loads(self.run_ledger(repo, "context", "--query", "unmatched telescope", "--format", "json", expected=1).stdout),
                "doctor-v1": json.loads(self.run_ledger(repo, "doctor", "--format", "json").stdout),
                "status-v1": json.loads(self.run_ledger(repo, "status", "--format", "json").stdout),
                "check-v1": json.loads(self.run_ledger(repo, "check", "--format", "json").stdout),
            }
            for schema, report in reports.items():
                self.assertEqual(schema, report["schema"])
                self.assertTrue(set(golden["required_fields"][schema]).issubset(report), schema)
            self.assertEqual("CONTEXT_NO_MATCH", reports["context-bundle-v1"]["error"]["code"])

    def test_workflow_plan_contract_is_versioned_and_read_only(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            before = subprocess.run(
                ["git", "-C", str(repo), "status", "--porcelain=v1"],
                text=True,
                capture_output=True,
                encoding="utf-8",
                check=True,
            ).stdout
            report = json.loads(
                self.run_ledger(
                    repo,
                    "plan",
                    "--query",
                    "explain the retry boundary",
                    "--format",
                    "json",
                ).stdout
            )
            golden = json.loads(WORKFLOW_GOLDEN.read_text(encoding="utf-8"))
            self.assertEqual(golden["schema"], report["schema"])
            self.assertIn(report["mode"], golden["modes"])
            self.assertTrue(set(golden["required_fields"]).issubset(report))
            self.assertTrue(
                set(golden["next_action_fields"]).issubset(report["next_action"])
            )
            after = subprocess.run(
                ["git", "-C", str(repo), "status", "--porcelain=v1"],
                text=True,
                capture_output=True,
                encoding="utf-8",
                check=True,
            ).stdout
            self.assertEqual(before, after)

    def test_doctor_failed_error_code_matches_the_golden_contract(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            (repo / ".context-ledger" / "config.json").write_text("{not json", encoding="utf-8")
            failed = self.run_ledger(repo, "doctor", "--format", "json", expected=2)
            report = json.loads(failed.stdout)
            golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
            self.assertEqual(golden["error_codes"]["doctor_failed"], report["error_code"])

    def test_json_errors_remain_versioned_and_preserve_exit_class(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            status = self.run_ledger(repo, "status", "--format", "json", expected=2)
            status_report = json.loads(status.stdout)
            self.assertEqual("status-v1", status_report["schema"])
            self.assertFalse(status_report["ok"])
            self.assertEqual("LEDGER_ERROR", status_report["error_code"])
            self.assertEqual("", status.stderr)

            check = self.run_ledger(repo, "check", "--format", "json", expected=2)
            check_report = json.loads(check.stdout)
            self.assertEqual("check-v1", check_report["schema"])
            self.assertFalse(check_report["ok"])
            self.assertEqual("CHECK_FAILED", check_report["error_code"])
            self.assertEqual("", check.stderr)

            context = self.run_ledger(
                repo, "context", "--query", "anything", "--format", "json", expected=2
            )
            context_report = json.loads(context.stdout)
            self.assertEqual("context-bundle-v1", context_report["schema"])
            self.assertEqual("LEDGER_ERROR", context_report["error"]["code"])
            self.assertEqual("", context.stderr)

            equals_context = self.run_ledger(
                repo, "context", "--query=anything", "--format=json", expected=2
            )
            self.assertEqual(
                "context-bundle-v1", json.loads(equals_context.stdout)["schema"]
            )
            self.assertEqual("", equals_context.stderr)

            missing = Path(raw) / "does-not-exist"
            missing_status = self.run_ledger(missing, "status", "--format", "json", expected=2)
            missing_report = json.loads(missing_status.stdout)
            self.assertEqual("status-v1", missing_report["schema"])
            self.assertFalse(missing_report["ok"])
            self.assertNotIn(str(missing), missing_status.stdout)
            self.assertEqual("", missing_status.stderr)

            deceptive = subprocess.run(
                [sys.executable, str(LEDGER), "--repo", "context", "status", "--format", "json"],
                cwd=Path(raw),
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(2, deceptive.returncode)
            self.assertEqual("status-v1", json.loads(deceptive.stdout)["schema"])
            self.assertEqual("", deceptive.stderr)

    def test_future_configuration_schema_returns_stable_json_error(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            config_path = repo / ".context-ledger" / "config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["schema_version"] = RUNTIME.VERSION + 1
            config_path.write_text(json.dumps(config), encoding="utf-8")
            commands = (
                ("status", "error_code"),
                ("doctor", "error_code"),
                ("check", "error_code"),
            )
            for command, field in commands:
                failed = self.run_ledger(repo, command, "--format", "json", expected=2)
                report = json.loads(failed.stdout)
                self.assertEqual("UNSUPPORTED_SCHEMA", report[field], command)
                self.assertNotIn(str(repo), failed.stdout)
                self.assertEqual("", failed.stderr)
            context = self.run_ledger(
                repo, "context", "--query", "feature", "--format", "json", expected=2
            )
            context_report = json.loads(context.stdout)
            self.assertEqual("UNSUPPORTED_SCHEMA", context_report["error"]["code"])
            self.assertNotIn(str(repo), context.stdout)
            self.assertEqual("", context.stderr)

            plan = self.run_ledger(
                repo, "plan", "--query", "feature", "--format", "json", expected=2
            )
            plan_report = json.loads(plan.stdout)
            self.assertEqual("workflow-plan-v1", plan_report["schema"])
            self.assertEqual("UNSUPPORTED_SCHEMA", plan_report["error"]["code"])
            self.assertNotIn(str(repo), plan.stdout)
            self.assertEqual("", plan.stderr)

    def test_future_private_state_schema_returns_stable_json_error(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            state_path = RUNTIME.context_state_path(repo)
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["schema_version"] = RUNTIME.VERSION + 1
            state_path.write_text(json.dumps(state), encoding="utf-8")
            failed = self.run_ledger(repo, "status", "--format", "json", expected=2)
            report = json.loads(failed.stdout)
            self.assertEqual("UNSUPPORTED_SCHEMA", report["error_code"])
            self.assertNotIn(str(state_path.parent), failed.stdout)


if __name__ == "__main__":
    unittest.main()
