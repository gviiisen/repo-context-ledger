import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
EVAL = ROOT / "tests/fixtures/workflow-plan-eval-v1.json"
GOLDEN = ROOT / "tests/golden/workflow-plan-v1.json"


class WorkflowPlanTests(unittest.TestCase):
    def run_ledger(
        self,
        repo: Path,
        *args: str,
        expected: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"
        environment["REPO_CONTEXT_LEDGER_PRINCIPAL"] = "workflow-owner"
        result = subprocess.run(
            [sys.executable, str(LEDGER), "--repo", str(repo), *args],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
        )
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def initialized_repo(self, raw: str) -> Path:
        repo = Path(raw) / "repo"
        repo.mkdir()
        self.run_ledger(repo, "init")
        return repo

    @staticmethod
    def session_id(result: subprocess.CompletedProcess[str]) -> str:
        return next(
            line.removeprefix("Session: ").strip()
            for line in result.stdout.splitlines()
            if line.startswith("Session: ")
        )

    def plan(self, repo: Path, query: str, *extra: str) -> dict:
        result = self.run_ledger(
            repo,
            "plan",
            "--query",
            query,
            "--format",
            "json",
            *extra,
        )
        return json.loads(result.stdout)

    def test_auto_plan_classifies_readonly_small_fix_and_ordinary_change(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(raw)
            evaluation = json.loads(EVAL.read_text(encoding="utf-8"))
            self.assertEqual("workflow-plan-eval-v1", evaluation["schema"])
            for case in evaluation["cases"]:
                query, expected = case["query"], case["mode"]
                with self.subTest(query=query):
                    plan = self.plan(repo, query)
                    self.assertEqual("workflow-plan-v1", plan["schema"])
                    self.assertEqual(expected, plan["mode"])
                    self.assertIn("kind", plan["next_action"])
                    self.assertIsInstance(plan["next_action"]["argv"], list)
                    self.assertTrue(plan["reasons"])

    def test_workflow_plan_matches_the_published_golden_shape(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(raw)
            plan = self.plan(repo, "explain the retry boundary")
            golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
            self.assertEqual(golden["schema"], plan["schema"])
            self.assertIn(plan["mode"], golden["modes"])
            self.assertTrue(set(golden["required_fields"]).issubset(plan))
            self.assertTrue(
                set(golden["next_action_fields"]).issubset(plan["next_action"])
            )

    def test_skill_keeps_the_front_door_short_and_routes_detail_to_references(self):
        text = (ROOT / "skills/repo-context-ledger/SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(text), 12000)
        self.assertIn("workflow-plan-v1", text)
        self.assertIn("references/production-workflow.md", text)
        self.assertIn("references/verification-presets.md", text)
        self.assertIn("references/document-model.md", text)

    def test_explicit_intent_is_high_confidence_and_readonly_cannot_start(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(raw)
            plan = self.plan(repo, "inspect the current implementation", "--intent", "readonly")
            self.assertEqual("readonly", plan["mode"])
            self.assertEqual("high", plan["confidence"])
            self.assertFalse(plan["requires_confirmation"])

            rejected = self.run_ledger(
                repo,
                "start",
                "--title",
                "Should remain read only",
                "--workflow",
                "readonly",
                expected=2,
            )
            self.assertIn("cannot start", rejected.stderr)
            status = self.run_ledger(repo, "status")
            self.assertIn("Active task sessions: 0", status.stdout)

            started = self.run_ledger(
                repo,
                "start",
                "--title",
                "Repair one parser edge",
                "--workflow",
                "small-fix",
            )
            self.assertIn("Workflow: small-fix", started.stdout)

    def test_owned_checkpoint_produces_resume_next_action(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(raw)
            started = self.run_ledger(
                repo,
                "start",
                "--title",
                "Announcement rate limiting",
                "--feature",
                "announcement-rate-limit",
                "--workflow",
                "ordinary-change",
            )
            session = self.session_id(started)
            self.run_ledger(
                repo,
                "checkpoint",
                "--session",
                session,
                "--summary",
                "The rate-limit boundary and retry caller were identified.",
                "--next",
                "Implement the bounded retry and rerun focused tests.",
            )

            plan = self.plan(repo, "continue announcement rate limiting")
            self.assertEqual("resume", plan["mode"])
            self.assertEqual(session, plan["session_id"])
            self.assertEqual("resume", plan["next_action"]["kind"])
            self.assertEqual(["resume", "--session", session], plan["next_action"]["argv"])
            self.assertFalse(plan["requires_confirmation"])

            context = json.loads(self.run_ledger(
                repo,
                "context",
                "--query",
                "continue announcement rate limiting",
                "--format",
                "json",
            ).stdout)
            self.assertEqual(plan["mode"], context["workflow"]["mode"])
            self.assertEqual("workflow-plan-v1", context["workflow"]["schema"])

    def test_ambiguous_resume_plan_fails_closed_to_clarification(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(raw)
            for suffix in ("worker", "gateway"):
                self.run_ledger(
                    repo,
                    "start",
                    "--title",
                    f"Announcement retry {suffix}",
                    "--feature",
                    "announcement-retry",
                    "--workflow",
                    "ordinary-change",
                )
            plan = self.plan(repo, "continue announcement retry", "--intent", "resume")
            self.assertEqual("resume", plan["mode"])
            self.assertTrue(plan["requires_confirmation"])
            self.assertEqual("clarify", plan["next_action"]["kind"])
            self.assertEqual([], plan["next_action"]["argv"])


if __name__ == "__main__":
    unittest.main()
