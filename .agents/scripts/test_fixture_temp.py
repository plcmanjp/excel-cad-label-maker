"""Boundary and preservation checks; all generated payloads remain in OS Temp."""
import os
from pathlib import Path
import stat
import subprocess
import unittest
from unittest import mock

import fixture_temp as fixture


class FixtureTempTests(unittest.TestCase):
    def test_real_path_unique_and_repo_scoped(self):
        first = fixture.create_run()
        second = fixture.create_run()
        workspace, base, blocked = fixture.validate_base()
        self.assertNotEqual(first, second)
        self.assertEqual(first.parent, second.parent)
        self.assertTrue(first.is_relative_to(base))
        self.assertFalse(first.is_relative_to(workspace))
        self.assertFalse(any(first.is_relative_to(root) for root in blocked))
        other = first / "synthetic-repository"
        other.mkdir()
        self.assertNotEqual(first.parent, fixture.create_run(other).parent)
        print("PRESERVED_FIXTURE_RUN=" + str(first))

    def test_normal_cleanup_and_failure_preserve_payload(self):
        before = os.environ.copy()
        normal = fixture.FixtureDirectory()
        with normal as name:
            payload = Path(name) / "normal.txt"
            payload.write_bytes(b"normal")
        normal.cleanup()
        self.assertEqual(payload.read_bytes(), b"normal")
        failed = fixture.FixtureDirectory()
        with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
            with failed as name:
                failed_payload = Path(name) / "failure.txt"
                failed_payload.write_bytes(b"failure")
                raise RuntimeError("synthetic failure")
        self.assertEqual(failed_payload.read_bytes(), b"failure")
        self.assertEqual(os.environ, before)
        print("PRESERVED_FAILURE_RUN=" + failed.name)

    def test_workspace_and_sync_roots_rejected_before_creation(self):
        base = Path(fixture.tempfile.gettempdir()).resolve()
        with self.assertRaises(ValueError):
            fixture.create_run(base)
        with mock.patch.object(fixture, "sync_roots", return_value=[base]):
            with self.assertRaises(ValueError):
                fixture.create_run()
        with mock.patch.dict(os.environ, {"OneDriveFixture": str(base)}):
            with self.assertRaises(ValueError):
                fixture.create_run()

    def test_invalid_environment_and_registry_failure_are_not_ignored(self):
        with mock.patch.dict(os.environ, {"OneDriveFixture": "relative-root"}):
            with self.assertRaises(ValueError):
                fixture.create_run()
        with mock.patch.object(fixture, "sync_roots", side_effect=PermissionError("registry")):
            with self.assertRaises(PermissionError):
                fixture.create_run()

    def test_existing_link_and_reparse_ancestors_rejected(self):
        # Windows runners can expose an 8.3 Temp alias; create_run uses its
        # resolved spelling after validating the actual ancestor chain.
        base = Path(fixture.tempfile.gettempdir()).resolve(strict=True)
        original = Path.lstat
        for mode, attributes in ((stat.S_IFLNK, 0), (stat.S_IFDIR, 0x400)):
            def observed(path, *args, **kwargs):
                if path == base / "excel-cad-harness":
                    return mock.Mock(st_mode=mode, st_file_attributes=attributes)
                return original(path, *args, **kwargs)
            with self.subTest(mode=mode), mock.patch.object(Path, "lstat", observed):
                with self.assertRaises(ValueError):
                    fixture.create_run()

    @unittest.skipUnless(os.name == "nt", "Windows junction counterexample")
    def test_real_junction_is_rejected_and_preserved(self):
        root = fixture.create_run()
        target = root / "target"
        target.mkdir()
        link = root / "junction"
        result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                                capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        with mock.patch.object(fixture.tempfile, "gettempdir", return_value=str(link)):
            with self.assertRaises(ValueError):
                fixture.create_run()
        self.assertTrue(link.is_dir())
        self.assertTrue(target.is_dir())

    def test_counterexample_rename_keeps_bytes_and_directory(self):
        root = fixture.create_run()
        path = root / "CURRENT.md"
        path.write_bytes(b"previous")
        fixture.preserve_for_absence(path)
        fixture.preserve_for_absence(path)
        self.assertFalse(path.exists())
        self.assertEqual(next(root.glob("CURRENT.md.preserved-*")).read_bytes(), b"previous")
        directory = root / "month"
        directory.mkdir()
        (directory / "journal.md").write_bytes(b"journal")
        fixture.preserve_for_absence(directory)
        self.assertEqual(next(root.glob("month.preserved-*" )).joinpath("journal.md").read_bytes(), b"journal")


if __name__ == "__main__":
    unittest.main()
