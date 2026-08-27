import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
SPEC = importlib.util.spec_from_file_location("ledger_lock_trust", LEDGER)
assert SPEC and SPEC.loader
LEDGER_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LEDGER_MODULE)


class LockAndPresetTrustTests(unittest.TestCase):
    def run_ledger(
        self,
        repo: Path,
        *args: str,
        expected: int = 0,
        principal: str = "test-owner",
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"
        environment["REPO_CONTEXT_LEDGER_PRINCIPAL"] = principal
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

    @staticmethod
    def session_id(result: subprocess.CompletedProcess[str]) -> str:
        return next(
            line.removeprefix("Session: ").strip()
            for line in result.stdout.splitlines()
            if line.startswith("Session: ")
        )

    def initialized_repo(self, raw: str) -> Path:
        repo = Path(raw) / "repo"
        repo.mkdir()
        subprocess.run(
            ["git", "-C", str(repo), "init", "-b", "main"],
            check=True,
            text=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.name", "Trust Test"], check=True
        )
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "trust@example.test"], check=True
        )
        self.run_ledger(repo, "init")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-m", "initialize"],
            check=True,
            text=True,
            capture_output=True,
        )
        return repo

    def test_doctor_distinguishes_live_and_stale_write_locks(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(raw)
            lock = repo / ".context-ledger/.write.lock"
            lock.write_text(
                f"version=1 pid={os.getpid()} started=2026-08-27T17:00:00+08:00 "
                "command=start nonce=live-test\n",
                encoding="utf-8",
            )
            live = json.loads(self.run_ledger(repo, "doctor", "--format", "json").stdout)
            live_finding = next(item for item in live["findings"] if item["code"] == "WRITE_LOCK_ACTIVE")
            self.assertEqual("warning", live_finding["severity"])
            self.assertIn("pid=", live_finding["details"]["items"][0])
            self.assertNotIn(str(repo), json.dumps(live_finding))

            lock.write_text(
                "version=1 pid=999999999 started=2026-08-27T16:00:00+08:00 "
                "command=finish nonce=stale-test\n",
                encoding="utf-8",
            )
            stale = json.loads(self.run_ledger(repo, "doctor", "--format", "json").stdout)
            stale_finding = next(item for item in stale["findings"] if item["code"] == "WRITE_LOCK_STALE")
            self.assertEqual("repairable", stale_finding["severity"])
            self.assertTrue(stale_finding["suggested_actions"])

    def test_repo_lock_never_unlinks_a_replaced_owner_token(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "repo"
            repo.mkdir()
            lock = repo / ".context-ledger/.write.lock"
            with LEDGER_MODULE.repo_lock(repo):
                owned = lock.read_text(encoding="utf-8")
                self.assertRegex(owned, r"\bnonce=[0-9a-f]{32}\b")
                lock.write_text(
                    "version=1 pid=42 started=2026-08-27T17:00:00+08:00 "
                    "command=replacement nonce=other-owner\n",
                    encoding="utf-8",
                )
            self.assertTrue(lock.exists())
            self.assertIn("nonce=other-owner", lock.read_text(encoding="utf-8"))

    def test_verification_preset_requires_exact_principal_local_trust(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = self.initialized_repo(raw)
            marker = repo / "preset-ran.txt"
            config_path = repo / ".context-ledger/config.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["verification"]["presets"]["trusted-check"] = {
                "argv": [
                    sys.executable,
                    "-c",
                    "from pathlib import Path; Path('preset-ran.txt').write_text('first')",
                ],
                "cwd": ".",
                "timeout": 30,
                "sensitive": False,
                "platforms": [LEDGER_MODULE.verification_platform()],
            }
            config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
            started = self.run_ledger(repo, "start", "--title", "Trust reviewed preset")
            session = self.session_id(started)

            blocked = self.run_ledger(
                repo,
                "verify",
                "--session",
                session,
                "--preset",
                "trusted-check",
                expected=2,
            )
            self.assertFalse(marker.exists())
            digest = re.search(r"sha256:[0-9a-f]{64}", blocked.stderr)
            self.assertIsNotNone(digest, blocked.stderr)

            trusted = self.run_ledger(
                repo,
                "verify",
                "--session",
                session,
                "--preset",
                "trusted-check",
                "--trust-digest",
                digest.group(0),
            )
            self.assertIn("Recorded passed verification", trusted.stdout)
            self.assertEqual("first", marker.read_text(encoding="utf-8"))
            self.assertNotIn("preset-trust", self._git_status(repo))

            marker.unlink()
            foreign = self.run_ledger(
                repo,
                "verify",
                "--session",
                session,
                "--preset",
                "trusted-check",
                expected=2,
                principal="other-user",
            )
            self.assertIn("trust", foreign.stderr.casefold())
            self.assertFalse(marker.exists())

            config["verification"]["presets"]["trusted-check"]["argv"][-1] = (
                "from pathlib import Path; Path('preset-ran.txt').write_text('changed')"
            )
            config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
            changed = self.run_ledger(
                repo,
                "verify",
                "--session",
                session,
                "--preset",
                "trusted-check",
                expected=2,
            )
            self.assertIn("trust", changed.stderr.casefold())
            self.assertFalse(marker.exists())

    @staticmethod
    def _git_status(repo: Path) -> str:
        result = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain"],
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.stdout


if __name__ == "__main__":
    unittest.main()
