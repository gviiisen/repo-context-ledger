"""Real subprocess and temporary-repository tests for lean verification and forwarding."""
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import test_ledger as flow

RUNTIME = flow.LEDGER_MODULE
ASSET = flow.ROOT / "skills/repo-context-ledger/assets/verify-change.py"
spec = importlib.util.spec_from_file_location("acceptance_example", ASSET)
SUITE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SUITE)


class VerificationBoundaryTests(unittest.TestCase):
    run_ledger = flow.LedgerFlowTests.run_ledger
    run_git = flow.LedgerFlowTests.run_git
    init_git_repo = flow.LedgerFlowTests.init_git_repo
    repository_snapshot = flow.LedgerFlowTests.repository_snapshot

    def installed_fixture(self, root):
        skill_home = root / "user home"
        target = skill_home / "skills/repo-context-ledger"
        shutil.copytree(flow.LEDGER.parent.parent, target)
        return skill_home

    def launch(self, repo, *args, skill_home=None, cwd=None):
        env = dict(os.environ, CODEX_HOME=str(skill_home))
        return subprocess.run([sys.executable, str(repo / ".context-ledger/ledger.py"), *args],
            cwd=cwd or repo, env=env, capture_output=True, text=True, encoding="utf-8")

    def test_global_launcher_preserves_repository_selection_and_follows_upgrades(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = root / "project with spaces"
            self.init_git_repo(repo)
            skill_home = self.installed_fixture(root)
            before = self.repository_snapshot(repo)
            self.run_ledger(repo, "init", "--runtime", "global", "--dry-run")
            self.assertEqual(before, self.repository_snapshot(repo))
            self.run_ledger(repo, "init", "--runtime", "global")
            launcher = repo / ".context-ledger/ledger.py"
            self.assertEqual(RUNTIME.global_runtime_launcher(), launcher.read_text(encoding="utf-8"))
            self.assertLess(launcher.stat().st_size, 2000)
            # cwd deliberately lies outside the project. Forwarder supplies the project root.
            status = self.launch(repo, "status", "--format", "json", skill_home=skill_home, cwd=root)
            self.assertEqual(0, status.returncode, status.stderr)
            self.assertIn("status-v1", status.stdout)
            started = self.launch(repo, "start", "--title", "Fixture continuation", skill_home=skill_home, cwd=root)
            self.assertEqual(0, started.returncode, started.stderr)
            self.assertTrue(flow.private_draft(repo, started).is_file())
            preserved = self.repository_snapshot(repo)
            runtime = skill_home / "skills/repo-context-ledger/scripts/ledger.py"
            runtime.write_text(runtime.read_text(encoding="utf-8").replace(
                'TOOL_VERSION = "' + RUNTIME.TOOL_VERSION + '"', 'TOOL_VERSION = "9.9.9-test"'), encoding="utf-8")
            version = self.launch(repo, "--version", skill_home=skill_home, cwd=root)
            self.assertEqual(0, version.returncode, version.stderr)
            self.assertIn("9.9.9-test", version.stdout)
            self.assertEqual(preserved, self.repository_snapshot(repo))
            self.run_ledger(repo, "init")  # Saved global mode survives refresh.
            self.assertEqual(RUNTIME.global_runtime_launcher(), launcher.read_text(encoding="utf-8"))

    def test_global_launcher_missing_relative_or_recursive_target_fails_without_changes(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            repo = root / "repo"
            self.init_git_repo(repo)
            self.run_ledger(repo, "init", "--runtime", "global")
            before = self.repository_snapshot(repo)
            for target in (root / "absent", Path("relative"), repo):
                result = self.launch(repo, "status", skill_home=target)
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertEqual(before, self.repository_snapshot(repo))
            local = repo / "skills/repo-context-ledger/scripts"
            local.mkdir(parents=True)
            shutil.copy2(repo / ".context-ledger/ledger.py", local / "ledger.py")
            result = self.launch(repo, "status", skill_home=repo)
            self.assertEqual(2, result.returncode)
            self.assertIn("no local fallback", result.stderr)

    def test_global_runtime_validation_and_doctor_check_the_launcher(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            config = RUNTIME.load_config(repo)
            for invalid in ([], {"mode": "anything"}, {"mode": "global", "path": "arbitrary.py"}):
                with self.assertRaises(RUNTIME.LedgerError):
                    RUNTIME.validate_config(repo, {**config, "runtime": invalid})
            self.run_ledger(repo, "init", "--runtime", "global")
            self.run_ledger(repo, "doctor")
            (repo / ".context-ledger/ledger.py").write_bytes(b"\xff broken launcher\n")
            failed = self.run_ledger(repo, "doctor", expected=2)
            self.assertIn("RUNTIME_DRIFT", failed.stdout)

    def test_grouped_checks_stop_after_failure_and_report_unrun_steps(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            marker = root / "must-not-exist"
            checks = [
                ("first", [sys.executable, "-c", "pass"]),
                ("second", [sys.executable, "-c", "raise SystemExit(7)"]),
                ("third", [sys.executable, "-c", f"from pathlib import Path; Path({str(marker)!r}).touch()"]),
            ]
            output = io.StringIO()
            with redirect_stdout(output):
                result = SUITE.run_checks(checks, root)
            self.assertEqual(1, result)
            self.assertFalse(marker.exists())
            text = output.getvalue()
            self.assertIn("ledger-step: first passed", text)
            self.assertIn("ledger-step: second failed", text)
            self.assertIn("ledger-step: third not-run", text)
            summary = RUNTIME.verification_output_summary(text, "", "failed")
            for item in ("first=passed", "second=failed", "third=not-run"):
                self.assertIn(item, summary)
            with self.assertRaises(ValueError):
                SUITE.run_checks([], root)

    def test_one_verify_keeps_substep_results_and_separates_timings(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            started = self.run_ledger(repo, "start", "--title", "Grouped acceptance")
            session = flow.session_from_result(started)
            (repo / "scripts").mkdir(exist_ok=True)
            helper = repo / "scripts/verify-change.py"
            checks = [("imports", [sys.executable, "-c", "import time; time.sleep(0.15)"]),
                      ("focused", [sys.executable, "-c", "assert 2 == 2"])]
            helper.write_text(ASSET.read_text(encoding="utf-8").replace("CHECKS = []", "CHECKS = " + repr(checks)), encoding="utf-8")
            result = self.run_ledger(repo, "--timings", "verify", "--session", session,
                "--", sys.executable, str(helper))
            report = json.loads(result.stderr.split("repo-context-ledger-timings: ")[-1])
            self.assertGreaterEqual(report["stages"]["verification_command_ms"], 100)
            self.assertGreaterEqual(report["ledger_overhead_ms"], 0)
            for stage in ("verification_prepare_ms", "verification_record_ms", "lock_wait_ms"):
                self.assertGreaterEqual(report["stages"][stage], 0)
            self.assertAlmostEqual(report["elapsed_ms"], report["ledger_overhead_ms"] + report["stages"]["verification_command_ms"], delta=0.02)
            draft = flow.private_draft(repo, started).read_text(encoding="utf-8")
            self.assertEqual(1, draft.count("- Command:"))
            self.assertIn("imports=passed, focused=passed", draft)
            self.assertNotIn("ledger_overhead_ms", draft)
            self.assertNotIn(str(repo), result.stderr)
            self.run_ledger(repo, "verify", "--session", session, "--sensitive", "--", sys.executable, str(helper))
            sensitive = flow.private_draft(repo, started).read_text(encoding="utf-8").split("<sensitive verification>")[-1]
            self.assertNotIn("imports=passed", sensitive)


if __name__ == "__main__":
    unittest.main()
