import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "bin" / "concise-default.py"
SKILL = REPO / "SKILL.md"

class ConciseDefaultCliTest(unittest.TestCase):
    def run_cli(self, home: Path, *args: str):
        env = os.environ.copy()
        env["USERPROFILE"] = str(home)
        env["HOME"] = str(home)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=REPO,
            env=env,
            text=True,
            capture_output=True,
        )

    def install_skill(self, home: Path):
        target = home / ".codex" / "skills" / "concise"
        target.mkdir(parents=True)
        shutil.copyfile(SKILL, target / "SKILL.md")

    def test_on_writes_codex_instructions_and_status_observes_config(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            self.install_skill(home)

            on = self.run_cli(home, "on", "ultra")
            self.assertEqual(on.returncode, 0, on.stderr + on.stdout)
            self.assertIn("concise default ON (level: ultra)", on.stdout)
            instructions = home / ".codex" / "instructions.md"
            self.assertTrue(instructions.exists())
            self.assertIn("答复要像", instructions.read_text(encoding="utf-8"))

            status = self.run_cli(home, "status")
            self.assertEqual(status.returncode, 0, status.stderr + status.stdout)
            self.assertIn("Codex CLI: ON", status.stdout)
            self.assertIn("Codex App: OFF", status.stdout)

    def test_off_removes_generated_targets_but_keeps_saved_level(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            self.install_skill(home)
            self.assertEqual(self.run_cli(home, "on", "lite").returncode, 0)

            off = self.run_cli(home, "off")
            self.assertEqual(off.returncode, 0, off.stderr + off.stdout)
            self.assertFalse((home / ".codex" / "instructions.md").exists())
            self.assertEqual((home / ".config" / "concise" / "config").read_text(encoding="utf-8").strip(), "lite")

    def test_rejects_full_level(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            self.install_skill(home)
            result = self.run_cli(home, "on", "full")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("level must be lite or ultra", result.stderr + result.stdout)

if __name__ == "__main__":
    unittest.main()