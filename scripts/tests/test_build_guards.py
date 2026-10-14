"""Prove build refusal protects junction targets and missing EXE cannot get a receipt."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

@unittest.skipUnless(sys.platform == "win32", "Windows build guards")
class BuildGuards(unittest.TestCase):
    def test_junction_ancestor_refused_before_output_mutation(self):
        for ancestor in ("dist", "build"):
            with self.subTest(ancestor=ancestor), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                repo = root / "repo"
                (repo / "scripts").mkdir(parents=True)
                script = repo / "scripts/build-dev.ps1"
                shutil.copyfile(ROOT / "scripts/build-dev.ps1", script)
                protected = root / "protected"
                protected.mkdir()
                sentinel = protected / "sentinel.txt"
                sentinel.write_bytes(b"protected content")
                junction = repo / ancestor
                subprocess.run(["cmd.exe", "/c", "mklink", "/J", str(junction), str(protected)],
                               capture_output=True, check=True, timeout=10)
                result = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                                         "-File", str(script), "-CheckOnly"], capture_output=True, timeout=15)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b"Linked build roots", result.stderr)
                self.assertEqual(sentinel.read_bytes(), b"protected content")
                self.assertEqual(list(protected.iterdir()), [sentinel])

    def test_missing_executable_receipt_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            shutil.copyfile(ROOT / "scripts/build-receipt.py", root / "scripts/build-receipt.py")
            result = subprocess.run([sys.executable, "-B", str(root / "scripts/build-receipt.py")],
                                     capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"executable is missing", result.stderr)
            self.assertFalse((root / "dist").exists())

if __name__ == "__main__":
    unittest.main()
