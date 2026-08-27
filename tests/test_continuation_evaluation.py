import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "scripts" / "evaluate_continuation.py"


class ContinuationEvaluationTests(unittest.TestCase):
    def test_synthetic_continuation_corpus_protects_accuracy_privacy_and_budget(self):
        result = subprocess.run(
            [sys.executable, str(EVALUATOR), "--format", "json"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("continuation-eval-report-v1", report["schema"])
        self.assertEqual(8, report["case_count"])
        self.assertEqual(report["top1_cases"], report["top1_correct"])
        self.assertEqual(1, report["ambiguity_count"])
        self.assertEqual(2, report["foreign_overlap_count"])
        self.assertEqual(0, report["privacy_violations"])
        self.assertEqual(0, report["capsule_budget_violations"])
        self.assertEqual(0, report["anchor_failures"])
        self.assertEqual(0, report["expectation_failures"])
        self.assertGreaterEqual(report["latency_ms"], 0)
        self.assertNotIn(str(ROOT), result.stdout)


if __name__ == "__main__":
    unittest.main()
