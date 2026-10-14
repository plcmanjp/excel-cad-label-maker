"""Windows label UI. Original developer: 직장인. Continuing developer: plcmanjp."""
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from tkinterdnd2 import COPY, DND_FILES, REFUSE_DROP, TkinterDnD
from converter import (CAD_COLORS, CAD_FONTS, LabelSettings, create_drawing,
                       extract_blocks_auto, save_drawing, select_dropped_file,
                       validate_excel_path)

APP_TITLE = "Excel CAD Label Maker (개발 빌드)"


class App:
    def __init__(self, root):
        self.root = root
        root.title(APP_TITLE)
        root.minsize(620, 650)
        self.excel_path = tk.StringVar()
        self.status = tk.StringVar(value="Excel 파일을 놓거나 파일 찾기를 눌러 시작하세요.")
        self.auto_fit = tk.BooleanVar(value=True)
        self.entries = {}
        self.create_widgets()
        self.register_drop_targets(root)

    def create_widgets(self):
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="Excel 파일로 덕트 라벨 만들기",
                  font=("맑은 고딕", 15, "bold")).pack(anchor="w")
        ttk.Label(outer, text="각 열을 위에서 아래로 읽고, 빈 셀마다 새 라벨을 만듭니다.").pack(anchor="w", pady=(4, 12))
        file_frame = ttk.LabelFrame(outer, text="1. Excel 파일", padding=10)
        file_frame.pack(fill="x")
        self.drop_area = tk.Label(file_frame, text="Excel 파일을 여기에 드래그 앤 드롭하세요\n.xlsx 및 .xls 파일 한 개",
                                  bg="#eef4fc", fg="#234b7c", relief="solid", bd=1,
                                  pady=18, font=("맑은 고딕", 11))
        self.drop_area.pack(fill="x", pady=(0, 8))
        path_row = ttk.Frame(file_frame)
        path_row.pack(fill="x")
        ttk.Entry(path_row, textvariable=self.excel_path, state="readonly").pack(side="left", fill="x", expand=True)
        ttk.Button(path_row, text="파일 찾기", command=self.on_browse).pack(side="left", padx=(8, 0))
        ttk.Button(path_row, text="선택 해제", command=self.clear_file).pack(side="left", padx=(4, 0))
        ttk.Label(file_frame, textvariable=self.status, wraplength=560).pack(anchor="w", pady=(8, 0))
        options = ttk.LabelFrame(outer, text="2. 라벨 규격 (mm)", padding=10)
        options.pack(fill="x", pady=10)
        fields = [("한 행의 라벨 수", "cols_per_row", "5"), ("글자 크기 비율", "text_scale", "0.45"),
                  ("한 칸 가로폭", "cell_w", "60"), ("한 칸 높이", "cell_h", "15"),
                  ("라벨 간 가로 간격", "gap_x", "20"), ("라벨 간 세로 간격", "gap_y", "20")]
        for index, (label, key, default) in enumerate(fields):
            row, column = divmod(index, 2)
            ttk.Label(options, text=label).grid(row=row, column=column * 2, sticky="w", pady=5)
            entry = ttk.Entry(options, width=12)
            entry.insert(0, default)
            entry.grid(row=row, column=column * 2 + 1, sticky="w", padx=(8, 20), pady=5)
            self.entries[key] = entry
        ttk.Checkbutton(options, text="긴 글자를 폭에 맞게 자동 축소 및 압축",
                         variable=self.auto_fit).grid(row=3, column=0, columnspan=4, sticky="w", pady=5)
        style = ttk.LabelFrame(outer, text="3. 글꼴과 색상", padding=10)
        style.pack(fill="x")
        self.combos = {}
        for row, (label, key, values, index) in enumerate([
            ("글꼴", "font_key", list(CAD_FONTS), 0),
            ("테두리 색상", "box_color", list(CAD_COLORS), 4),
            ("문자 색상", "text_color", list(CAD_COLORS), 2),
        ]):
            ttk.Label(style, text=label).grid(row=row, column=0, sticky="w", pady=4)
            combo = ttk.Combobox(style, values=values, state="readonly", width=32)
            combo.current(index)
            combo.grid(row=row, column=1, sticky="w", padx=12, pady=4)
            self.combos[key] = combo
        self.run_button = ttk.Button(outer, text="DXF 도면 생성 및 저장", command=self.on_generate, state="disabled")
        self.run_button.pack(fill="x", pady=14, ipady=8)
        ttk.Label(outer, text="원개발자 직장인 | Fork 및 후속 개발 plcmanjp").pack(anchor="w")

    def register_drop_targets(self, widget):
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind("<<Drop>>", self.on_drop)
        widget.dnd_bind("<<DropEnter>>", self.on_drop_enter)
        widget.dnd_bind("<<DropLeave>>", self.on_drop_leave)
        for child in widget.winfo_children():
            self.register_drop_targets(child)

    def on_drop_enter(self, event):
        self.drop_area.configure(bg="#dceafa")
        return COPY

    def on_drop_leave(self, event):
        self.drop_area.configure(bg="#eef4fc")
        return COPY

    def select_file(self, value):
        path = validate_excel_path(value)
        self.excel_path.set(str(path))
        self.drop_area.configure(text=f"선택한 파일: {path.name}\n다른 Excel 파일을 놓으면 변경됩니다.")
        self.status.set("파일 선택 완료. 규격을 확인한 뒤 DXF 도면을 저장하세요.")
        self.run_button.configure(state="normal")

    def on_drop(self, event):
        self.on_drop_leave(event)
        try:
            self.select_file(select_dropped_file(self.root.tk, event.data))
        except (ValueError, tk.TclError) as error:
            self.status.set(str(error))
            return REFUSE_DROP
        return COPY

    def on_browse(self):
        value = filedialog.askopenfilename(parent=self.root, title="Excel 파일 선택",
                                           filetypes=[("Excel 파일", "*.xlsx *.xls")])
        if value:
            try:
                self.select_file(value)
            except ValueError as error:
                self.status.set(str(error))

    def clear_file(self):
        self.excel_path.set("")
        self.drop_area.configure(text="Excel 파일을 여기에 드래그 앤 드롭하세요\n.xlsx 및 .xls 파일 한 개")
        self.status.set("Excel 파일을 놓거나 파일 찾기를 눌러 시작하세요.")
        self.run_button.configure(state="disabled")

    def on_generate(self):
        try:
            values = {key: int(entry.get()) if key == "cols_per_row" else float(entry.get())
                      for key, entry in self.entries.items()}
            settings = LabelSettings(**values, auto_fit=self.auto_fit.get(),
                                      font_key=self.combos["font_key"].get(),
                                      box_color=CAD_COLORS[self.combos["box_color"].get()],
                                      text_color=CAD_COLORS[self.combos["text_color"].get()])
            blocks = extract_blocks_auto(self.excel_path.get())
            if not blocks:
                self.status.set("Excel 파일에 라벨로 만들 데이터가 없습니다.")
                return
            doc = create_drawing(blocks, settings)
            output = filedialog.asksaveasfilename(parent=self.root, title="DXF 도면 저장",
                                                  initialfile=Path(self.excel_path.get()).stem + ".dxf",
                                                  defaultextension=".dxf", filetypes=[("DXF 도면", "*.dxf")])
            if not output:
                return
            save_drawing(doc, output)
            self.status.set(f"총 {len(blocks)}개 라벨 저장 완료: {Path(output).name}")
            messagebox.showinfo("저장 완료", f"총 {len(blocks)}개 라벨을 저장했습니다.\n{output}", parent=self.root)
        except Exception as error:
            self.status.set("도면을 생성하지 못했습니다. 파일과 규격을 확인해 주세요.")
            messagebox.showerror("도면 생성 오류", str(error), parent=self.root)


def main():
    root = TkinterDnD.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
