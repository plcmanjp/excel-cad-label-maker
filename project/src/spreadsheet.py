"""Virtualized Tk spreadsheet: only visible cells and one native Entry exist."""
import tkinter as tk
from tkinter import ttk, font

from accessibility import caption
from spreadsheet_data import (GridModel, MAX_CELLS, column_name, normalize_rows,
                              parse_tsv, serialize_tsv, validate_cell)


def display_scale(widget):
    """Convert Tk pixels-per-point to a factor relative to Windows 96 DPI."""
    return max(1.0, float(widget.tk.call("tk", "scaling")) * .75)


class SpreadsheetGrid(ttk.Frame):
    def __init__(self, parent, *, rows=(), row_limit=None, on_change=None, on_error=None):
        super().__init__(parent)
        self.model = GridModel(rows, row_limit)
        self.on_change = on_change or (lambda: None)
        self.on_error = on_error or (lambda message: None)
        self.anchor = self.active = (0, 0)
        self.row_offset = self.col_offset = 0
        self.editing = False
        self.cell_font = font.Font(self, family="맑은 고딕", size=10)
        self.cell_h = max(28, self.cell_font.metrics("linespace") + 12)
        self.cell_w = max(130, self.cell_font.measure("가나다라마바사아") + 20)
        self.header_h, self.header_w = self.cell_h, max(54, self.cell_font.measure("250000") + 12)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        scale = display_scale(self)
        self.canvas = tk.Canvas(self, background="white", highlightthickness=1,
                                highlightbackground="#7d91aa", takefocus=True, width=round(640 * scale), height=round(270 * scale))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.yscroll = ttk.Scrollbar(self, command=lambda *args: self.scroll("row", *args))
        self.yscroll.grid(row=0, column=1, sticky="ns")
        self.xscroll = ttk.Scrollbar(self, orient="horizontal", command=lambda *args: self.scroll("col", *args))
        self.xscroll.grid(row=1, column=0, sticky="ew")
        self.entry = ttk.Entry(self.canvas, font=self.cell_font)
        caption(self.canvas, "라벨 스프레드시트")
        caption(self.entry, "선택 셀 편집")
        self.canvas.bind("<Configure>", self.resized)
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<Double-1>", lambda event: self.begin_edit())
        self.canvas.bind("<KeyPress>", self.type_key)
        self.canvas.bind("<MouseWheel>", self.wheel)
        self.canvas.bind("<Shift-MouseWheel>", lambda event: self.wheel(event, horizontal=True))
        for name, delta in {"Left": (0, -1), "Right": (0, 1), "Up": (-1, 0), "Down": (1, 0),
                            "Tab": (0, 1), "Return": (1, 0)}.items():
            self.canvas.bind(f"<{name}>", lambda event, delta=delta: self.move(*delta))
            self.canvas.bind(f"<Shift-{name}>", lambda event, delta=delta, name=name:
                             self.move(*((-delta[0], -delta[1]) if name in {"Tab", "Return"} else delta), extend=name not in {"Tab", "Return"}))
        self.canvas.bind("<Home>", lambda event: self.select(self.active[0], 0))
        self.canvas.bind("<End>", lambda event: self.select(self.active[0], self.model.shape[1] - 1))
        self.canvas.bind("<Control-Home>", lambda event: self.select(0, 0))
        self.canvas.bind("<Control-End>", lambda event: self.select(self.model.shape[0] - 1, self.model.shape[1] - 1))
        self.canvas.bind("<F2>", lambda event: self.begin_edit())
        self.canvas.bind("<Delete>", lambda event: self.clear())
        self.canvas.bind("<BackSpace>", lambda event: self.begin_edit(""))
        self.canvas.bind("<Control-a>", lambda event: self.select_all())
        self.canvas.bind("<Control-c>", lambda event: self.copy())
        self.canvas.bind("<Control-x>", lambda event: self.copy(cut=True))
        self.canvas.bind("<Control-v>", lambda event: self.paste())
        self.canvas.bind("<Control-z>", lambda event: self.history())
        self.canvas.bind("<Control-y>", lambda event: self.history(redo=True))
        self.entry.bind("<Return>", lambda event: self.finish_move(1, 0))
        self.entry.bind("<Tab>", lambda event: self.finish_move(0, 1))
        self.entry.bind("<Shift-Return>", lambda event: self.finish_move(-1, 0))
        self.entry.bind("<Shift-Tab>", lambda event: self.finish_move(0, -1))
        self.entry.bind("<Escape>", self.cancel_edit)
        self.entry.bind("<FocusOut>", lambda event: self.commit_edit())
        self.entry.bind("<Control-v>", lambda event: self.paste_in_entry())
        self.entry.bind("<Control-z>", lambda event: self.history())
        self.entry.bind("<Control-y>", lambda event: self.history(redo=True))
        self.redraw()

    @property
    def selection(self):
        r, c = self.anchor
        rr, cc = self.active
        return min(r, rr), min(c, cc), max(r, rr), max(c, cc)

    @property
    def extent(self):
        rows, cols = self.model.shape
        return (self.model.row_limit if self.model.row_limit is not None else min(MAX_CELLS // cols, max(20, rows + 10)),
                min(MAX_CELLS // rows, max(6, cols + 2)))

    def visible(self):
        return (max(1, (self.canvas.winfo_height() - self.header_h) // self.cell_h),
                max(1, (self.canvas.winfo_width() - self.header_w) // self.cell_w))

    def ensure_active_visible(self):
        vr, vc = self.visible()
        r, c = self.active
        self.row_offset = min(self.row_offset, r) if r < self.row_offset else max(self.row_offset, r - vr + 1)
        self.col_offset = min(self.col_offset, c) if c < self.col_offset else max(self.col_offset, c - vc + 1)

    def resized(self, event=None):
        # A growing preview or DPI/window resize must not hide the active cell.
        # Explicit scrollbar movement still permits browsing away from it.
        self.ensure_active_visible()
        self.redraw()

    def place_entry(self):
        r, c = self.active
        self.entry.place(x=self.header_w + (c - self.col_offset) * self.cell_w + 1,
                         y=self.header_h + (r - self.row_offset) * self.cell_h + 1,
                         width=self.cell_w - 2, height=self.cell_h - 2)

    def redraw(self):
        if not self.winfo_exists():
            return
        self.canvas.delete("all")
        vr, vc = self.visible()
        er, ec = self.extent
        self.row_offset = min(max(0, er - vr), self.row_offset)
        self.col_offset = min(max(0, ec - vc), self.col_offset)
        top, left, bottom, right = self.selection
        for rr in range(min(vr + 1, er - self.row_offset)):
            r = rr + self.row_offset
            y = self.header_h + rr * self.cell_h
            for cc in range(min(vc + 1, ec - self.col_offset)):
                c = cc + self.col_offset
                x = self.header_w + cc * self.cell_w
                chosen = top <= r <= bottom and left <= c <= right
                self.canvas.create_rectangle(x, y, x + self.cell_w, y + self.cell_h,
                                             fill="#deebff" if chosen else "white", outline="#d4dce6")
                text = self.model.get(r, c)
                # Rendering is bounded; the full value remains in Entry/copy/DXF.
                limit = max(4, self.cell_w // max(1, self.cell_font.measure("가")))
                display = text[:limit] + ("…" if len(text) > limit else "")
                self.canvas.create_text(x + 6, y + self.cell_h / 2, anchor="w", text=display, font=self.cell_font)
                if (r, c) == self.active:
                    self.canvas.create_rectangle(x + 1, y + 1, x + self.cell_w - 1, y + self.cell_h - 1, outline="#2162ad", width=2)
        for cc in range(min(vc + 1, ec - self.col_offset)):
            c = cc + self.col_offset
            x = self.header_w + cc * self.cell_w
            self.canvas.create_rectangle(x, 0, x + self.cell_w, self.header_h, fill="#eef3f9", outline="#c1cedd")
            self.canvas.create_text(x + self.cell_w / 2, self.header_h / 2, text=f"{column_name(c)} ({c + 1}줄)", font=self.cell_font)
        for rr in range(min(vr + 1, er - self.row_offset)):
            y = self.header_h + rr * self.cell_h
            self.canvas.create_rectangle(0, y, self.header_w, y + self.cell_h, fill="#eef3f9", outline="#c1cedd")
            self.canvas.create_text(self.header_w / 2, y + self.cell_h / 2, text=str(rr + self.row_offset + 1), font=self.cell_font)
        self.canvas.create_rectangle(0, 0, self.header_w, self.header_h, fill="#eef3f9", outline="#c1cedd")
        self.yscroll.set(self.row_offset / er, min(1, (self.row_offset + vr) / er))
        self.xscroll.set(self.col_offset / ec, min(1, (self.col_offset + vc) / ec))
        if self.editing:
            self.place_entry()
        caption(self.canvas, f"라벨 스프레드시트, {column_name(self.active[1])}{self.active[0] + 1}, 선택 {bottom - top + 1}행 {right - left + 1}열")

    def scroll(self, axis, action, value, units=None):
        if not self.commit_edit():
            return
        count = self.extent[0 if axis == "row" else 1]
        page = self.visible()[0 if axis == "row" else 1]
        attr = "row_offset" if axis == "row" else "col_offset"
        position = int(float(value) * count) if action == "moveto" else getattr(self, attr) + int(value) * (page if units == "pages" else 1)
        setattr(self, attr, max(0, min(position, max(0, count - page))))
        self.redraw()

    def wheel(self, event, horizontal=False):
        self.scroll("col" if horizontal else "row", "scroll", -int(event.delta / 120) * 3, "units")
        return "break"

    def hit(self, event):
        er, ec = self.extent
        return (max(0, min(er - 1, self.row_offset + (event.y - self.header_h) // self.cell_h)),
                max(0, min(ec - 1, self.col_offset + (event.x - self.header_w) // self.cell_w)))

    def click(self, event):
        if not self.commit_edit():
            return "break"
        self.canvas.focus_set()
        r, c = self.hit(event)
        if event.x < self.header_w and event.y < self.header_h:
            return self.select_all()
        if event.x < self.header_w:
            self.anchor, self.active = (r, 0), (r, self.model.shape[1] - 1)
            self.changed()
            return "break"
        if event.y < self.header_h:
            self.anchor, self.active = (0, c), (self.model.shape[0] - 1, c)
            self.changed()
            return "break"
        return self.select(r, c, extend=bool(event.state & 1))

    def drag(self, event):
        if not self.editing:
            self.select(*self.hit(event), extend=True)
        return "break"

    def select(self, row, column, extend=False):
        if not self.commit_edit():
            return "break"
        er, ec = self.extent
        self.active = (max(0, min(row, er - 1)), max(0, min(column, ec - 1)))
        if not extend:
            self.anchor = self.active
        self.ensure_active_visible()
        self.changed()
        return "break"

    def select_all(self):
        self.anchor = (0, 0)
        return self.select(self.model.shape[0] - 1, self.model.shape[1] - 1, extend=True)

    def move(self, dr, dc, extend=False):
        r, c = self.active
        # Tab follows the visible spreadsheet columns, Enter follows rows.
        return self.select(r + dr, c + dc, extend)

    def begin_edit(self, initial=None):
        if self.editing:
            return "break"
        r, c = self.active
        self.editing = True
        self.entry.delete(0, "end")
        self.entry.insert(0, self.model.get(r, c) if initial is None else initial)
        self.place_entry()
        self.entry.focus_set()
        if initial is None:
            self.entry.selection_range(0, "end")
        self.entry.icursor("end")
        return "break"

    def type_key(self, event):
        if event.char and event.char.isprintable() and not event.state & 4:
            return self.begin_edit(event.char)

    def commit_edit(self):
        if not self.editing:
            return True
        try:
            value = validate_cell(self.entry.get(), *self.active)
            self.model.paste(*self.active, ((value,),))
        except ValueError as error:
            self.on_error(str(error))
            return False
        self.editing = False
        self.entry.place_forget()
        self.changed()
        return True

    def cancel_edit(self, event=None):
        self.editing = False
        self.entry.place_forget()
        self.canvas.focus_set()
        return "break"

    def finish_move(self, dr, dc):
        if self.commit_edit():
            self.canvas.focus_set()
            self.move(dr, dc)
        return "break"

    def changed(self):
        self.redraw()
        self.on_change()

    def paste_text(self, text):
        values = parse_tsv(text)
        if not self.commit_edit():
            return False
        r, c, _, _ = self.selection
        self.model.paste(r, c, values)
        self.anchor = r, c
        self.active = r + len(values) - 1, c + len(values[0]) - 1
        self.ensure_active_visible()
        self.changed()
        self.on_error("")
        return True

    def paste(self):
        try:
            self.paste_text(self.clipboard_get())
        except (ValueError, tk.TclError) as error:
            self.on_error(str(error) if isinstance(error, ValueError) else "클립보드에서 텍스트 표를 읽을 수 없습니다.")
        return "break"

    def paste_in_entry(self):
        try:
            text = self.clipboard_get()
            values = parse_tsv(text)
            if len(values) == 1 and len(values[0]) == 1:
                if self.entry.selection_present():
                    self.entry.delete("sel.first", "sel.last")
                self.entry.insert("insert", values[0][0])
            else:
                self.paste_text(text)
                self.canvas.focus_set()
        except (ValueError, tk.TclError) as error:
            self.on_error(str(error))
        return "break"

    def copy_text(self):
        if not self.commit_edit():
            raise ValueError("셀 입력을 확인해 주세요.")
        return serialize_tsv(self.model.rectangle(*self.selection))

    def copy(self, cut=False):
        try:
            text = self.copy_text()
            self.clipboard_clear()
            # Tk converts LF to CRLF for CF_UNICODETEXT on Windows. Passing
            # serialized CRLF here produces CRCRLF and blank Excel rows.
            self.clipboard_append(text.replace("\r\n", "\n"))
            if cut:
                self.clear()
        except (ValueError, tk.TclError) as error:
            self.on_error(str(error))
        return "break"

    def clear(self):
        if self.commit_edit():
            self.model.clear(*self.selection)
            self.changed()
        return "break"

    def delete_rows(self):
        if self.commit_edit():
            try:
                top, _, bottom, _ = self.selection
                self.model.delete_rows(top, bottom)
                self.select(min(top, self.model.shape[0] - 1), 0)
            except ValueError as error:
                self.on_error(str(error))

    def history(self, redo=False):
        if self.commit_edit():
            (self.model.redo if redo else self.model.undo)()
            self.select(min(self.active[0], self.model.shape[0] - 1), min(self.active[1], self.model.shape[1] - 1))
        return "break"
