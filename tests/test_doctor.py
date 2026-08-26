import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
SPEC = importlib.util.spec_from_file_location("repo_context_ledger_contract_runtime", LEDGER)
RUNTIME = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNTIME)


class DoctorTests(unittest.TestCase):
    def run_git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        return result

    def run_ledger(
        self,
        repo: Path,
        *args: str,
        expected: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(LEDGER), "--repo", str(repo), *args],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def init_repo(self, repo: Path) -> None:
        repo.mkdir(parents=True)
        self.run_git(repo, "init", "-b", "main")
        self.run_git(repo, "config", "user.name", "Contract Tester")
        self.run_git(repo, "config", "user.email", "contract@example.test")
        source = repo / "src" / "service.py"
        source.parent.mkdir()
        source.write_text("VALUE = 1\n", encoding="utf-8")
        self.run_ledger(repo, "init")
        self.run_git(repo, "add", "-A")
        self.run_git(repo, "commit", "-m", "Initialize fixture")

    def write_pack(
        self,
        repo: Path,
        name: str,
        feature: str,
        tracked: list[str],
        *,
        status: str = "current",
        superseded_by: str = "",
    ) -> Path:
        pack = repo / "docs" / "ai" / "context-packs" / f"{name}.md"
        fingerprints = []
        for raw in tracked:
            digest = RUNTIME.file_digest(repo / raw, repo)
            fingerprints.append(f"- `{raw}` — `sha256:{digest}`")
        lineage = f"Superseded by: {superseded_by}\n" if superseded_by else ""
        pack.write_text(
            f"# {name} context pack\n\n"
            f"Status: {status}\nFeature: {feature}\n{lineage}"
            "Quality profile: evidence-v1\nLanguage: en\nDetail: standard\n"
            "Source commit: fixture\nBase branch: main\nBase commit: fixture\n"
            "Last refreshed: 2026-08-21T00:00:00\n\n"
            "## Purpose\n\nRoutes the fixture feature without loading unrelated code.\n\n"
            "## Load order\n\n"
            "- Read first: Read the tracked service implementation.\n"
            "- Read if needed: Read callers only when behavior crosses the boundary.\n"
            "- Do not load by default: Do not read unrelated feature modules.\n\n"
            "## Entry points and code map\n\n"
            "| Path / symbol | Role |\n| --- | --- |\n"
            f"| `{tracked[0]}` | Owns the fixture behavior. |\n\n"
            "## Contracts and boundaries\n\n"
            "- Invariants and contracts: The public fixture result remains stable.\n"
            "- Failure / recovery: Failures remain explicit and retry safe.\n"
            "- Non-goals: Persistence and unrelated routes are outside this fixture.\n\n"
            "## Verification\n\nRun `python -m unittest` to verify fixture behavior.\n\n"
            "<!-- repo-context-ledger:pack-specs:start -->\n"
            "## Stable context\n\n- No linked stable specs yet.\n"
            "<!-- repo-context-ledger:pack-specs:end -->\n\n"
            "<!-- repo-context-ledger:pack-files:start -->\n"
            "## Tracked file fingerprints\n\n"
            + "\n".join(fingerprints)
            + "\n<!-- repo-context-ledger:pack-files:end -->\n",
            encoding="utf-8",
        )
        return pack

    def test_doctor_reports_a_versioned_read_only_json_contract(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            before = {
                path.relative_to(repo).as_posix(): path.read_bytes()
                for path in repo.rglob("*")
                if path.is_file() and ".git" not in path.parts
            }
            result = self.run_ledger(repo, "doctor", "--format", "json")
            report = json.loads(result.stdout)
            self.assertEqual("doctor-v1", report["schema"])
            self.assertEqual("pass", report["summary"]["overall"])
            self.assertEqual([], [item for item in report["findings"] if item["severity"] != "pass"])
            after = {
                path.relative_to(repo).as_posix(): path.read_bytes()
                for path in repo.rglob("*")
                if path.is_file() and ".git" not in path.parts
            }
            self.assertEqual(before, after)

    def test_doctor_groups_stale_paths_and_bounds_details(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            second = repo / "src" / "other.py"
            second.write_text("VALUE = 2\n", encoding="utf-8")
            self.write_pack(repo, "service", "service", ["src/service.py", "src/other.py"])
            (repo / "src" / "service.py").write_text("VALUE = 3\n", encoding="utf-8")
            second.write_text("VALUE = 4\n", encoding="utf-8")
            result = self.run_ledger(
                repo, "doctor", "--format", "json", "--max-items", "1"
            )
            report = json.loads(result.stdout)
            stale = [item for item in report["findings"] if item["code"] == "PACK_STALE"]
            self.assertEqual(1, len(stale))
            self.assertEqual("repairable", stale[0]["severity"])
            self.assertEqual(2, stale[0]["details"]["total"])
            self.assertEqual(1, stale[0]["details"]["omitted"])
            self.assertEqual(1, len(stale[0]["details"]["items"]))

    def test_doctor_detects_duplicate_features_overlap_and_missing_tracked_files(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            self.write_pack(repo, "service-a", "service", ["src/service.py"])
            self.write_pack(repo, "service-b", "service", ["src/service.py"])
            missing = self.write_pack(repo, "missing", "missing", ["src/service.py"])
            text = missing.read_text(encoding="utf-8").replace("src/service.py", "src/missing.py")
            missing.write_text(text, encoding="utf-8")
            report = json.loads(
                self.run_ledger(repo, "doctor", "--format", "json", expected=2).stdout
            )
            by_code = {item["code"]: item for item in report["findings"]}
            self.assertEqual("error", by_code["PACK_DUPLICATE_FEATURE"]["severity"])
            self.assertEqual("warning", by_code["PACK_SCOPE_OVERLAP"]["severity"])
            self.assertEqual("repairable", by_code["PACK_MISSING_TRACKED_FILE"]["severity"])

    def test_doctor_reports_invalid_private_state_instead_of_crashing(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            state_path = RUNTIME.context_state_path(repo)
            state_path.parent.mkdir(parents=True, exist_ok=True)
            state_path.write_text("{not json", encoding="utf-8")
            result = self.run_ledger(repo, "doctor", "--format", "json", expected=2)
            report = json.loads(result.stdout)
            finding = next(item for item in report["findings"] if item["code"] == "PRIVATE_STATE_INVALID")
            self.assertEqual("error", finding["severity"])
            self.assertNotIn(str(state_path.parent), result.stdout)

    def test_doctor_never_exposes_foreign_private_session_fields(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            session_id = "foreign-private-secret-session"
            draft = RUNTIME.task_session_draft_path(repo, session_id)
            draft.parent.mkdir(parents=True, exist_ok=True)
            draft.write_text("# Foreign customer secret\n", encoding="utf-8")
            state = RUNTIME.load_context_state(repo)
            state["task_sessions"][session_id] = {
                "draft": RUNTIME.session_draft_ref(repo, draft),
                "publish_path": "docs/changes/2026/08/foreign-secret.md",
                "feature": "foreign-secret-feature",
                "status": "active",
                "updated_at": "2026-08-21T00:00:00+08:00",
                "owner_principal": "p-1111111111111111",
                "resume_epoch": 1,
                "epoch_required": False,
                "continuation_tool": "cursor",
                "grants": [],
            }
            RUNTIME.save_context_state(repo, state)
            result = self.run_ledger(repo, "doctor", "--format", "json")
            self.assertNotIn(session_id, result.stdout)
            self.assertNotIn("foreign-secret", result.stdout)
            self.assertNotIn("Foreign customer", result.stdout)

            state_path = RUNTIME.context_state_path(repo)
            malformed_id = "foreign-malformed-secret"
            state["task_sessions"] = {
                malformed_id: {
                    "owner_principal": "p-1111111111111111",
                    "status": "active",
                }
            }
            state_path.write_text(json.dumps(state), encoding="utf-8")
            malformed = self.run_ledger(repo, "doctor", "--format", "json", expected=2)
            self.assertNotIn(malformed_id, malformed.stdout)
            self.assertNotIn("owner_principal", malformed.stdout)

    def test_doctor_rejects_out_of_range_detail_bounds(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            result = self.run_ledger(repo, "doctor", "--max-items", "0", expected=2)
            self.assertIn("must be from 1 to 100", result.stderr)
            structured = self.run_ledger(
                repo, "doctor", "--format", "json", "--max-items", "0", expected=2
            )
            report = json.loads(structured.stdout)
            self.assertEqual("doctor-v1", report["schema"])
            self.assertEqual("INVALID_ARGUMENT", report["error_code"])
            self.assertEqual("", structured.stderr)

    def test_doctor_validates_explicit_pack_lineage_without_auto_superseding_overlap(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            self.write_pack(repo, "service", "service", ["src/service.py"])
            self.write_pack(
                repo,
                "legacy-service",
                "legacy-service",
                ["src/service.py"],
                status="superseded",
                superseded_by="service",
            )
            report = json.loads(self.run_ledger(repo, "doctor", "--format", "json").stdout)
            codes = {item["code"] for item in report["findings"]}
            self.assertNotIn("PACK_SCOPE_OVERLAP", codes)
            self.assertNotIn("PACK_LINEAGE_INVALID", codes)
            self.assertNotIn("PACK_LINEAGE_BROKEN", codes)

    def test_doctor_reports_broken_links_and_invalid_config_as_findings(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            (repo / "docs" / "specs" / "broken.md").write_text(
                "# Broken\n\n[missing](not-here.md)\n", encoding="utf-8"
            )
            broken = json.loads(self.run_ledger(repo, "doctor", "--format", "json").stdout)
            self.assertIn("BROKEN_LOCAL_LINK", {item["code"] for item in broken["findings"]})

            config = repo / ".context-ledger" / "config.json"
            config.write_text("{not json", encoding="utf-8")
            invalid = self.run_ledger(repo, "doctor", "--format", "json", expected=2)
            report = json.loads(invalid.stdout)
            self.assertIn("CONFIG_INVALID", {item["code"] for item in report["findings"]})
            self.assertNotIn(str(repo), invalid.stdout)

    def test_doctor_warns_when_legacy_active_handoff_instructions_remain(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_repo(repo)
            agents = repo / "AGENTS.md"
            agents.write_text(
                agents.read_text(encoding="utf-8")
                + "\n## Legacy workflow\n\nWrite docs/changes/.active-handoff before editing.\n",
                encoding="utf-8",
            )
            report = json.loads(self.run_ledger(repo, "doctor", "--format", "json").stdout)
            finding = next(
                item for item in report["findings"]
                if item["code"] == "LEGACY_WORKFLOW_CONFLICT"
            )
            self.assertEqual("warning", finding["severity"])
            self.assertEqual(["AGENTS.md"], finding["details"]["items"])


if __name__ == "__main__":
    unittest.main()
