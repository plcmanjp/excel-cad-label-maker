"""A bounded viewport consuming the same placed cells as the DXF writer."""
import tkinter as tk
import math
from tkinter import font, ttk
from collections import OrderedDict
from text_bitmap import glyph_image


class Preview(ttk.Frame):
    def __init__(self, parent, on_select):
        super().__init__(parent)
        self.on_select = on_select
        self.layout = None
        self.selected = None
        self.scale = 1.0
        self.fit_mode = True
        self.selected_fit_pending = False
        self.selected_fit_mode = False
        self.pending = None
        self.cells_by_label = {}
        self.images = OrderedDict()
        self.visible_images = []
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        tools = ttk.Frame(self)
        tools.grid(row=0, column=0, columnspan=2, sticky="ew")
        for text, command in [("전체 맞춤", self.fit), ("확대", lambda: self.zoom(1.35)), ("축소", lambda: self.zoom(1 / 1.35)), ("선택 라벨", self.show_selected)]:
            ttk.Button(tools, text=text, command=command).pack(side="left", padx=2)
        self.note = tk.StringVar(value="파일을 선택하면 도면을 미리 볼 수 있습니다.")
        self.canvas = tk.Canvas(self, background="white", highlightthickness=1, takefocus=True)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.vertical = ttk.Scrollbar(self, orient="vertical", command=self._yview)
        self.vertical.grid(row=1, column=1, sticky="ns")
        self.horizontal = ttk.Scrollbar(self, orient="horizontal", command=self._xview)
        self.horizontal.grid(row=2, column=0, sticky="ew")
        self.canvas.configure(yscrollcommand=self.vertical.set, xscrollcommand=self.horizontal.set)
        ttk.Label(self, textvariable=self.note, wraplength=560).grid(row=3, column=0, columnspan=2, sticky="ew")
        ttk.Label(self, text="글꼴 표시는 참고용입니다. 실제 CAD에서 글꼴과 문자 폭을 확인하세요.", wraplength=560).grid(row=4, column=0, columnspan=2, sticky="ew")
        self.canvas.bind("<Configure>", self.resized)
        self.canvas.bind("<Map>", self.resized)
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<MouseWheel>", self.wheel)
        self.canvas.bind("<Control-plus>", lambda event: self.zoom(1.35))
        self.canvas.bind("<Control-minus>", lambda event: self.zoom(1 / 1.35))
        self.canvas.bind("<Left>", lambda event: self._xview("scroll", -1, "units"))
        self.canvas.bind("<Right>", lambda event: self._xview("scroll", 1, "units"))
        self.canvas.bind("<Up>", lambda event: self._yview("scroll", -1, "units"))
        self.canvas.bind("<Down>", lambda event: self._yview("scroll", 1, "units"))
        self.bind("<Destroy>", self._destroy, add="+")

    def _destroy(self, event):
        if event.widget is self and self.pending:
            self.after_cancel(self.pending)
            self.pending = None

    def _xview(self, *args):
        self.canvas.xview(*args)
        self.schedule()

    def _yview(self, *args):
        self.canvas.yview(*args)
        self.schedule()

    def wheel(self, event):
        if event.state & 4:
            self.zoom(1.2 if event.delta > 0 else 1 / 1.2)
        else:
            self._yview("scroll", -int(event.delta / 120), "units")
        return "break"

    def set_layout(self, layout):
        self.layout = layout
        self.selected = None
        self.selected_fit_pending = False
        self.cells_by_label = {}
        for cell in layout.cells if layout else ():
            self.cells_by_label.setdefault(cell.label, []).append(cell)
        self.fit()

    def resized(self, event):
        if self.selected_fit_mode and self.canvas.winfo_ismapped():
            self.show_selected()
        elif self.fit_mode:
            self.fit()
        else:
            self.schedule()

    def fit(self):
        self.fit_mode = True
        self.selected_fit_pending = False
        self.selected_fit_mode = False
        if self.layout and self.layout.cells:
            x1, y1, x2, y2 = self.layout.bounds
            width, height = self.viewport()
            self.scale = max(0.002, min((width - 40) / max(x2 - x1, 1), (height - 40) / max(y2 - y1, 1)))
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.schedule()

    def zoom(self, factor):
        self.fit_mode = False
        self.selected_fit_pending = False
        self.selected_fit_mode = False
        self.scale = max(0.002, min(self.scale * factor, 100))
        self.schedule()

    def select(self, label, center=False):
        self.selected = label
        if center:
            self.show_selected()
        else:
            self.schedule()

    def show_selected(self):
        if self.layout and self.selected is not None and self.selected < len(self.layout.label_bounds):
            self.selected_fit_mode = True
            self.fit_mode = False
            if not self.canvas.winfo_ismapped():
                self.selected_fit_pending = True
                self.schedule()
                return
            self.selected_fit_pending = False
            x1, y1, x2, y2 = self.layout.label_bounds[self.selected]
            width, height = self.viewport()
            self.scale = max(0.002, min((width - 60) / max(x2 - x1, 1), (height - 60) / max(y2 - y1, 1), 15))
            self.draw()
            total_width = self.layout.bounds[2] * self.scale + 40
            total_height = -self.layout.bounds[1] * self.scale + 40
            self.canvas.xview_moveto(max(0, (x1 * self.scale - 10) / max(total_width, 1)))
            self.canvas.yview_moveto(max(0, (-y2 * self.scale - 10) / max(total_height, 1)))
            self.schedule()

    def viewport(self):
        if not self.canvas.winfo_ismapped():
            return 300, 200
        return max(self.canvas.winfo_width(), 61), max(self.canvas.winfo_height(), 61)

    def schedule(self):
        if self.pending:
            self.after_cancel(self.pending)
        self.pending = self.after(35, self.draw)

    def point(self, x, y):
        return 20 + x * self.scale, 20 - y * self.scale

    def draw(self):
        if self.pending:
            self.after_cancel(self.pending)
        self.pending = None
        self.canvas.delete("all")
        if not self.layout or not self.layout.cells:
            self.canvas.create_text(20, 20, anchor="nw", text="라벨 없음", fill="#555555")
            return
        self.canvas.configure(scrollregion=(0, 0, self.layout.bounds[2] * self.scale + 40, -self.layout.bounds[1] * self.scale + 40))
        vx, vy = self.canvas.canvasx(0), self.canvas.canvasy(0)
        vw, vh = self.canvas.winfo_width(), self.canvas.winfo_height()
        visible = []
        for index, (x1, y1, x2, y2) in enumerate(self.layout.label_bounds):
            left, top = self.point(x1, y2)
            right, bottom = self.point(x2, y1)
            if right >= vx and left <= vx + vw and bottom >= vy and top <= vy + vh:
                visible.append(index)
        # Whole-fit views may contain thousands of tiny labels. Keep Tk work bounded.
        shown = visible[:200]
        if self.selected in visible and self.selected not in shown:
            shown[-1] = self.selected
        colors = {1: "#c62020", 2: "#8c7500", 3: "#148029", 4: "#007a9e", 5: "#225ac6", 6: "#a029a0", 7: "#222222"}
        family = self.layout.settings.font_key.split(" (")[0]
        if family == "AutoCAD 표준":
            family = "Arial"
        self.visible_images = []
        fallback = False
        cell_count = 0
        coarse = False
        for index in shown:
            if self.layout.settings.cell_h * self.scale < 2:
                x1, y1, x2, y2 = self.layout.label_bounds[index]
                self.canvas.create_rectangle(*self.point(x1, y2), *self.point(x2, y1), outline=colors[self.layout.settings.box_color], tags=(f"label-{index}",))
                coarse = True
                continue
            all_cells = self.cells_by_label[index]
            _, label_top = self.point(*all_cells[0].corners[0])
            cell_pixels = self.layout.settings.cell_h * self.scale
            start = max(0, int((vy - label_top) // cell_pixels) - 1)
            end = min(len(all_cells), math.ceil((vy + vh - label_top) / cell_pixels) + 1)
            for cell in all_cells[start:end]:
                left, top = self.point(*cell.corners[0])
                right, bottom = self.point(*cell.corners[2])
                if right < vx or left > vx + vw or bottom < vy or top > vy + vh:
                    continue
                if cell_count >= 1200:
                    coarse = True
                    break
                cell_count += 1
                tags = (f"label-{index}",)
                self.canvas.create_rectangle(left, top, right, bottom, outline=colors[self.layout.settings.box_color],
                                             width=2 if index == self.selected else 1, tags=tags)
                if cell.text_height * self.scale >= 4:
                    pixels = max(4, round(cell.text_height * self.scale))
                    color = colors[self.layout.settings.text_color]
                    key = (cell.text, family, pixels, cell.width_factor, color)
                    if key not in self.images:
                        try:
                            self.images[key] = glyph_image(self.canvas, *key)
                        except (OSError, AttributeError, tk.TclError):
                            self.images[key] = None
                        if len(self.images) > 128:
                            self.images.popitem(last=False)
                    bitmap = self.images.get(key)
                    if bitmap:
                        self.visible_images.append(bitmap)
                        self.canvas.create_image(*self.point(*cell.center), image=bitmap, tags=tags)
                    else:
                        fallback = True
                        display_font = font.Font(self.canvas, family=family, size=-pixels)
                        self.canvas.create_text(*self.point(*cell.center), text=cell.text, font=display_font, fill=color, tags=tags)
        width, height = self.layout.bounds[2], -self.layout.bounds[1]
        suffix = f" (현재 영역 {len(visible):,}개 중 {len(shown):,}개 표시, 확대해서 확인)" if len(visible) > 200 else ""
        if fallback:
            suffix += " (일부 문자는 가로 압축을 생략한 참고 표시)"
        if coarse:
            suffix += " (작은 칸은 라벨 윤곽으로 표시, 상세는 확대 및 전체 문자 보기)"
        self.note.set(f"전체 배치 {width:g} × {height:g} mm, 확대 {self.scale:.2f} px/mm{suffix}")

    def click(self, event):
        items = self.canvas.find_overlapping(self.canvas.canvasx(event.x) - 2, self.canvas.canvasy(event.y) - 2,
                                             self.canvas.canvasx(event.x) + 2, self.canvas.canvasy(event.y) + 2)
        for item in reversed(items):
            for tag in self.canvas.gettags(item):
                if tag.startswith("label-"):
                    self.on_select(int(tag[6:]))
                    return
