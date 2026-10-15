"""Transactional spreadsheet modal shared by add and batch edit."""
import tkinter as tk
from tkinter import ttk
from accessibility import expose_buttons
from spreadsheet import SpreadsheetGrid, display_scale
from spreadsheet_data import normalize_row, normalize_rows


def center(dialog, parent):
    dialog.update_idletasks()
    width = min(dialog.winfo_reqwidth(), dialog.winfo_screenwidth() - 40)
    height = min(dialog.winfo_reqheight(), dialog.winfo_screenheight() - 80)
    x = max(0, min(parent.winfo_x() + (parent.winfo_width() - width) // 2, dialog.winfo_screenwidth() - width))
    y = max(0, min(parent.winfo_y() + (parent.winfo_height() - height) // 2, dialog.winfo_screenheight() - height - 50))
    dialog.geometry(f"{width}x{height}+{x}+{y}")


class LabelEditor(tk.Toplevel):
    def __init__(self, parent, *, rows=None, origin="직접 입력", max_rows=None, on_apply, on_close):
        super().__init__(parent)
        self.withdraw()
        self.title("라벨 추가" if rows is None else f"라벨 편집 ({len(rows)}개)")
        self.transient(parent)
        scale = self.display_scale = display_scale(self)
        self.compact = False
        self.minsize(min(round(480 * scale), self.winfo_screenwidth() - 40),
                     min(round(360 * scale), self.winfo_screenheight() - 80))
        self.on_apply, self.on_close = on_apply, on_close
        self.max_rows = max_rows
        self._notified = False
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        ttk.Label(self, text="1행 = 1라벨, A/B/C열 = 라벨의 1/2/3줄. 중간 빈 셀은 빈 줄입니다.",
                  wraplength=600).grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        toolbar = ttk.Frame(self)
        toolbar.grid(row=1, column=0, sticky="ew", padx=12, pady=4)
        self.error = ttk.Label(self, text="", foreground="#a01818", wraplength=600)
        self.preview = ttk.Label(self, text="", wraplength=600, justify="left")
        self.grid = SpreadsheetGrid(self, rows=rows or (), row_limit=max_rows,
                                    on_change=self.refresh_preview, on_error=lambda text: self.error.configure(text=text))
        self.grid.grid(row=2, column=0, sticky="nsew", padx=12)
        for number, (title, command) in enumerate([("복사", self.grid.copy), ("붙여넣기", self.grid.paste),
                               ("내용 비우기", self.grid.clear), ("되돌리기", self.grid.history),
                               ("다시 실행", lambda: self.grid.history(redo=True))]):
            ttk.Button(toolbar, text=title, command=command, width=10).grid(row=number // 3, column=number % 3, sticky="ew", padx=1, pady=1)
        for column in range(3):
            toolbar.columnconfigure(column, weight=1)
        if max_rows is None:
            ttk.Button(toolbar, text="행 삭제", command=self.grid.delete_rows, width=9).grid(row=1, column=2, sticky="ew", padx=1, pady=1)
        self.preview.grid(row=3, column=0, sticky="ew", padx=12, pady=5)
        self.origin_label = ttk.Label(self, text=origin, wraplength=600)
        self.origin_label.grid(row=4, column=0, sticky="ew", padx=12)
        self.clipboard_hint = ttk.Label(self, text="Excel 대상 셀은 텍스트 형식으로 지정하세요. 수식은 계산하지 않습니다.", wraplength=600)
        self.clipboard_hint.grid(row=5, column=0, sticky="ew", padx=12, pady=3)
        self.error.grid(row=6, column=0, sticky="ew", padx=12)
        buttons = ttk.Frame(self)
        buttons.grid(row=7, column=0, sticky="ew", padx=12, pady=10)
        self.apply_button = ttk.Button(buttons, text="적용", command=self.apply)
        self.apply_button.pack(side="right")
        ttk.Button(buttons, text="취소", command=self.destroy).pack(side="right", padx=5)
        ttk.Label(buttons, text="F2 셀 편집, Ctrl+Enter 적용, Esc 취소").pack(side="left")
        expose_buttons(self)
        self.bind("<Control-Return>", lambda event: self.apply())
        for widget in (self.grid.canvas, self.grid.entry):
            widget.bind("<Control-Return>", lambda event: self.apply())
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Destroy>", self._destroyed, add="+")
        self.bind("<Configure>", self.resize_wrap, add="+")
        self.refresh_preview()
        center(self, parent)
        self.deiconify()
        self.grab_set()
        self.grid.canvas.focus_set()

    def resize_wrap(self, event):
        if event.widget is self:
            for child in self.winfo_children():
                if isinstance(child, ttk.Label):
                    child.configure(wraplength=max(200, event.width - 24))
            compact = event.height < round(480 * self.display_scale)
            if compact != self.compact:
                self.compact = compact
                if compact:
                    self.origin_label.grid_remove()
                else:
                    self.origin_label.grid()
                self.clipboard_hint.configure(text="Excel 대상 셀은 텍스트 형식으로 지정하세요." if compact else
                                               "Excel 대상 셀은 텍스트 형식으로 지정하세요. 수식은 계산하지 않습니다.")
                self.refresh_preview()

    def refresh_preview(self):
        index = self.grid.active[0]
        row = self.grid.model.rows[index] if index < len(self.grid.model.rows) else ()
        cells = normalize_row(row)
        # A bounded textual line preview retains cell numbers and blank positions.
        lines = [f"{number + 1}줄: {value[:100] or '(빈 줄)'}{'…' if len(value) > 100 else ''}" for number, value in enumerate(cells[:4])]
        suffix = f" / 전체 {len(cells):,}줄" if len(cells) > 4 else ""
        if self.compact:
            detail = " / ".join(f"{n + 1}: {value[:18] or '(빈 줄)'}{'…' if len(value) > 18 else ''}" for n, value in enumerate(cells[:3]))
            self.preview.configure(text=f"선택 행 {index + 1}: {len(cells)}줄 라벨\n{detail or '한 칸 이상 문자를 입력하세요.'}")
        else:
            self.preview.configure(text=f"선택 행 {index + 1}: {len(cells)}줄 라벨{suffix}\n" + ("\n".join(lines) if cells else "빈 행은 추가하지 않습니다. 편집 행은 한 칸 이상 입력하세요."))

    def apply(self):
        if not self.grid.commit_edit():
            return "break"
        try:
            rows = self.grid.model.rows
            if self.max_rows is not None:
                for index, row in enumerate(rows):
                    if not normalize_row(row):
                        raise ValueError(f"{index + 1}행이 비어 있습니다. 편집 라벨에는 한 칸 이상 입력해 주세요. 취소하면 원래 값이 유지됩니다.")
            rows = normalize_rows(rows)
            if not rows:
                raise ValueError("한 행 이상 문자를 입력해 주세요.")
            self.on_apply(rows)
        except ValueError as error:
            self.error.configure(text=str(error))
            self.grid.canvas.focus_set()
            return "break"
        self.destroy()
        return "break"

    def _destroyed(self, event):
        if event.widget is self and not self._notified:
            self._notified = True
            self.on_close()
