from pathlib import Path
from queue import Empty
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from update_check import ReleaseInfo, UpdateResult, release_page_url
from update_notice import UpdateNotifier

RELEASE = ReleaseInfo("0.2.0", "v0.2.0", release_page_url("v0.2.0"), "app.zip")


class UpdateNoticeTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.parent = ttk.Frame(self.root)
        self.parent.pack()
        self.errors = []
        self.root.report_callback_exception = lambda *args: self.errors.append(args)

    def notifier(self, result, **kwargs):
        return UpdateNotifier(self.root, self.parent, current_version="0.1.0",
                               checker=lambda version: result, auto_check=False, **kwargs)

    def pump(self, until, timeout=2):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.root.update()
            if until():
                self.assertFalse(self.errors)
                return
            time.sleep(.01)
        self.fail("GUI condition timed out")

    def test_newer_result_shows_real_dialog_and_later_closes_it(self):
        notice = self.notifier(UpdateResult("available", RELEASE))
        notice.check()
        self.pump(lambda: notice.dialog is not None)
        self.assertEqual(notice.dialog.title(), "새 버전 알림")
        self.assertIsNone(self.root.grab_current())
        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)
        labels = [w.cget("text") for w in descendants(notice.dialog) if isinstance(w, ttk.Label)]
        self.assertIn("현재 버전: 0.1.0\n최신 버전: 0.2.0", labels)
        later = next(w for w in descendants(notice.dialog) if isinstance(w, ttk.Button) and w.cget("text") == "나중에")
        later.invoke()
        self.assertFalse(notice.dialog.winfo_exists())

    def test_startup_current_and_failures_do_not_show_message_boxes(self):
        for result in [UpdateResult("current", RELEASE), UpdateResult("unavailable")]:
            notice = self.notifier(result)
            with patch("update_notice.messagebox.showinfo") as message:
                notice.check()
                self.pump(lambda: not notice._active)
                self.assertIsNone(notice.dialog)
                message.assert_not_called()

    def test_manual_current_feedback(self):
        notice = self.notifier(UpdateResult("current", RELEASE))
        with patch("update_notice.messagebox.showinfo") as message:
            notice.check(manual=True)
            self.pump(lambda: not notice._active)
            message.assert_called_once()

    def test_no_duplicate_queries_and_no_duplicate_dialogs(self):
        checker = Mock(return_value=UpdateResult("available", RELEASE))
        notice = UpdateNotifier(self.root, self.parent, checker=checker, auto_check=False)
        notice.check()
        notice.check()
        self.pump(lambda: notice.dialog is not None)
        checker.assert_called_once()
        dialog = notice.dialog
        notice.show_notice(RELEASE)
        self.assertIs(notice.dialog, dialog)

    def test_excel_dialog_scope_defers_notice(self):
        notice = self.notifier(UpdateResult("available", RELEASE))
        with notice.defer_notices():
            notice.check()
            self.pump(lambda: notice._pending is not None)
            self.assertIsNone(notice.dialog)
        self.pump(lambda: notice.dialog is not None)

    def test_worker_completion_after_close_does_not_touch_tk(self):
        started, release = threading.Event(), threading.Event()
        def checker(version):
            started.set()
            release.wait(2)
            return UpdateResult("available", RELEASE)
        notice = UpdateNotifier(self.root, self.parent, checker=checker, auto_check=True)
        notice.check()
        self.assertTrue(started.wait(1))
        self.root.update()  # Still responsive while network work waits.
        self.root.destroy()
        self._cleanups.clear()  # Already destroyed this root.
        release.set()
        self.assertEqual(notice._queue.get(timeout=1)[1].status, "available")
        self.assertTrue(notice._closed)
        self.assertIsNone(notice._after_id)
        self.assertIsNone(notice._startup_id)
        self.assertFalse(self.errors)

    def test_browser_button_revalidates_url_and_closes_only_on_success(self):
        notice = self.notifier(UpdateResult("available", RELEASE))
        notice.show_notice(RELEASE)
        with patch("update_notice.webbrowser.open", return_value=True) as browser:
            notice.open_release(RELEASE)
            browser.assert_called_once_with(RELEASE.page_url)
        self.assertFalse(notice.dialog.winfo_exists())
        bad = ReleaseInfo("0.2.0", "v0.2.0", "https://evil.example", "app.zip")
        with patch("update_notice.webbrowser.open") as browser:
            notice.show_notice(bad)
            notice.open_release(bad)
            browser.assert_not_called()


if __name__ == "__main__":
    unittest.main()
