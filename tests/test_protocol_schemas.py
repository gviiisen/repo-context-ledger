import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
SCHEMA_ROOT = ROOT / "schemas"
CONTRACTS = {
    "workflow-plan-v1": "workflow-plan-v1.schema.json",
    "context-bundle-v1": "context-bundle-v1.schema.json",
    "resume-capsule-v2": "resume-capsule-v2.schema.json",
    "doctor-v1": "doctor-v1.schema.json",
    "status-v1": "status-v1.schema.json",
    "check-v1": "check-v1.schema.json",
}


class ProtocolSchemaTests(unittest.TestCase):
    def run_ledger(
        self, repo: Path, *args: str, expected: int = 0
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"
        environment["REPO_CONTEXT_LEDGER_PRINCIPAL"] = "protocol-owner"
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

    def session_id(self, result: subprocess.CompletedProcess[str]) -> str:
        for line in result.stdout.splitlines():
            if line.startswith("Session: "):
                return line.removeprefix("Session: ").strip()
        self.fail(f"start output did not contain a session ID: {result.stdout}")

    def assert_schema_value(self, rule: dict, value: object, path: str) -> None:
        declared = rule.get("type")
        if declared is not None:
            declared_types = [declared] if isinstance(declared, str) else declared
            matches = []
            for item in declared_types:
                if item == "null":
                    matches.append(value is None)
                elif item == "boolean":
                    matches.append(isinstance(value, bool))
                elif item == "integer":
                    matches.append(isinstance(value, int) and not isinstance(value, bool))
                elif item == "number":
                    matches.append(isinstance(value, (int, float)) and not isinstance(value, bool))
                else:
                    expected = {"string": str, "array": list, "object": dict}[item]
                    matches.append(isinstance(value, expected))
            self.assertTrue(any(matches), f"{path} does not match type {declared!r}")
        if "const" in rule:
            self.assertEqual(rule["const"], value, path)
        if "enum" in rule:
            self.assertIn(value, rule["enum"], path)
        if isinstance(value, dict):
            self.assertTrue(
                set(rule.get("required", [])).issubset(value),
                f"{path} is missing required fields",
            )
            for field, child_rule in rule.get("properties", {}).items():
                if field in value:
                    self.assert_schema_value(child_rule, value[field], f"{path}.{field}")
        if isinstance(value, list) and "items" in rule:
            for index, item in enumerate(value):
                self.assert_schema_value(rule["items"], item, f"{path}[{index}]")

    def assert_declared_shape(self, schema: dict, sample: dict) -> None:
        self.assertEqual("https://json-schema.org/draft/2020-12/schema", schema["$schema"])
        self.assertEqual("object", schema["type"])
        self.assertTrue(schema["$id"].startswith("https://github.com/gviiisen/"))
        self.assert_schema_value(schema, sample, "$")

    def test_every_public_protocol_has_a_parseable_versioned_schema(self):
        for protocol, filename in CONTRACTS.items():
            with self.subTest(protocol=protocol):
                schema = json.loads((SCHEMA_ROOT / filename).read_text(encoding="utf-8"))
                self.assertEqual(protocol, schema["title"])
                self.assertTrue(schema["additionalProperties"])

    def test_runtime_reports_match_their_published_top_level_contracts(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(raw)
            started = self.run_ledger(
                repo,
                "start",
                "--title",
                "Protocol continuation",
                "--feature",
                "protocol-continuation",
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
                "The public protocol boundary is identified and documented.",
                "--next",
                "Continue validating the published protocol shapes.",
            )
            context = json.loads(
                self.run_ledger(
                    repo,
                    "context",
                    "--query",
                    "continue protocol continuation",
                    "--format",
                    "json",
                ).stdout
            )
            samples = {
                "workflow-plan-v1": json.loads(
                    self.run_ledger(
                        repo,
                        "plan",
                        "--query",
                        "explain retry behavior",
                        "--format",
                        "json",
                    ).stdout
                ),
                "context-bundle-v1": context,
                "resume-capsule-v2": context["resume"]["capsule"],
                "doctor-v1": json.loads(
                    self.run_ledger(repo, "doctor", "--format", "json").stdout
                ),
                "status-v1": json.loads(
                    self.run_ledger(repo, "status", "--format", "json").stdout
                ),
                "check-v1": json.loads(
                    self.run_ledger(repo, "check", "--format", "json").stdout
                ),
            }
            for protocol, sample in samples.items():
                with self.subTest(protocol=protocol):
                    schema = json.loads(
                        (SCHEMA_ROOT / CONTRACTS[protocol]).read_text(encoding="utf-8")
                    )
                    self.assertEqual(protocol, sample["schema"])
                    self.assert_declared_shape(schema, sample)

            no_match = json.loads(
                self.run_ledger(
                    repo,
                    "context",
                    "--query",
                    "completely unrelated unmatched route",
                    "--format",
                    "json",
                    expected=1,
                ).stdout
            )
            self.assert_declared_shape(
                json.loads(
                    (SCHEMA_ROOT / CONTRACTS["context-bundle-v1"]).read_text(encoding="utf-8")
                ),
                no_match,
            )

    def test_versioned_error_reports_keep_the_same_required_shape(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(raw)
            (repo / ".context-ledger" / "config.json").write_text(
                "{invalid json", encoding="utf-8"
            )
            commands = {
                "workflow-plan-v1": ("plan", "--query", "inspect", "--format", "json"),
                "context-bundle-v1": (
                    "context",
                    "--query",
                    "inspect",
                    "--format",
                    "json",
                ),
                "doctor-v1": ("doctor", "--format", "json"),
                "status-v1": ("status", "--format", "json"),
                "check-v1": ("check", "--format", "json"),
            }
            for protocol, argv in commands.items():
                with self.subTest(protocol=protocol):
                    report = json.loads(
                        self.run_ledger(repo, *argv, expected=2).stdout
                    )
                    schema = json.loads(
                        (SCHEMA_ROOT / CONTRACTS[protocol]).read_text(encoding="utf-8")
                    )
                    self.assertEqual(protocol, report["schema"])
                    self.assert_declared_shape(schema, report)


if __name__ == "__main__":
    unittest.main()
