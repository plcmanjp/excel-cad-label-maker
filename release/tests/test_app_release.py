"""Synthetic release packages exercise publication refusal boundaries without publishing."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/package-app-release.py"
spec = importlib.util.spec_from_file_location("app_packager", SCRIPT)
packager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packager)


class AppReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.build, self.output = self.root / "build", self.root / "output"
        self.snapshot = {"commit": "synthetic-commit", "branch": "main", "dirty": False}
        self.git = patch.object(packager, "git_snapshot", return_value=self.snapshot)
        self.git.start()
        self.addCleanup(self.git.stop)
        self.source = "project/P001-excel-cad-label/src/excel_cad_label.py"
        self.asset = "project/P001-excel-cad-label/src/assets/app-icon.ico"
        sources = {self.source: b"# synthetic entrypoint\n", self.asset: b"synthetic icon",
                   "project/P001-excel-cad-label/src/app_version.py": b"APP_VERSION = '0.2.0'\n",
                   "project/requirements-dev.lock.txt": b"synthetic lock\n"}
        for name, data in sources.items():
            self.write(self.root / name, data)
        config = {"version": "0.2.0", "tag": "v0.2.0", "release_type": "recovered-source-build",
                  "original_baseline_replaced": False, "binary_name": "Excel_CAD_Label.exe"}
        self.write(self.root / "release/app-release.json", json.dumps(config).encode())
        files = {"Excel_CAD_Label.exe": b"SYNTHETIC-NOT-RUNNABLE", "VERSION": b"0.2.0\n",
                 "_internal/assets/app-icon.ico": sources[self.asset], "third_party/README.md": b"notice\n"}
        for name, data in files.items():
            self.write(self.build / name, data)
        self.receipt = {"type": "release-build", "source_dirty": False, "source_commit": "synthetic-commit",
                        "app_version": "0.2.0", "lock_sha256": packager.digest(sources["project/requirements-dev.lock.txt"]),
                        "entrypoint": {"path": self.source, "sha256": packager.digest(sources[self.source])},
                        "sources": {self.source: packager.digest(sources[self.source])},
                        "assets": {self.asset: packager.digest(sources[self.asset])},
                        "files": {name: packager.digest(data) for name, data in files.items()}}
        self.write_receipt()

    def write(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def write_receipt(self):
        self.write(self.build / "build-receipt.json", json.dumps(self.receipt).encode())

    def invoke(self):
        return packager.package_build(self.root, self.build, self.output)

    def test_zip_manifest_and_checksum_bind_actual_executable(self):
        result = self.invoke()
        archive = self.output / result["archive"]
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), result["sha256"])
        self.assertIn(result["sha256"], (self.output / "SHA256SUMS.txt").read_text())
        with zipfile.ZipFile(archive) as package:
            manifest = json.loads(package.read("Excel-CAD-Label-Maker/release-manifest.json"))
            self.assertEqual(manifest["source_commit"], "synthetic-commit")
            self.assertEqual(manifest["binary_sha256"], packager.digest(package.read("Excel-CAD-Label-Maker/Excel_CAD_Label.exe")))
            for name, expected in manifest["files"].items():
                self.assertEqual(packager.digest(package.read("Excel-CAD-Label-Maker/" + name)), expected)
        before = archive.read_bytes()
        with self.assertRaisesRegex(ValueError, "will not be overwritten"):
            self.invoke()
        self.assertEqual(archive.read_bytes(), before)

    def test_dirty_nonmain_stale_or_development_receipt_refused(self):
        for field, value in [("dirty", True), ("branch", "feature/test")]:
            with self.subTest(field=field), patch.object(packager, "git_snapshot", return_value=dict(self.snapshot, **{field: value})):
                with self.assertRaisesRegex(ValueError, "clean main"):
                    self.invoke()
        for field, value in [("source_dirty", True), ("source_commit", "stale"), ("type", "development-build")]:
            with self.subTest(field=field):
                original = self.receipt[field]
                self.receipt[field] = value
                self.write_receipt()
                with self.assertRaisesRegex(ValueError, "receipt or commit mismatch"):
                    self.invoke()
                self.receipt[field] = original
        self.assertFalse(self.output.exists())

    def test_changed_or_extra_package_files_refused(self):
        binary = self.build / "Excel_CAD_Label.exe"
        original = binary.read_bytes()
        binary.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Packaged file hash mismatch"):
            self.invoke()
        binary.write_bytes(original)
        (self.build / "extra.xlsx").write_bytes(b"synthetic unwanted file")
        with self.assertRaisesRegex(ValueError, "Unlisted or missing"):
            self.invoke()
        self.assertFalse(self.output.exists())

    def test_version_source_and_path_drift_refused(self):
        version = self.build / "VERSION"
        version.write_text("0.1.0")
        with self.assertRaisesRegex(ValueError, "version mismatch"):
            self.invoke()
        version.write_bytes(b"0.2.0\n")
        (self.root / self.asset).write_bytes(b"changed icon")
        with self.assertRaisesRegex(ValueError, "Source or asset hash mismatch"):
            self.invoke()
        for name in ["../outside", "/absolute", "folder\\file", "C:/file"]:
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "Unsafe receipt path"):
                packager.safe_relative(name)
        self.assertFalse(self.output.exists())

    def test_existing_checksum_refused_before_archive_creation(self):
        self.output.mkdir()
        sums = self.output / "SHA256SUMS.txt"
        sums.write_bytes(b"protected checksum")
        with self.assertRaisesRegex(ValueError, "will not be overwritten"):
            self.invoke()
        self.assertEqual(sums.read_bytes(), b"protected checksum")
        self.assertEqual(list(self.output.iterdir()), [sums])

    def test_dangling_checksum_link_refused_without_target_creation(self):
        self.output.mkdir()
        target = self.root / "outside-output.txt"
        sums = self.output / "SHA256SUMS.txt"
        try:
            sums.symlink_to(target)
        except OSError as error:
            self.skipTest("Symlink creation unavailable: " + str(error))
        with self.assertRaisesRegex(ValueError, "Linked package paths"):
            self.invoke()
        self.assertFalse(target.exists())
        self.assertTrue(sums.is_symlink())
        self.assertEqual(list(self.output.iterdir()), [sums])


if __name__ == "__main__":
    unittest.main()
