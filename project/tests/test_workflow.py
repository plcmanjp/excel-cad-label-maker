"""File preservation, schema recovery and deterministic job-race boundaries."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys
import tempfile
from threading import Event, Thread
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from converter import LabelSettings, create_drawing, save_drawing
from jobs import Cancelled, Cancellation, Jobs
from settings_store import SettingsError, SettingsStore, defaults
from text_bitmap import glyph_png


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def test_presets_last_settings_rename_delete_and_overwrite(self):
        store = SettingsStore(self.directory)
        changed = {**defaults(), "cell_w": 72, "mode": "display", "font_key": "AutoCAD 표준 (Standard)"}
        store.remember(changed)
        store.save("한글 규격", changed)
        with self.assertRaises(SettingsError):
            store.save("한글 규격", defaults())
        store.save("한글 규격", defaults(), overwrite=True)
        store.rename("한글 규격", "새 규격")
        reloaded = SettingsStore(self.directory)
        self.assertEqual(reloaded.last["cell_w"], 72)
        self.assertEqual(reloaded.last["font_key"], "AutoCAD 표준 (Standard)")
        self.assertEqual(reloaded.presets["새 규격"], defaults())
        self.assertEqual(set(json.loads(store.path.read_text(encoding="utf-8"))), {"version", "last", "presets"})
        for name in ("", "기본 규격", "마지막 설정", "A\nB", "A" * 61):
            with self.assertRaises(SettingsError):
                store.save(name, changed)
        store.delete("새 규격")
        self.assertEqual(SettingsStore(self.directory).presets, {})

    def test_corrupt_unknown_invalid_schema_preserved_until_explicit_recovery(self):
        path = self.directory / "settings.json"
        for contents in [b"bad json", b'{"version":3}', json.dumps({"version": 2, "last": {**defaults(), "cell_w": -1}, "presets": {}}).encode(),
                         json.dumps({"version": 2, "last": {**defaults(), "customer_path": "secret"}, "presets": {}}).encode()]:
            path.write_bytes(contents)
            store = SettingsStore(self.directory)
            self.assertTrue(store.protected)
            self.assertEqual(store.last, defaults())
            with self.assertRaises(SettingsError):
                store.remember(defaults())
            self.assertEqual(path.read_bytes(), contents)
            backup = store.recover()
            self.assertEqual(backup.read_bytes(), contents)
            self.assertFalse(SettingsStore(self.directory).protected)

    def test_failed_setting_replace_preserves_disk_and_memory(self):
        store = SettingsStore(self.directory)
        store.remember(defaults())
        old = store.path.read_bytes()
        with patch("settings_store.os.replace", side_effect=PermissionError("denied")), self.assertRaises(SettingsError):
            store.remember({**defaults(), "cell_w": 70})
        self.assertEqual(store.path.read_bytes(), old)
        self.assertEqual(store.last, defaults())
        self.assertEqual(list(self.directory.glob("*.tmp")), [])

    def test_cancel_after_write_before_replace_preserves_existing_dxf(self):
        output = self.directory / "existing.dxf"
        output.write_bytes(b"existing output")
        original = sha256(output.read_bytes()).hexdigest()
        token = Cancellation()
        doc = create_drawing([["A"]], LabelSettings())
        actual_write = doc.write
        def write(stream):
            actual_write(stream)
            token.cancel()
        with patch.object(doc, "write", side_effect=write), self.assertRaises(Cancelled):
            save_drawing(doc, output, token)
        self.assertEqual(sha256(output.read_bytes()).hexdigest(), original)
        self.assertEqual(list(self.directory.glob("*.tmp")), [])

    def test_cancel_after_atomic_commit_is_success(self):
        token = Cancellation()
        output = self.directory / "result.dxf"
        save_drawing(create_drawing([["A"]], LabelSettings()), output, token)
        self.assertTrue(token.committed)
        self.assertFalse(token.cancel())
        token.check()
        self.assertTrue(output.is_file())

    def test_os_replace_failure_preserves_existing_output(self):
        output = self.directory / "existing.dxf"
        output.write_bytes(b"existing")
        with patch("converter.os.replace", side_effect=PermissionError()), self.assertRaises(PermissionError):
            save_drawing(create_drawing([["A"]], LabelSettings()), output, Cancellation())
        self.assertEqual(output.read_bytes(), b"existing")
        self.assertEqual(list(self.directory.glob("*.tmp")), [])

    def test_cancel_and_commit_are_serialized(self):
        entered, release = Event(), Event()
        token = Cancellation()
        def commit():
            def action():
                entered.set()
                self.assertTrue(release.wait(2))
            token.commit(action)
        worker = Thread(target=commit)
        worker.start()
        self.assertTrue(entered.wait(2))
        result = []
        cancel_thread = Thread(target=lambda: result.append(token.cancel()))
        cancel_thread.start()
        release.set()
        worker.join(2)
        cancel_thread.join(2)
        self.assertEqual(result, [False])

    def test_job_generation_rejects_old_completions_and_close(self):
        jobs = Jobs()
        started, release = Event(), Event()
        def old(token, report):
            started.set()
            release.wait(2)
            return "old"
        first = jobs.start("read", old)
        self.assertTrue(started.wait(2))
        second = jobs.start("read", lambda token, report: "new")
        release.set()
        results = [jobs.queue.get(timeout=2), jobs.queue.get(timeout=2)]
        current = [r for r in results if r.generation == jobs.generation]
        self.assertEqual((current[0].generation, current[0].value), (second, "new"))
        self.assertTrue(any(r.generation == first and r.status == "cancelled" for r in results))
        jobs.close()
        with self.assertRaises(RuntimeError):
            jobs.start("read", lambda token, report: None)

    def test_gdi_preview_applies_width_factor_and_retains_height(self):
        normal = glyph_png("한글 ABC 001", "맑은 고딕", 24, 1.0, "#222222")
        compressed = glyph_png("한글 ABC 001", "맑은 고딕", 24, .65, "#222222")
        normal_size = struct.unpack(">II", normal[16:24])
        compressed_size = struct.unpack(">II", compressed[16:24])
        self.assertEqual(compressed_size, (round(normal_size[0] * .65), normal_size[1]))

    def test_colliding_reserved_preset_in_disk_is_preserved(self):
        path = self.directory / "settings.json"
        data = json.dumps({"version": 2, "last": defaults(), "presets": {"마지막 설정": defaults()}}, ensure_ascii=False).encode("utf-8")
        path.write_bytes(data)
        store = SettingsStore(self.directory)
        self.assertTrue(store.protected)
        self.assertEqual(path.read_bytes(), data)


if __name__ == "__main__":
    unittest.main()
