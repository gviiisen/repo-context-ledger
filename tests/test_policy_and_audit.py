import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
SPEC = importlib.util.spec_from_file_location("repo_context_ledger_policy_runtime", LEDGER)
RUNTIME = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNTIME)

FAILED_CHANGE = ROOT / "docs/changes/2026/08/20260822003651-gviiisen-9d9c476d8a-pin-standalone-runtime-checkout-line-endings.md"
RESOLUTION_CHANGE = ROOT / "docs/changes/2026/08/20260822003911-gviiisen-e688fa6347-classify-git-attributes-as-repository-configurat.md"


class PolicyAndAuditTests(unittest.TestCase):
    def command(self, *args: str, expected: int = 0):
        result = subprocess.run(
            args,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        return result

    def git(self, repo: Path, *args: str, expected: int = 0):
        return self.command("git", "-C", str(repo), *args, expected=expected)

    def ledger(self, repo: Path, *args: str, expected: int = 0):
        return self.command(sys.executable, str(LEDGER), "--repo", str(repo), *args, expected=expected)

    def initialized_repo(self, root: Path) -> Path:
        repo = root / "repo"
        repo.mkdir()
        self.git(repo, "init", "-b", "main")
        self.git(repo, "config", "user.name", "Policy Test")
        self.git(repo, "config", "user.email", "policy@example.test")
        (repo / "src").mkdir()
        (repo / "src/app.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.ledger(repo, "init")
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-m", "initialize")
        return repo

    def test_policy_classifies_actual_canonical_derived_delta(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(Path(raw))
            spec = repo / "docs/specs/extra.md"
            spec.write_text("# Extra stable context\n", encoding="utf-8")
            self.git(repo, "add", str(spec))
            self.git(repo, "commit", "-m", "merge stable context without derived sync")
            self.git(repo, "switch", "-c", "derived-sync")
            self.ledger(repo, "sync", "--derived")
            self.git(repo, "add", "-A")
            self.git(repo, "commit", "-m", "refresh derived outputs")

            result = self.ledger(repo, "policy", "--base", "main")
            self.assertIn("Ledger policy mode: derived-only", result.stdout)
            self.assertIn("Ledger policy passed.", result.stdout)

    def test_derived_policy_rejects_a_hand_edited_generated_index(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(Path(raw))
            spec = repo / "docs/specs/extra.md"
            spec.write_text("# Extra stable context\n", encoding="utf-8")
            self.git(repo, "add", str(spec))
            self.git(repo, "commit", "-m", "merge stable context without derived sync")
            self.git(repo, "switch", "-c", "derived-sync")
            self.ledger(repo, "sync", "--derived")
            index = repo / "docs/specs/README.md"
            index.write_text(
                index.read_text(encoding="utf-8").replace(
                    "Extra stable context", "Hand-edited stable context"
                ),
                encoding="utf-8",
            )
            self.git(repo, "add", "-A")
            self.git(repo, "commit", "-m", "hand edit derived output")

            result = self.ledger(repo, "policy", "--base", "main", expected=2)
            self.assertIn("Ledger policy mode: derived-only", result.stdout)
            self.assertIn("requires sync --derived action update", result.stderr)

    def test_unmanaged_prose_in_generated_index_is_not_derived_only(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(Path(raw))
            spec = repo / "docs/specs/extra.md"
            spec.write_text("# Extra stable context\n", encoding="utf-8")
            self.git(repo, "add", str(spec))
            self.git(repo, "commit", "-m", "merge stable context without derived sync")
            self.git(repo, "switch", "-c", "derived-sync")
            self.ledger(repo, "sync", "--derived")
            index = repo / "docs/specs/README.md"
            index.write_text(index.read_text(encoding="utf-8") + "\nHuman prose.\n", encoding="utf-8")
            config = RUNTIME.load_config(repo)
            merge_base, changed = RUNTIME.changed_scope_paths(repo, "main")
            self.assertFalse(RUNTIME.derived_only_changes(repo, config, merge_base, changed))

    def test_readme_prose_outside_the_managed_block_is_not_derived_only(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(Path(raw))
            self.git(repo, "switch", "-c", "readme-prose")
            readme = repo / "README.md"
            readme.write_text(readme.read_text(encoding="utf-8") + "\nHuman prose.\n", encoding="utf-8")
            config = RUNTIME.load_config(repo)
            merge_base, changed = RUNTIME.changed_scope_paths(repo, "main")
            self.assertFalse(RUNTIME.derived_only_changes(repo, config, merge_base, changed))

    def test_policy_does_not_treat_source_change_as_derived(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(Path(raw))
            self.git(repo, "switch", "-c", "ordinary")
            (repo / "src/app.py").write_text("VALUE = 2\n", encoding="utf-8")
            result = self.ledger(repo, "policy", "--base", "main", expected=2)
            self.assertIn("Ledger policy mode: ordinary", result.stdout)
            self.assertIn("Changed-scope strict Coverage check failed", result.stderr)

    def test_historical_dispositions_are_ledger_docs_not_implementation(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(Path(raw))
            config = RUNTIME.load_config(repo)
            self.assertEqual(
                "docs",
                RUNTIME.coverage_path_kind(
                    config, "docs/audit-dispositions/known-finding.json"
                ),
            )

    def install_history_fixture(self, repo: Path) -> tuple[str, str]:
        changes = repo / "docs/changes/2026/08"
        changes.mkdir(parents=True, exist_ok=True)
        failed_rel = "docs/changes/2026/08/failed-change.md"
        resolved_rel = "docs/changes/2026/08/resolution-change.md"
        failed = repo / failed_rel
        resolved = repo / resolved_rel
        failed.write_bytes(FAILED_CHANGE.read_bytes())
        resolved.write_bytes(RESOLUTION_CHANGE.read_bytes())
        return failed_rel, resolved_rel

    def test_historical_disposition_is_hash_bound_and_resolves_finding(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(Path(raw))
            failed_rel, resolved_rel = self.install_history_fixture(repo)
            failed = repo / failed_rel
            disposition_root = repo / "docs/audit-dispositions"
            disposition_root.mkdir(parents=True)
            disposition = {
                "schema": "historical-disposition-v1",
                "record": failed_rel,
                "record_sha256": "sha256:" + hashlib.sha256(failed.read_bytes()).hexdigest(),
                "finding": "FINAL_VERIFICATION_FAILED",
                "disposition": "resolved-by-later-change",
                "reason": "A later completed Change added the missing repository configuration coverage.",
                "resolved_by": resolved_rel,
                "approved_by": "maintainer",
                "approved_at": "2026-08-27T23:50:00+08:00",
            }
            path = disposition_root / "failed-change.json"
            path.write_text(json.dumps(disposition), encoding="utf-8")

            config = RUNTIME.load_config(repo)
            accepted, errors, count = RUNTIME.load_historical_dispositions(repo, config)
            self.assertEqual(1, count)
            self.assertEqual([], errors)
            self.assertIn((failed_rel, "FINAL_VERIFICATION_FAILED"), accepted)

            failed.write_text(failed.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            _, errors, _ = RUNTIME.load_historical_dispositions(repo, config)
            self.assertTrue(any("record_sha256 does not match" in error for error in errors))

    def test_as_recorded_audit_separates_unresolved_findings(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(Path(raw))
            self.install_history_fixture(repo)
            recorded = self.ledger(repo, "audit", "--history", "--policy", "as-recorded")
            self.assertIn("Unresolved historical findings: 1", recorded.stdout)
            unresolved = self.ledger(
                repo,
                "audit", "--history", "--policy", "as-recorded", "--fail-on", "unresolved",
                expected=2,
            )
            self.assertIn("unresolved FINAL_VERIFICATION_FAILED", unresolved.stderr)


if __name__ == "__main__":
    unittest.main()
