import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build_runtime.py"
CANONICAL = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
MIRROR = ROOT / ".context-ledger" / "ledger.py"


class RuntimeBuildTests(unittest.TestCase):
    def run_build(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(BUILD), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def test_repository_runtime_outputs_match_the_deterministic_build(self):
        result = self.run_build("--check")
        self.assertIn("standalone runtime outputs are current", result.stdout.casefold())
        self.assertEqual(CANONICAL.read_bytes(), MIRROR.read_bytes())

    def test_two_fresh_builds_are_byte_identical_and_executable(self):
        with tempfile.TemporaryDirectory() as raw:
            first = Path(raw) / "first.py"
            second = Path(raw) / "second.py"
            self.run_build("--output", str(first), "--output", str(second))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            compile(first.read_text(encoding="utf-8"), str(first), "exec")
            version = subprocess.run(
                [sys.executable, str(first), "--version"],
                text=True,
                capture_output=True,
                encoding="utf-8",
            )
            self.assertEqual(0, version.returncode, version.stderr)
            self.assertIn("repo-context-ledger 0.7.0", version.stdout)

    def test_check_detects_output_drift_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as raw:
            output = Path(raw) / "ledger.py"
            self.run_build("--output", str(output))
            output.write_text("# drift\n", encoding="utf-8")
            before = output.read_bytes()
            result = self.run_build("--check", "--output", str(output), expected=2)
            self.assertIn("drift", result.stderr.casefold())
            self.assertEqual(before, output.read_bytes())

    def test_ordered_low_coupling_fragments_are_embedded_without_markers(self):
        generated = CANONICAL.read_text(encoding="utf-8")
        self.assertIn('TOOL_VERSION = "0.7.0"', generated)
        self.assertIn("class LedgerError", generated)
        self.assertIn("class CommandResult", generated)
        self.assertLess(generated.index("class LedgerError"), generated.index("class CommandResult"))
        self.assertNotIn("@repo-context-ledger:", generated)
        for name in ("constants.pyfrag", "errors.pyfrag", "models.pyfrag"):
            self.assertTrue((ROOT / "src" / "repo_context_ledger" / name).is_file(), name)

    def test_git_checkout_pins_runtime_generation_inputs_and_outputs_to_lf(self):
        paths = (
            "scripts/build_runtime.py",
            "src/repo_context_ledger/runtime.py.tmpl",
            "src/repo_context_ledger/constants.pyfrag",
            "src/repo_context_ledger/errors.pyfrag",
            "src/repo_context_ledger/models.pyfrag",
            "skills/repo-context-ledger/scripts/ledger.py",
            ".context-ledger/ledger.py",
        )
        result = subprocess.run(
            ["git", "-C", str(ROOT), "check-attr", "eol", "--", *paths],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        observed = {}
        for line in result.stdout.splitlines():
            path, separator, value = line.partition(": eol: ")
            self.assertEqual(": eol: ", separator)
            observed[path] = value
        self.assertEqual({path: "lf" for path in paths}, observed)


if __name__ == "__main__":
    unittest.main()
