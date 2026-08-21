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
ROUTING_EVAL = ROOT / "tests" / "fixtures" / "routing-eval-v1.json"
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

    def test_synthetic_routing_evaluation_keeps_expected_primary_feature(self):
        corpus = json.loads(ROUTING_EVAL.read_text(encoding="utf-8"))
        self.assertEqual("routing-eval-v1", corpus["schema"])
        for case in corpus["cases"]:
            tokens = RUNTIME.query_tokens(case["query"])
            ranked = []
            for candidate in case["candidates"]:
                pack = {
                    **candidate,
                    "status": "current",
                    "superseded_by": "",
                    "fingerprints_ok": True,
                }
                score, _ = RUNTIME.score_context_pack(pack, case["query"], tokens)
                ranked.append((score, candidate["feature"]))
            ranked.sort(key=lambda item: (-item[0], item[1]))
            self.assertEqual(case["expected_feature"], ranked[0][1], case["query"])


if __name__ == "__main__":
    unittest.main()
