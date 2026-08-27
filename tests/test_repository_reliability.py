import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"


class RepositoryReliabilityTests(unittest.TestCase):
    def run_ledger(
        self,
        repo: Path,
        *args: str,
        expected: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"
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

    def init_git_repo(self, repo: Path) -> None:
        repo.mkdir(parents=True)
        self.run_git(repo, "init", "-b", "main")
        self.run_git(repo, "config", "user.name", "Reliability Test")
        self.run_git(repo, "config", "user.email", "reliability@example.test")
        source = repo / "src/service.py"
        source.parent.mkdir(parents=True)
        source.write_text("VALUE = 1\n", encoding="utf-8")
        self.run_git(repo, "add", ".")
        self.run_git(repo, "commit", "-m", "initial")

    @staticmethod
    def session_id(result: subprocess.CompletedProcess[str]) -> str:
        for line in result.stdout.splitlines():
            if line.startswith("Session: "):
                return line.removeprefix("Session: ").strip()
        raise AssertionError(result.stdout)

    def test_evidence_accepts_unquoted_unicode_and_space_paths(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            self.run_ledger(repo, "init")
            started = self.run_ledger(
                repo,
                "start",
                "--title",
                "Repair localized paths",
                "--feature",
                "localized-paths",
            )
            paths = (
                "src/space in name.py",
                "src/中文目录/提现处理器.py",
            )
            for relative in paths:
                path = repo / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("VALUE = 2\n", encoding="utf-8")

            args: list[str] = ["evidence", "--session", self.session_id(started)]
            for relative in paths:
                args.extend(("--path", relative))
            evidence = self.run_ledger(repo, *args)

            for relative in paths:
                self.assertIn(f"- {relative}\n", evidence.stdout.replace("\r\n", "\n"))

    def test_evidence_uses_the_destination_of_a_unicode_rename(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            self.run_ledger(repo, "init")
            original = repo / "src/old name.py"
            original.write_text("VALUE = 4\n", encoding="utf-8")
            self.run_git(repo, "add", ".")
            self.run_git(repo, "commit", "-m", "add rename source")
            started = self.run_ledger(
                repo,
                "start",
                "--title",
                "Rename localized source",
                "--feature",
                "localized-rename",
            )
            destination = "src/中文 新文件.py"
            self.run_git(repo, "mv", "src/old name.py", destination)

            evidence = self.run_ledger(
                repo,
                "evidence",
                "--session",
                self.session_id(started),
                "--path",
                destination,
            )
            self.assertIn(f"- {destination}\n", evidence.stdout.replace("\r\n", "\n"))

    @unittest.skipIf(os.name == "nt", "POSIX-only Git filename characters")
    def test_git_path_reader_preserves_control_and_arrow_filenames(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            self.run_ledger(repo, "init")
            paths = {
                "src/arrow -> file.py",
                "src/tab\tname.py",
                "src/line\nbreak.py",
                'src/quote"file.py',
                "src/backslash\\file.py",
            }
            for relative in paths:
                path = repo / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("VALUE = 3\n", encoding="utf-8")

            probe = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    (
                        "import importlib.util,json,sys;from pathlib import Path;"
                        "spec=importlib.util.spec_from_file_location('ledger',sys.argv[1]);"
                        "module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);"
                        "print(json.dumps(module.git_dirty_paths(Path(sys.argv[2])),ensure_ascii=False))"
                    ),
                    str(LEDGER),
                    str(repo),
                ],
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
            )
            self.assertEqual(0, probe.returncode, probe.stderr)
            self.assertTrue(paths.issubset(set(json.loads(probe.stdout))))

    def test_changed_scope_check_fails_closed_when_git_status_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            self.init_git_repo(repo)
            self.run_ledger(repo, "init")
            self.run_git(repo, "add", ".")
            self.run_git(repo, "commit", "-m", "initialize ledger")
            (repo / ".git/index").write_bytes(b"not-a-git-index")

            result = self.run_ledger(
                repo,
                "check",
                "--strict",
                "--changed-since",
                "main",
                expected=2,
            )
            self.assertIn("Git command failed", result.stderr)
            self.assertIn("status", result.stderr)
            machine = self.run_ledger(
                repo,
                "check",
                "--strict",
                "--changed-since",
                "main",
                "--format",
                "json",
                expected=2,
            )
            self.assertEqual("GIT_COMMAND_FAILED", json.loads(machine.stdout)["error_code"])

    @unittest.skipIf(os.name == "nt", "POSIX file modes are not enforced on Windows")
    def test_init_and_sync_preserve_existing_file_modes(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            readme = repo / "README.md"
            readme.write_text("# Existing\n", encoding="utf-8")
            readme.chmod(0o644)

            self.run_ledger(repo, "init")
            self.assertEqual(0o644, stat.S_IMODE(readme.stat().st_mode))

            readme.chmod(0o644)
            self.run_ledger(repo, "sync")
            self.assertEqual(0o644, stat.S_IMODE(readme.stat().st_mode))


if __name__ == "__main__":
    unittest.main()
