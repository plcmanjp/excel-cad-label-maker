"""Keep network work off Tk; show notices only from the main event loop."""
from queue import Empty, Queue
from contextlib import contextmanager
import threading
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser

from app_version import APP_VERSION
from update_check import UpdateResult, check_for_update, release_page_url
from accessibility import caption


class UpdateNotifier:
    def __init__(self, root, parent, *, current_version=APP_VERSION, checker=check_for_update, auto_check=True, modal_scope=None):
        self.root, self.current_version, self.checker = root, current_version, checker
        self.status = tk.StringVar(value=f"앱 버전 {current_version}")
        self.frame = ttk.Frame(parent)
        self.frame.pack(side="right")
        self.available_release = None
        self.button = tk.Button(self.frame, text="업데이트 확인", command=lambda: self.check(manual=True),
                                background="#eef1f5", activebackground="#e0e5ec", relief="flat", borderwidth=1,
                                padx=10, pady=3, font=("맑은 고딕", 9))
        self.button.pack(side="right")
        self._queue = Queue()
        self._active = self._closed = False
        self._pending = None
        self._after_id = None
        self._startup_id = None
        self._defer_depth = 0
        self.modal_scope = modal_scope or self.defer_notices
        self.dialog = None
        root.bind("<Destroy>", self._on_destroy, add="+")
        if auto_check:
            self._startup_id = root.after(700, self.check)

    def _on_destroy(self, event):
        if event.widget is self.root:
            self._closed = True
            for identifier in (self._after_id, self._startup_id):
                if identifier is not None:
                    self.root.after_cancel(identifier)
            self._after_id = self._startup_id = None

    @contextmanager
    def defer_notices(self):
        self._defer_depth += 1
        try:
            yield
        finally:
            self._defer_depth -= 1

    def check(self, manual=False):
        if self._active or self._closed:
            return
        if manual and self.available_release is not None:
            self.show_notice(self.available_release)
            return
        if self._startup_id is not None:
            self.root.after_cancel(self._startup_id)
            self._startup_id = None
        self._active = True
        self.button.configure(state="disabled", text="확인 중...")
        caption(self.button, "업데이트 확인 중")
        self.status.set("업데이트 확인 중...")
        # The worker never touches a Tk object, even when the window has closed.
        threading.Thread(target=self._worker, args=(manual,), daemon=True).start()
        self._after_id = self.root.after(100, self._poll)

    def _worker(self, manual):
        try:
            result = self.checker(self.current_version)
        except Exception:
            result = UpdateResult("unavailable", reason="checker-error")
        self._queue.put((manual, result))

    def _poll(self):
        self._after_id = None
        if self._closed:
            return
        if self._pending is None:
            try:
                self._pending = self._queue.get_nowait()
            except Empty:
                self._after_id = self.root.after(100, self._poll)
                return
        if self._defer_depth or self.root.grab_current() is not None:
            self._after_id = self.root.after(100, self._poll)
            return
        manual, result = self._pending
        self._pending = None
        self._active = False
        self.button.configure(state="normal")
        if result.status == "available" and result.release is not None and self._trusted_page(result.release):
            self.available_release = result.release
            self.status.set(f"새 버전 {result.release.version} 사용 가능")
            if manual:
                self.show_notice(result.release)
        elif result.status == "current" and result.release is not None:
            self.available_release = None
            self.status.set(f"새 정식 버전 없음 (공개 {result.release.version})")
            if manual:
                with self.modal_scope():
                    messagebox.showinfo("업데이트 확인", "설치된 앱보다 새로운 정식 버전이 없습니다.", parent=self.root)
        else:
            self.status.set("업데이트 확인 불가. 앱은 계속 사용할 수 있습니다.")
            if manual:
                with self.modal_scope():
                    messagebox.showinfo("업데이트 확인", "지금은 업데이트를 확인할 수 없습니다.\n잠시 후 다시 확인해 주세요.", parent=self.root)
        available = self.available_release is not None
        self.button.configure(text="새 버전 확인" if available else "업데이트 확인",
                              background="#dbe7ff" if available else "#eef1f5",
                              foreground="#134ba5" if available else "#222222",
                              activebackground="#c8daff" if available else "#e0e5ec")
        caption(self.button, self.button.cget("text"))

    def show_notice(self, release):
        if not self._trusted_page(release):
            return
        if self.dialog is not None and self.dialog.winfo_exists():
            self.dialog.lift()
            return
        dialog = self.dialog = tk.Toplevel(self.root)
        dialog.withdraw()
        dialog.title("새 버전 알림")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        content = ttk.Frame(dialog, padding=20)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text="새로운 정식 버전을 사용할 수 있습니다.", font=("맑은 고딕", 11, "bold")).pack(anchor="w")
        ttk.Label(content, text=f"현재 버전: {self.current_version}\n최신 버전: {release.version}").pack(anchor="w", pady=10)
        ttk.Label(content, text="GitHub 릴리스 페이지에서 변경 내역과 다운로드를 확인하세요.").pack(anchor="w")
        buttons = ttk.Frame(content)
        buttons.pack(fill="x", pady=(16, 0))
        ttk.Button(buttons, text="릴리스 페이지 열기", command=lambda: self.open_release(release)).pack(side="left")
        later = ttk.Button(buttons, text="나중에", command=dialog.destroy)
        later.pack(side="right")
        dialog.update_idletasks()
        width, height = dialog.winfo_reqwidth(), dialog.winfo_reqheight()
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        # Keep absolute positions on desktops with monitors left/above the primary.
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.deiconify()
        later.focus_set()
        dialog.bind("<Escape>", lambda event: dialog.destroy())

    def open_release(self, release):
        # Validate again at action time; never open an arbitrary URL from JSON.
        if not self._trusted_page(release):
            return
        try:
            opened = webbrowser.open(release.page_url)
        except OSError:
            opened = False
        if opened:
            if self.dialog is not None and self.dialog.winfo_exists():
                self.dialog.destroy()
        else:
            messagebox.showwarning("브라우저 열기", "릴리스 페이지를 열지 못했습니다. 기본 브라우저를 확인해 주세요.", parent=self.root)

    @staticmethod
    def _trusted_page(release):
        try:
            return release.page_url == release_page_url(release.tag)
        except (ValueError, AttributeError):
            return False
