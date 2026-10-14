"""One modal for adding and editing a complete output label."""
import tkinter as tk
from tkinter import ttk
from accessibility import caption, expose_buttons


def center(dialog, parent):
    dialog.update_idletasks()
    width, height = dialog.winfo_reqwidth(), dialog.winfo_reqheight()
    x = parent.winfo_x() + (parent.winfo_width() - width) // 2
    y = parent.winfo_y() + (parent.winfo_height() - height) // 2
    dialog.geometry(f"{width}x{height}+{x}+{y}")


class LabelEditor(tk.Toplevel):
    def __init__(self, parent, *, texts=None, origin="직접 입력", on_apply, on_close):
        super().__init__(parent)
        self.withdraw()
        self.title("라벨 추가" if texts is None else "라벨 편집")
        self.transient(parent)
        self.minsize(480, 300)
        self.on_apply, self.on_close = on_apply, on_close
        self._notified = False
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        ttk.Label(self, text="한 줄이 도면의 한 칸입니다. 원본 Excel은 변경하지 않습니다.").grid(row=0, column=0, columnspan=2, sticky="w", padx=14, pady=(12, 6))
        self.text = tk.Text(self, width=72, height=14, wrap="none", undo=True, font=("맑은 고딕", 10))
        self.text.grid(row=1, column=0, sticky="nsew", padx=(14, 0))
        scroll = ttk.Scrollbar(self, command=self.text.yview)
        scroll.grid(row=1, column=1, sticky="ns", padx=(0, 14))
        self.text.configure(yscrollcommand=scroll.set)
        horizontal = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        horizontal.grid(row=2, column=0, sticky="ew", padx=(14, 0))
        self.text.configure(xscrollcommand=horizontal.set)
        ttk.Label(self, text=origin, wraplength=600).grid(row=3, column=0, columnspan=2, sticky="ew", padx=14, pady=5)
        self.error = ttk.Label(self, text="", foreground="#a01818", wraplength=600)
        self.error.grid(row=4, column=0, columnspan=2, sticky="ew", padx=14)
        buttons = ttk.Frame(self)
        buttons.grid(row=5, column=0, columnspan=2, sticky="ew", padx=14, pady=12)
        self.apply_button = ttk.Button(buttons, text="적용", command=self.apply)
        self.apply_button.pack(side="right")
        ttk.Button(buttons, text="취소", command=self.destroy).pack(side="right", padx=5)
        ttk.Label(buttons, text="Ctrl+Enter 적용, Esc 취소").pack(side="left")
        if texts:
            self.text.insert("1.0", "\n".join(texts))
        caption(self.text, "라벨 문자 입력")
        expose_buttons(self)
        self.bind("<Control-Return>", lambda event: self.apply())
        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Destroy>", self._destroyed, add="+")
        center(self, parent)
        self.deiconify()
        self.grab_set()
        self.text.focus_set()

    def apply(self):
        try:
            self.on_apply(self.text.get("1.0", "end-1c"))
        except ValueError as error:
            self.error.configure(text=str(error))
            self.text.focus_set()
            return "break"
        self.destroy()
        return "break"

    def _destroyed(self, event):
        if event.widget is self and not self._notified:
            self._notified = True
            self.on_close()
