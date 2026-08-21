import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "scripts" / "evaluate_routing.py"


class RoutingEvaluationTests(unittest.TestCase):
    def test_labeled_corpus_reports_accuracy_boundaries_budget_and_latency(self):
        result = subprocess.run([sys.executable, str(EVALUATOR), "--format", "json"], text=True, capture_output=True, encoding="utf-8", errors="replace")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual("routing-eval-report-v1", report["schema"])
        self.assertEqual(6, report["case_count"])
        self.assertEqual(report["top1_cases"], report["top1_correct"])
        self.assertEqual(1, report["ambiguity_count"])
        self.assertEqual(1, report["fallback_count"])
        self.assertEqual(1, report["stale_selection_count"])
        self.assertEqual(0, report["superseded_selection_count"])
        self.assertEqual(0, report["expectation_failures"])
        self.assertGreater(report["required_read_characters"], 0)
        self.assertGreaterEqual(report["latency_ms"], 0)
        self.assertNotIn(str(ROOT), result.stdout)


if __name__ == "__main__":
    unittest.main()
