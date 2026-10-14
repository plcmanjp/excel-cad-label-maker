"""Quick Excel -> review -> DXF workflow. Credits: 직장인 and plcmanjp."""
from dataclasses import asdict
from contextlib import contextmanager
import os
from pathlib import Path
from queue import Empty
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from app_version import APP_VERSION
from converter import CAD_COLORS, CAD_FONTS, LabelSettings, compute_layout, drawing_from_layout, save_drawing, select_dropped_file, validate_excel_path
from input_model import Diagnostic, InputOptions, analyze, read_workbook
from jobs import Jobs
from preview import Preview
from settings_store import SettingsError, SettingsStore, defaults
from tkinterdnd2 import COPY, DND_FILES, REFUSE_DROP
from update_check import check_for_update
from update_notice import UpdateNotifier
from accessibility import caption, expose_buttons
from input_model import Analysis
from working_data import apply_edits, edited_label, parse_label_text
from label_editor import LabelEditor, center

APP_TITLE = f"Excel CAD Label Maker {APP_VERSION}"
PAGE_SIZE = 100


class App:
    def __init__(self, root, *, current_version=APP_VERSION, update_checker=check_for_update, check_updates=True, settings_dir=None):
        self.root = root
        root.title(APP_TITLE)
        root.iconbitmap(default=str(Path(__file__).resolve().parent / "assets" / "app-icon.ico"))
        root.geometry("1120x760")
        root.minsize(640, 420)
        self.store = SettingsStore(settings_dir)
        self.jobs = Jobs()
        self.snapshot = self.analysis = self.layout = None
        self.base_analysis = None
        self.replacements = {}
        self.additions = []
        self.edit_revision = self.saved_edit_revision = 0
        self.rendered_edit_revision = 0
        self.editor = self.popup_scope = None
        self.pending_edit_reset = False
        self.last_settings = None
        self.diagnostics = ()
        self.busy = self.saving = self.closed = self.confirmed = False
        self.source_changed = False
        self.after_id = self.debounce_id = None
        self.idle_ids = set()
        self.notice_scope = None
        self.modal_open = False
        self.selected = None
        self.page = 0
        self.diag_page = 0
        self.diag_filter = tk.StringVar(value="전체")
        self.output = None
        self.pending_read = None
        self._loading = True
        self._narrow = self._show_settings = False
        self.excel_path = tk.StringVar()
        self.status = tk.StringVar(value="Excel을 불러오거나 행 추가로 시작하세요.")
        self.save_reason = tk.StringVar(value="Excel을 불러오거나 행을 추가해 주세요.")
        self.summary = tk.StringVar(value="라벨 0개, 총 0칸")
        self.selection_info = tk.StringVar(value="라벨을 선택하면 크기와 원본 셀을 확인할 수 있습니다.")
        self.form_error = tk.StringVar()
        self.preset_state = tk.StringVar()
        self.preset = tk.StringVar(value="마지막 설정")
        self.sheet = tk.StringVar()
        self.cell_range = tk.StringVar()
        self.skip_header = tk.BooleanVar(value=False)
        self.mode = tk.StringVar(value="기존 해석")
        self.auto_fit = tk.BooleanVar(value=True)
        self.advanced_open = tk.BooleanVar(value=False)
        self.vars, self.entries, self.combos = {}, {}, {}
        self.create_widgets()
        self.excel_path.trace_add("write", self.show_filename)
        self.updates = UpdateNotifier(root, self.update_frame, current_version=current_version, checker=update_checker, auto_check=check_updates, modal_scope=self.dialog_scope)
        self.apply_values(self.store.last)
        self._loading = False
        self.register_drop_targets(root)
        for variable in [*self.vars.values(), self.auto_fit, self.mode, self.cell_range, self.skip_header]:
            variable.trace_add("write", self.settings_changed)
        root.bind("<Control-o>", lambda event: self._shortcut(self.on_browse))
        root.bind("<Control-s>", lambda event: self._shortcut(self.on_generate))
        root.bind("<Control-Tab>", lambda event: self.switch_tab(1))
        root.bind("<Control-Shift-Tab>", lambda event: self.switch_tab(-1))
        root.bind("<Configure>", self._resize, add="+")
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.bind("<Destroy>", self._destroyed, add="+")
        self.after_id = root.after(40, self.poll)
        if self.store.warning:
            self.status.set(self.store.warning)
        self._layout_panels()
        self._update_preset_state()
        self.render_diagnostics()
        self.render_list()
        root.update_idletasks()
        expose_buttons(root)
        field_names = {"cell_w": "한 칸 가로폭", "cell_h": "한 칸 높이", "cols_per_row": "한 행의 라벨 수", "gap_x": "가로 간격", "gap_y": "세로 간격", "text_height": "기본 글자 높이", "min_text_height": "최소 글자 높이 경고"}
        for key, entry in self.entries.items():
            caption(entry, field_names[key])
        caption(self.sheet_combo, "시트 선택")
        caption(self.range_entry, "셀 범위")
        caption(self.data_tree, "출력 데이터")
        caption(self.diag_tree, "확인할 사항")
        caption(self.preview.canvas, "도면")
        self.status.trace_add("write", lambda *args: caption(self.status_label, self.status.get()))
        self.summary.trace_add("write", lambda *args: caption(self.summary_label, self.summary.get()))
        self.schedule_idle(self.browse_button.focus_set)

    def _shortcut(self, command):
        if not self.modal_open:
            command()
        return "break"

    @contextmanager
    def dialog_scope(self):
        self.modal_open = True
        try:
            with self.updates.defer_notices():
                yield
        finally:
            self.modal_open = False

    def create_widgets(self):
        outer = self.outer = ttk.Frame(self.root, padding=8)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(2, weight=1)
        header = ttk.Frame(outer)
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="덕트 라벨 만들기", font=("맑은 고딕", 13, "bold")).pack(side="left")
        self.update_frame = ttk.Frame(header)
        self.update_frame.pack(side="right")
        ttk.Button(header, text="? 도움말", command=self.show_help).pack(side="right", padx=5)
        self.settings_button = ttk.Button(header, text="설정 보기", command=self.toggle_settings)
        self.settings_button.pack(side="right", padx=5)
        file_frame = ttk.Frame(outer)
        file_frame.grid(row=1, column=0, sticky="ew", pady=5)
        file_frame.columnconfigure(0, weight=1)
        self.drop_area = tk.Label(file_frame, text="Excel 파일을 놓거나 행 추가로 시작하세요", background="#eef4fc", foreground="#234b7c", pady=6)
        self.drop_area.grid(row=0, column=0, columnspan=4, sticky="ew")
        self.filename = tk.StringVar(value="선택한 Excel 없음")
        ttk.Label(file_frame, textvariable=self.filename).grid(row=1, column=0, sticky="ew")
        self.browse_button = ttk.Button(file_frame, text="파일 찾기", command=self.on_browse)
        self.browse_button.grid(row=1, column=1, padx=3)
        ttk.Button(file_frame, text="다시 읽기", command=self.reload).grid(row=1, column=2, padx=3)
        ttk.Button(file_frame, text="새 작업", command=self.clear_file).grid(row=1, column=3)
        ttk.Button(file_frame, text="예제", command=self.make_example).grid(row=1, column=4, padx=(3, 0))
        self.body = ttk.Frame(outer)
        self.body.grid(row=2, column=0, sticky="nsew")
        self.body.columnconfigure(1, weight=1)
        self.body.rowconfigure(0, weight=1)
        self.settings_frame = ttk.Frame(self.body)
        self.settings_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.settings_frame.rowconfigure(0, weight=1)
        self.settings_canvas = tk.Canvas(self.settings_frame, width=305, highlightthickness=0)
        self.settings_canvas.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(self.settings_frame, orient="vertical", command=self.settings_canvas.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.settings_canvas.configure(yscrollcommand=scroll.set)
        self.form = ttk.Frame(self.settings_canvas, padding=4)
        self.settings_canvas.create_window(0, 0, window=self.form, anchor="nw", tags="form")
        self.form.bind("<Configure>", lambda event: self.settings_canvas.configure(scrollregion=self.settings_canvas.bbox("all")))
        self.settings_canvas.bind("<MouseWheel>", lambda event: self.settings_canvas.yview_scroll(-int(event.delta / 120), "units"))
        presets = ttk.LabelFrame(self.form, text="프리셋", padding=5)
        presets.pack(fill="x")
        self.preset_combo = ttk.Combobox(presets, textvariable=self.preset, values=["마지막 설정", "기본 규격", *self.store.presets], state="readonly", width=28)
        self.preset_combo.pack(fill="x")
        self.preset_combo.bind("<<ComboboxSelected>>", self.load_preset)
        actions = ttk.Frame(presets)
        actions.pack(fill="x", pady=3)
        for text, action in [("저장", self.save_preset), ("이름 변경", self.rename_preset), ("삭제", self.delete_preset)]:
            ttk.Button(actions, text=text, command=action, width=8).pack(side="left", padx=1)
        ttk.Label(presets, textvariable=self.preset_state, wraplength=280).pack(anchor="w")
        if self.store.protected:
            ttk.Button(presets, text="설정 복구", command=self.recover_settings).pack(fill="x")
        basic = ttk.LabelFrame(self.form, text="기본 규격", padding=5)
        basic.pack(before=presets, fill="x", pady=(0, 4))
        self._fields(basic, [("한 칸 가로폭", "cell_w", "mm"), ("한 칸 높이", "cell_h", "mm"), ("한 행의 라벨 수", "cols_per_row", "개")])
        input_frame = self.input_frame = ttk.LabelFrame(self.form, text="입력 범위", padding=5)
        input_frame.pack(fill="x", pady=4)
        ttk.Label(input_frame, text="시트 (기본: 첫 시트)").pack(anchor="w")
        self.sheet_combo = ttk.Combobox(input_frame, textvariable=self.sheet, state="readonly", width=28)
        self.sheet_combo.pack(fill="x")
        self.sheet_combo.bind("<<ComboboxSelected>>", self.change_sheet)
        ttk.Label(input_frame, text="셀 범위 (빈 값: 전체, 예 A1:C20)").pack(anchor="w")
        self.range_entry = ttk.Entry(input_frame, textvariable=self.cell_range)
        self.range_entry.pack(fill="x")
        ttk.Checkbutton(input_frame, text="선택 범위의 첫 행 제외", variable=self.skip_header).pack(anchor="w")
        self.advanced_toggle = ttk.Checkbutton(self.form, text="고급 설정", variable=self.advanced_open, command=self.toggle_advanced)
        self.advanced_toggle.pack(anchor="w", pady=4)
        self.advanced = ttk.LabelFrame(self.form, text="간격, 글자와 입력 해석", padding=5)
        self._fields(self.advanced, [("가로 간격", "gap_x", "mm"), ("세로 간격", "gap_y", "mm"), ("기본 글자 높이", "text_height", "mm"), ("최소 글자 높이 경고", "min_text_height", "mm")])
        self.ratio = tk.StringVar()
        ttk.Label(self.advanced, textvariable=self.ratio).pack(anchor="w")
        ttk.Checkbutton(self.advanced, text="긴 글자 자동 축소 및 압축", variable=self.auto_fit).pack(anchor="w")
        for title, key, values in [("글꼴", "font_key", list(CAD_FONTS)), ("테두리 색상", "box_color", list(CAD_COLORS)), ("문자 색상", "text_color", list(CAD_COLORS))]:
            ttk.Label(self.advanced, text=title).pack(anchor="w")
            variable = self.vars[key] = tk.StringVar()
            combo = self.combos[key] = ttk.Combobox(self.advanced, textvariable=variable, values=values, state="readonly", width=28)
            combo.pack(fill="x")
        ttk.Label(self.advanced, text="입력 문자 해석").pack(anchor="w")
        self.mode_combo = ttk.Combobox(self.advanced, textvariable=self.mode, values=["기존 해석", "표시 형식 반영"], state="readonly", width=28)
        self.mode_combo.pack(fill="x")
        self.advanced_summary = tk.StringVar()
        self.advanced_summary_label = ttk.Label(self.form, textvariable=self.advanced_summary, wraplength=280)
        self.advanced_summary_label.pack(fill="x")
        ttk.Label(self.form, textvariable=self.form_error, foreground="#a01818", wraplength=280).pack(fill="x", pady=4)
        self.preview_frame = ttk.Frame(self.body)
        self.preview_frame.grid(row=0, column=1, sticky="nsew")
        self.preview_frame.rowconfigure(1, weight=1)
        self.preview_frame.columnconfigure(0, weight=1)
        self.summary_label = ttk.Label(self.preview_frame, textvariable=self.summary)
        self.summary_label.grid(row=0, column=0, sticky="ew", pady=3)
        self.tabs = ttk.Notebook(self.preview_frame)
        self.tabs.grid(row=1, column=0, sticky="nsew")
        data_frame = ttk.Frame(self.tabs)
        self.tabs.add(data_frame, text="출력 데이터")
        data_frame.rowconfigure(0, weight=1)
        data_frame.columnconfigure(0, weight=1)
        self.data_tree = ttk.Treeview(data_frame, columns=("number", "count", "text", "source", "diagnosis"), show="headings", selectmode="browse", height=8)
        for key, title, width in [("number", "번호", 45), ("count", "칸", 40), ("text", "출력 예정 문자", 260), ("source", "원본 셀", 100), ("diagnosis", "확인", 90)]:
            self.data_tree.heading(key, text=title)
            self.data_tree.column(key, width=width, minwidth=35, stretch=key == "text")
        self.data_tree.grid(row=0, column=0, sticky="nsew")
        data_scroll = ttk.Scrollbar(data_frame, orient="vertical", command=self.data_tree.yview)
        data_scroll.grid(row=0, column=1, sticky="ns")
        self.data_tree.configure(yscrollcommand=data_scroll.set)
        self.data_tree.bind("<<TreeviewSelect>>", self.list_selected)
        self.data_tree.bind("<Double-1>", self.edit_from_table)
        self.data_tree.bind("<Return>", lambda event: self.edit_selected())
        self.data_tree.bind("<Home>", lambda event: self.select_table_edge())
        self.data_tree.bind("<End>", lambda event: self.select_table_edge(last=True))
        page_row = ttk.Frame(data_frame)
        page_row.grid(row=1, column=0, sticky="ew")
        ttk.Button(page_row, text="이전 100개", command=lambda: self.change_page(-1)).pack(side="left")
        ttk.Button(page_row, text="다음 100개", command=lambda: self.change_page(1)).pack(side="left")
        self.page_info = tk.StringVar()
        ttk.Label(page_row, textvariable=self.page_info).pack(side="left", padx=4)
        self.add_button = ttk.Button(page_row, text="행 추가", command=self.add_row)
        self.add_button.pack(side="right", padx=(4, 0))
        self.edit_button = ttk.Button(page_row, text="편집", command=self.edit_selected, state="disabled")
        self.edit_button.pack(side="right")
        self.preview = Preview(self.tabs, self.select_label)
        self.tabs.add(self.preview, text="도면 미리보기")
        ttk.Label(self.preview_frame, textvariable=self.selection_info, wraplength=650).grid(row=2, column=0, sticky="ew", pady=3)
        self.diag_tree = ttk.Treeview(self.preview_frame, columns=("severity", "cell", "message"), show="headings", height=3)
        for key, title, width in [("severity", "구분", 65), ("cell", "원본 셀", 90), ("message", "확인할 사항", 450)]:
            self.diag_tree.heading(key, text=title)
            self.diag_tree.column(key, width=width, stretch=key == "message")
        self.diag_tree.grid(row=4, column=0, sticky="ew")
        self.diag_tree.bind("<<TreeviewSelect>>", self.diagnostic_selected)
        self.confirm_button = ttk.Button(self.preview_frame, text="경고 내용 확인", command=self.confirm_warnings)
        diag_tools = self.diag_tools = ttk.Frame(self.preview_frame)
        diag_tools.grid(row=5, column=0, sticky="ew")
        diag_choice = ttk.Combobox(diag_tools, textvariable=self.diag_filter, values=["전체", "저장 차단", "경고", "선택 라벨"], state="readonly", width=9)
        diag_choice.pack(side="left")
        diag_choice.bind("<<ComboboxSelected>>", lambda event: self.change_diagnostic_page(0, reset=True))
        ttk.Button(diag_tools, text="이전", command=lambda: self.change_diagnostic_page(-1), width=6).pack(side="left")
        ttk.Button(diag_tools, text="다음", command=lambda: self.change_diagnostic_page(1), width=6).pack(side="left")
        self.diag_page_info = tk.StringVar()
        ttk.Label(diag_tools, textvariable=self.diag_page_info).pack(side="left", padx=3)
        self.confirm_button.grid(row=6, column=0, sticky="ew", pady=2)
        bottom = ttk.Frame(outer)
        bottom.grid(row=3, column=0, sticky="ew", pady=(5, 0))
        bottom.columnconfigure(0, weight=1)
        self.run_button = ttk.Button(bottom, text="DXF 저장", command=self.on_generate, state="disabled")
        self.run_button.grid(row=0, column=0, sticky="ew")
        self.cancel_button = ttk.Button(bottom, text="작업 취소", command=self.cancel, state="disabled")
        self.cancel_button.grid(row=0, column=1, padx=5)
        ttk.Label(bottom, textvariable=self.save_reason, wraplength=850).grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_label = ttk.Label(bottom, textvariable=self.status, wraplength=850)
        self.status_label.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.success_actions = ttk.Frame(bottom)
        self.success_actions.grid(row=3, column=0, columnspan=2, sticky="ew")
        for text, action in [("DXF 열기", self.open_output), ("저장 폴더 열기", lambda: self.open_output(folder=True)), ("다음 파일 선택", self.on_browse)]:
            ttk.Button(self.success_actions, text=text, command=action).pack(side="left", padx=2)
        self.success_actions.grid_remove()

    def _fields(self, parent, fields):
        for title, key, unit in fields:
            row = ttk.Frame(parent)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=title, width=19).pack(side="left")
            variable = self.vars[key] = tk.StringVar()
            entry = self.entries[key] = ttk.Entry(row, textvariable=variable, width=9)
            entry.pack(side="left")
            entry.bind("<FocusIn>", self._focus_field, add="+")
            ttk.Label(row, text=unit).pack(side="left", padx=3)

    def _focus_field(self, event):
        self.schedule_idle(lambda: self._scroll_to_field(event.widget))

    def schedule_idle(self, action):
        if self.closed:
            return
        identifier = [None]
        def run():
            self.idle_ids.discard(identifier[0])
            if not self.closed:
                action()
        identifier[0] = self.root.after_idle(run)
        self.idle_ids.add(identifier[0])

    def switch_tab(self, direction):
        if self.modal_open:
            return "break"
        self._show_settings = False
        self._layout_panels()
        index = (self.tabs.index(self.tabs.select()) + direction) % len(self.tabs.tabs())
        self.tabs.select(index)
        (self.data_tree if index == 0 else self.preview.canvas).focus_set()
        return "break"

    def _scroll_to_field(self, widget):
        if self.closed or not widget.winfo_exists():
            return
        relative = widget.winfo_rooty() - self.form.winfo_rooty()
        total = max(self.form.winfo_height(), 1)
        self.settings_canvas.yview_moveto(max(0, (relative - 50) / total))

    def toggle_advanced(self):
        if self.advanced_open.get():
            self.advanced.pack(before=self.advanced_summary_label, fill="x", pady=4)
        else:
            self.advanced.pack_forget()

    def _resize(self, event):
        if event.widget is not self.root:
            return
        narrow = event.width < 950
        if narrow == self._narrow:
            return
        self._narrow = narrow
        self._layout_panels()

    def _layout_panels(self):
        if self._narrow:
            self.body.columnconfigure(0, weight=1)
            self.body.columnconfigure(1, weight=0)
            if self._show_settings:
                self.preview_frame.grid_remove()
                self.settings_frame.grid(row=0, column=0, sticky="nsew")
                self.settings_button.configure(text="결과 보기")
            else:
                self.settings_frame.grid_remove()
                self.preview_frame.grid(row=0, column=0, sticky="nsew")
                self.settings_button.configure(text="설정 보기")
            if not self.settings_button.winfo_manager():
                self.settings_button.pack(side="right", padx=5)
        else:
            self.body.columnconfigure(0, weight=0)
            self.body.columnconfigure(1, weight=1)
            self.settings_frame.grid(row=0, column=0, sticky="nsew")
            self.preview_frame.grid(row=0, column=1, sticky="nsew")
            self.settings_button.pack_forget()
        caption(self.settings_button, self.settings_button.cget("text"))

    def toggle_settings(self):
        if self._narrow:
            self._show_settings = not self._show_settings
            self._layout_panels()
        else:
            self.entries["cell_w"].focus_set()

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

    def select_file(self, value, sheet=None):
        if self.saving or self.modal_open:
            self.status.set("저장 중입니다. 완료 또는 취소 후 파일을 바꿔 주세요.")
            return
        path = validate_excel_path(value)
        if not self.confirm_discard(always=True):
            self._restore_selection()
            return
        options = self.input_options()
        self.pending_edit_reset = False
        self.excel_path.set(str(path))
        self.drop_area.configure(text=f"선택한 파일: {path.name}")
        self.success_actions.grid_remove()
        settings = self.parse_settings()
        self.pending_read = (path, sheet)
        self.busy = True
        self.confirmed = False
        self.status.set(f"읽는 중: {path.name}")
        self.update_save_state()

        def action(token, report):
            source = read_workbook(path, sheet, token)
            report("검사 중")
            analysis = analyze(source, options, token)
            report("도면 생성 중")
            layout = compute_layout(analysis.blocks, settings, token) if settings else None
            return source, analysis, analysis, layout, settings, True, 0
        self.jobs.start("read", action)

    def on_drop(self, event):
        self.on_drop_leave(event)
        try:
            if self.saving or self.modal_open:
                self.status.set("저장 중에는 새 파일을 선택할 수 없습니다.")
                return REFUSE_DROP
            self.select_file(select_dropped_file(self.root.tk, event.data))
        except (ValueError, tk.TclError) as error:
            current = f" 현재 파일 {Path(self.excel_path.get()).name}을 유지합니다." if self.excel_path.get() else ""
            self.status.set(f"새 파일 선택 실패: {error}{current}")
            return REFUSE_DROP
        return COPY

    def on_browse(self):
        if self.modal_open:
            return
        if self.saving:
            self.status.set("저장 완료 또는 취소 후 다음 파일을 선택해 주세요.")
            return
        with self.dialog_scope():
            value = filedialog.askopenfilename(parent=self.root, title="Excel 파일 선택", filetypes=[("Excel 파일", "*.xlsx *.xls")])
        if value:
            try:
                self.select_file(value)
            except ValueError as error:
                self.status.set(f"새 파일 선택 실패: {error}")

    def reload(self):
        if self.excel_path.get():
            self.select_file(self.excel_path.get(), self.sheet.get() or None)

    def change_sheet(self, event=None):
        if self.snapshot:
            if self.saving:
                self.sheet.set(self.snapshot.sheet)
                return
            self.select_file(self.snapshot.path, self.sheet.get())

    def clear_file(self):
        if self.saving or self.modal_open or not self.confirm_discard(always=True):
            return
        self.jobs.invalidate()
        self.busy = False
        self.pending_read = None
        self.snapshot = self.analysis = self.layout = None
        self.base_analysis = None
        self.replacements.clear()
        self.additions.clear()
        self.edit_revision = self.saved_edit_revision = 0
        self.rendered_edit_revision = 0
        self.source_changed = False
        self.pending_edit_reset = False
        self.diagnostics = ()
        self.selected = None
        self.selection_info.set("라벨을 선택하면 크기와 원본 셀을 확인할 수 있습니다.")
        self.success_actions.grid_remove()
        self.excel_path.set("")
        self.sheet.set("")
        self.sheet_combo.configure(values=[])
        self._loading = True
        self.cell_range.set("")
        self.skip_header.set(False)
        self._loading = False
        self.preview.set_layout(None)
        self.drop_area.configure(text="Excel 파일을 놓거나 행 추가로 시작하세요")
        self.status.set("Excel을 불러오거나 행 추가로 시작하세요.")
        self.summary.set("라벨 0개, 총 0칸")
        self.render_list()
        self.render_diagnostics()
        self.update_save_state()

    def input_options(self):
        return InputOptions(self.cell_range.get().strip(), self.skip_header.get(), "display" if self.mode.get() == "표시 형식 반영" else "legacy")

    def parse_settings(self):
        self.invalid_field = None
        values = {}
        for key in ("cell_w", "cell_h", "cols_per_row", "gap_x", "gap_y", "text_height", "min_text_height"):
            try:
                value = self.vars[key].get().strip()
                number = int(value) if key == "cols_per_row" else float(value)
                import math
                if not math.isfinite(number) or (number <= 0 if key not in {"gap_x", "gap_y"} else number < 0):
                    raise ValueError()
                values[key] = number
            except (ValueError, OverflowError):
                self.invalid_field = key
                names = {"cell_w": "한 칸 가로폭", "cell_h": "한 칸 높이", "cols_per_row": "한 행의 라벨 수", "gap_x": "가로 간격", "gap_y": "세로 간격", "text_height": "기본 글자 높이", "min_text_height": "최소 글자 높이 경고"}
                self.form_error.set(f"입력 오류: {names[key]}에는 {'0 이상' if key in {'gap_x', 'gap_y'} else '0보다 큰'} 유한한 {'정수' if key == 'cols_per_row' else '숫자'}를 입력해 주세요.")
                return None
        values["text_scale"] = values.pop("text_height") / values["cell_h"]
        try:
            settings = LabelSettings(**values, auto_fit=self.auto_fit.get(), font_key=self.vars["font_key"].get(),
                                     box_color=CAD_COLORS[self.vars["box_color"].get()], text_color=CAD_COLORS[self.vars["text_color"].get()])
            self.form_error.set("")
            self.ratio.set(f"높이 대비 {settings.text_scale * 100:g}% (기존 비율 {settings.text_scale:g})")
            self.advanced_summary.set(f"간격 {settings.gap_x:g}/{settings.gap_y:g} mm, 글자 {settings.cell_h * settings.text_scale:g} mm, 최소 경고 {settings.min_text_height:g} mm, {self.mode.get()}")
            return settings
        except (ValueError, KeyError) as error:
            self.form_error.set(f"입력 오류: {error}")
            return None

    def settings_changed(self, *args):
        if self._loading or self.closed:
            return
        if self.snapshot and self.has_edits and self.analysis:
            try:
                desired = self.input_options()
            except ValueError:
                desired = None
            if desired is not None and desired != self.analysis.options:
                if not self.pending_edit_reset and not self.confirm_discard(always=True):
                    self._loading = True
                    self.cell_range.set(self.analysis.options.cell_range)
                    self.skip_header.set(self.analysis.options.skip_header)
                    self.mode.set("표시 형식 반영" if self.analysis.options.mode == "display" else "기존 해석")
                    self._loading = False
                    self.pending_edit_reset = False
                else:
                    self.pending_edit_reset = True
            elif desired == self.analysis.options:
                self.pending_edit_reset = False
        self.confirmed = False
        self.parse_settings()
        self._update_preset_state()
        if self.saving:
            self.status.set("저장 중 변경한 설정은 다음 결과부터 적용합니다.")
            return
        self.jobs.invalidate()
        self.busy = bool(self.snapshot or self.pending_read or self.has_edits)
        if self.debounce_id:
            self.root.after_cancel(self.debounce_id)
        self.debounce_id = self.root.after(220, self.rebuild)
        self.update_save_state()

    def rebuild(self):
        self.debounce_id = None
        if self.pending_read:
            path, sheet = self.pending_read
            try:
                self.select_file(path, sheet)
            except ValueError as error:
                self.form_error.set(str(error))
                self.busy = False
                self.update_save_state()
            return
        settings = self.parse_settings()
        try:
            options = self.input_options()
        except ValueError as error:
            self.form_error.set(str(error))
            self.busy = False
            self.update_save_state()
            return
        if self.snapshot is None and not self.has_edits:
            self.busy = False
            self.update_save_state()
            return
        source = self.snapshot
        reset_edits = self.pending_edit_reset
        revision = self.edit_revision
        replacements = () if reset_edits else tuple(self.replacements.items())
        additions = () if reset_edits else tuple(self.additions)
        self.busy = True
        self.status.set("검사 중: 현재 입력을 다시 확인합니다.")
        self.update_save_state()
        def action(token, report):
            base = analyze(source, options, token) if source else Analysis(None, options, "직접 입력", (), ())
            analysis = apply_edits(base, replacements, additions)
            report("도면 생성 중")
            layout = compute_layout(analysis.blocks, settings, token) if settings else None
            return source, base, analysis, layout, settings, reset_edits, revision
        self.jobs.start("layout", action)

    def poll(self):
        self.after_id = None
        if self.closed:
            return
        for _ in range(100):
            try:
                result = self.jobs.queue.get_nowait()
            except Empty:
                break
            if result.generation != self.jobs.generation:
                continue
            if result.status == "progress":
                self.status.set(str(result.value))
                continue
            self.busy = False
            was_saving = self.saving
            self.saving = False
            if self.notice_scope:
                self.notice_scope.__exit__(None, None, None)
                self.notice_scope = None
            if result.status == "done":
                if result.kind == "save":
                    self.output = Path(result.value)
                    self.status.set(f"저장 완료: {len(self.analysis.labels)}개 라벨, {self.analysis.cell_count}칸, {self.output.name}")
                    self.success_actions.grid()
                    self.remember()
                    self.saved_edit_revision = self.edit_revision
                    # Apply edits made while a captured save was in progress.
                else:
                    self.snapshot, self.base_analysis, self.analysis, self.layout, self.last_settings, reset_edits, revision = result.value
                    self.pending_read = None
                    if result.kind == "read":
                        self.source_changed = False
                    if reset_edits:
                        self.replacements.clear()
                        self.additions.clear()
                        self.edit_revision = self.saved_edit_revision = 0
                    self.rendered_edit_revision = 0 if reset_edits else revision
                    self.pending_edit_reset = False
                    self.excel_path.set(str(self.snapshot.path) if self.snapshot else "")
                    self.sheet.set(self.snapshot.sheet if self.snapshot else "")
                    self.sheet_combo.configure(values=self.snapshot.sheets if self.snapshot else [])
                    extra = tuple(Diagnostic("warning", code, message, label=label) for label, code, message in self.layout.warnings) if self.layout else ()
                    self.diagnostics = self.analysis.diagnostics + extra
                    self.page = 0
                    self.diag_page = 0
                    self.selected = None
                    self.selection_info.set("라벨을 선택하면 크기와 원본 셀을 확인할 수 있습니다.")
                    self.preview.set_layout(self.layout)
                    self.render_list()
                    self.render_diagnostics()
                    origin = f"{self.snapshot.sheet}!{self.analysis.applied_range}" if self.snapshot else "직접 입력"
                    self.summary.set(f"라벨 {len(self.analysis.labels):,}개, 총 {self.analysis.cell_count:,}칸, 확인 {len(self.diagnostics):,}건 | {origin}")
                    self.status.set("더블클릭으로 편집하거나 DXF를 저장하세요." if self.analysis.labels else "라벨이 없습니다. 범위를 확인하거나 행을 추가하세요.")
            elif result.status == "cancelled":
                self.status.set("작업이 취소되었습니다. 기존 출력 파일은 유지합니다.")
                if not was_saving:
                    self.pending_read = None
                    self._restore_selection()
                    self.restore_pending_options()
            else:
                if was_saving:
                    self.status.set(f"저장 실패: {result.value}")
                    if "원본" in str(result.value):
                        self.source_changed = True
                else:
                    self.pending_read = None
                    failed = Path(self.excel_path.get()).name
                    self._restore_selection()
                    self.restore_pending_options()
                    current = f" 현재 파일 {self.snapshot.path.name}을 유지합니다." if self.snapshot else " 현재 작업 데이터를 유지합니다." if self.has_edits else ""
                    self.status.set(f"{failed} 읽기 또는 검사 실패: {result.value}{current}")
                    if result.kind == "layout":
                        self.form_error.set(str(result.value))
                        self.invalid_field = "cell_h" if "높이" in str(result.value) else "cell_w"
            if was_saving and not self.current_matches():
                self.settings_changed()
            self.update_save_state()
        self.after_id = self.root.after(40, self.poll)

    def _restore_selection(self):
        if self.snapshot:
            self.excel_path.set(str(self.snapshot.path))
            self.sheet.set(self.snapshot.sheet)
        else:
            self.excel_path.set("")
        self.drop_area.configure(text=f"현재 파일: {self.snapshot.path.name}" if self.snapshot else "Excel 파일을 놓거나 행 추가로 시작하세요")

    def restore_pending_options(self):
        if self.pending_edit_reset and self.analysis:
            self._loading = True
            self.cell_range.set(self.analysis.options.cell_range)
            self.skip_header.set(self.analysis.options.skip_header)
            self.mode.set("표시 형식 반영" if self.analysis.options.mode == "display" else "기존 해석")
            self._loading = False
        self.pending_edit_reset = False

    def render_list(self):
        if self.snapshot:
            self.input_frame.pack(before=self.advanced_toggle, fill="x", pady=4)
        else:
            self.input_frame.pack_forget()
        self.mode_combo.configure(state="readonly" if self.snapshot else "disabled")
        self.data_tree.delete(*self.data_tree.get_children())
        labels = self.analysis.labels if self.analysis else ()
        start, end = self.page * PAGE_SIZE, min((self.page + 1) * PAGE_SIZE, len(labels))
        counts = {}
        for diagnostic in self.diagnostics:
            if diagnostic.label is not None:
                counts[diagnostic.label] = counts.get(diagnostic.label, 0) + 1
        for index in range(start, end):
            label = labels[index]
            summary = " / ".join(label.texts[:8])
            if len(label.texts) > 8:
                summary += f" (전체 {len(label.texts):,}칸, 더블클릭으로 편집)"
            self.data_tree.insert("", "end", iid=str(index), values=(index + 1, len(label.texts), summary,
                                  self.label_origin(label), f"{counts[index]}건" if index in counts else "정상"))
        self.page_info.set(f"{start + 1 if labels else 0}-{end} / {len(labels):,}개")

    def change_page(self, delta):
        if self.analysis:
            self.page = max(0, min(self.page + delta, max(0, (len(self.analysis.labels) - 1) // PAGE_SIZE)))
            self.render_list()

    def list_selected(self, event=None):
        selected = self.data_tree.selection()
        if selected:
            self.select_label(int(selected[0]), from_list=True)

    def select_table_edge(self, last=False):
        rows = self.data_tree.get_children()
        if rows:
            row = rows[-1] if last else rows[0]
            self.data_tree.focus(row)
            self.data_tree.selection_set(row)
            self.data_tree.see(row)
            self.select_label(int(row), from_list=True)
        return "break"

    def select_label(self, index, from_list=False):
        if not self.analysis or index >= len(self.analysis.labels):
            return
        self.selected = index
        if not from_list:
            self.page = index // PAGE_SIZE
            self.render_list()
            self.data_tree.selection_set(str(index))
            self.data_tree.see(str(index))
        label = self.analysis.labels[index]
        dimensions = ""
        if self.layout:
            x1, y1, x2, y2 = self.layout.label_bounds[index]
            cells = self.preview.cells_by_label[index]
            dimensions = f", {x2 - x1:g} × {y2 - y1:g} mm, 글자 최소 {min(c.text_height for c in cells):.3f} mm, 가로 배율 {min(c.width_factor for c in cells):.3f}"
        self.selection_info.set(f"라벨 {index + 1}{dimensions}, {self.label_origin(label)}")
        self.preview.select(index, center=from_list)
        self.render_diagnostics()

    def render_diagnostics(self):
        for widget in (self.diag_tree, self.diag_tools, self.confirm_button):
            if self.diagnostics:
                widget.grid()
            else:
                widget.grid_remove()
        self.update_edit_state()
        self.diag_tree.delete(*self.diag_tree.get_children())
        shown = self.filtered_diagnostics()
        self.diag_page = max(0, min(self.diag_page, max(0, (len(shown) - 1) // 200)))
        start, end = self.diag_page * 200, min((self.diag_page + 1) * 200, len(shown))
        for index, diagnostic in shown[start:end]:
            self.diag_tree.insert("", "end", iid=str(index), values=("저장 차단" if diagnostic.severity == "error" else "경고", diagnostic.address, diagnostic.message))
        warnings = sum(d.severity == "warning" for d in self.diagnostics)
        self.confirm_button.configure(text=f"경고 {warnings:,}건 {'확인 완료' if self.confirmed else '내용 확인'}", state="normal" if warnings and not self.busy and not self.confirmed else "disabled")
        caption(self.confirm_button, self.confirm_button.cget("text"))
        self.diag_page_info.set(f"{start + 1 if shown else 0}-{end} / {len(shown):,}건")

    def filtered_diagnostics(self):
        choice = self.diag_filter.get()
        return [(i, d) for i, d in enumerate(self.diagnostics) if choice == "전체" or
                choice == "저장 차단" and d.severity == "error" or choice == "경고" and d.severity == "warning" or
                choice == "선택 라벨" and self.selected is not None and d.label == self.selected]

    def change_diagnostic_page(self, delta, reset=False):
        self.diag_page = 0 if reset else max(0, self.diag_page + delta)
        self.render_diagnostics()

    @property
    def has_edits(self):
        return bool(self.replacements or self.additions)

    @property
    def unsaved_edits(self):
        return self.has_edits and self.edit_revision != self.saved_edit_revision

    def show_filename(self, *args):
        value = self.excel_path.get()
        self.filename.set(Path(value).name if value else "선택한 Excel 없음 (직접 입력 가능)")

    def label_origin(self, label):
        if label.origin == "manual":
            return "직접 입력"
        addresses = [a for a in label.addresses if a != "직접 입력"]
        location = f"{addresses[0]}:{addresses[-1]}" if addresses else "직접 입력"
        return location + (" (수정)" if label.origin == "edited" else "")

    def confirm_discard(self, always=False):
        if not (self.has_edits if always else self.unsaved_edits):
            return True
        if self.modal_open:
            return False
        with self.dialog_scope():
            return messagebox.askyesno("작업 데이터 확인", "편집하거나 추가한 작업 데이터가 사라집니다. 계속할까요?\n필요하면 먼저 DXF를 저장하세요.", parent=self.root)

    def update_edit_state(self):
        ready = not (self.busy or self.saving or self.debounce_id or self.modal_open)
        self.add_button.configure(state="normal" if ready else "disabled")
        self.edit_button.configure(state="normal" if ready and self.selected is not None else "disabled")

    def edit_from_table(self, event):
        row = self.data_tree.identify_row(event.y)
        if row and self.data_tree.identify_region(event.x, event.y) in {"cell", "tree"}:
            self.data_tree.selection_set(row)
            self.select_label(int(row))
            self.edit_selected()
        return "break"

    def add_row(self):
        return self.open_editor(None)

    def edit_selected(self):
        if self.selected is not None:
            self.open_editor(self.selected)
        return "break"

    def popup_closed(self):
        self.editor = None
        if self.popup_scope:
            scope, self.popup_scope = self.popup_scope, None
            scope.__exit__(None, None, None)
        if not self.closed and self.data_tree.winfo_exists():
            self.update_edit_state()
            self.data_tree.focus_set()

    def open_editor(self, index):
        if self.closed or self.busy or self.saving or self.debounce_id or self.modal_open:
            return
        if index is not None and (not self.analysis or index < 0 or index >= len(self.analysis.labels)):
            return
        label = self.analysis.labels[index] if index is not None else None
        self.popup_scope = self.dialog_scope()
        self.popup_scope.__enter__()
        try:
            self.editor = LabelEditor(self.root, texts=label.texts if label else None,
                                      origin=self.label_origin(label) if label else "새 라벨을 작업 데이터에 추가합니다.",
                                      on_apply=lambda text: self.apply_label(index, text), on_close=self.popup_closed)
        except Exception:
            self.popup_closed()
            raise
        self.update_edit_state()

    def apply_label(self, index, value):
        if self.closed or self.busy or self.saving or self.debounce_id:
            raise ValueError("결과 갱신이 끝난 뒤 다시 적용해 주세요.")
        texts = parse_label_text(value)
        replacements, additions = self.replacements.copy(), self.additions.copy()
        original_count = len(self.base_analysis.labels) if self.base_analysis else 0
        if index is None:
            additions.append(edited_label(texts))
        elif index < original_count:
            replacements[index] = edited_label(texts, self.base_analysis.labels[index])
        else:
            offset = index - original_count
            if not 0 <= offset < len(additions):
                raise ValueError("편집할 라벨을 다시 선택해 주세요.")
            additions[offset] = edited_label(texts, additions[offset])
        # Validate capacity before committing the in-memory transaction.
        candidate = apply_edits(self.base_analysis, replacements.items(), additions, self.input_options())
        self.replacements, self.additions = replacements, additions
        self.edit_revision += 1
        self.analysis = candidate
        self.layout = None
        self.diagnostics = candidate.diagnostics
        self.preview.set_layout(None)
        self.selection_info.set("도면 갱신 중입니다.")
        self.render_list()
        self.render_diagnostics()
        origin = f"{self.snapshot.sheet}!{candidate.applied_range}" if self.snapshot else "직접 입력"
        self.summary.set(f"라벨 {len(candidate.labels):,}개, 총 {candidate.cell_count:,}칸, 확인 {len(candidate.diagnostics):,}건 | {origin}")
        self.output = None
        self.success_actions.grid_remove()
        self.settings_changed()

    def show_help(self):
        if self.closed or self.modal_open:
            return
        self.popup_scope = self.dialog_scope()
        self.popup_scope.__enter__()
        try:
            dialog = self.editor = tk.Toplevel(self.root)
            dialog.withdraw()
            dialog.title("앱 도움말")
            dialog.transient(self.root)
            dialog.resizable(False, False)
            frame = ttk.Frame(dialog, padding=20)
            frame.pack(fill="both", expand=True)
            ttk.Label(frame, text="Excel CAD Label Maker", font=("맑은 고딕", 13, "bold")).pack(anchor="w")
            ttk.Label(frame, text="Excel 또는 직접 입력한 문자로 전기함 덕트 라벨의 DXF 도면을 만듭니다.\n행 추가와 더블클릭으로 편집하고, 도면을 확인한 뒤 DXF를 저장하세요.\n원본 Excel은 변경하지 않습니다.", wraplength=480).pack(anchor="w", pady=12)
            ttk.Label(frame, text=f"버전 {self.updates.current_version}\n원개발자: 직장인\nFork 및 후속 개발: plcmanjp").pack(anchor="w")
            ttk.Label(frame, text="DXF 출력 지원, DWG 직접 출력 미지원.\nCAD의 글꼴 환경에 따라 한글 표시가 달라질 수 있습니다.", wraplength=480).pack(anchor="w", pady=12)
            close = ttk.Button(frame, text="닫기", command=dialog.destroy)
            close.pack(anchor="e")
            expose_buttons(dialog)
            dialog.bind("<Escape>", lambda event: dialog.destroy())
            dialog.bind("<Destroy>", lambda event: self.popup_closed() if event.widget is dialog else None, add="+")
            center(dialog, self.root)
            dialog.deiconify()
            dialog.grab_set()
            close.focus_set()
        except Exception:
            self.popup_closed()
            raise

    def diagnostic_selected(self, event=None):
        selected = self.diag_tree.selection()
        if selected:
            diagnostic = self.diagnostics[int(selected[0])]
            if diagnostic.label is not None and diagnostic.label != self.selected:
                self.select_label(diagnostic.label)
            elif diagnostic.address:
                self.selection_info.set(f"원본 위치: {self.snapshot.sheet}!{diagnostic.address}\n{diagnostic.message}")

    def confirm_warnings(self):
        if self.busy or not self.analysis:
            return
        self.confirmed = True
        self.render_diagnostics()
        self.update_save_state()

    def update_save_state(self):
        if self.saving:
            reason = "저장 중입니다. 중복 저장은 기다려 주세요."
        elif self.busy or self.debounce_id:
            reason = "결과를 갱신 중입니다. 완료 후 저장할 수 있습니다."
        elif self.form_error.get():
            reason = self.form_error.get()
        elif self.source_changed:
            reason = "Excel 원본이 변경되었습니다. 다시 읽기로 결과를 재확인해 주세요."
        elif not self.analysis:
            reason = "Excel을 불러오거나 행을 추가해 주세요."
        elif self.analysis.errors:
            reason = f"저장 차단 오류 {len(self.analysis.errors)}건을 원본에서 수정해 주세요."
        elif not self.current_matches():
            reason = "현재 설정과 결과가 다릅니다. 결과를 다시 확인해 주세요."
        elif not self.analysis.labels or not self.layout:
            reason = "출력할 라벨이 없습니다. 시트와 범위를 확인해 주세요."
        elif any(d.severity == "warning" for d in self.diagnostics) and not self.confirmed:
            reason = "출력 예정 문자와 경고 내용을 확인한 뒤 경고 내용 확인을 눌러 주세요."
        else:
            reason = "저장할 준비가 되었습니다."
        self.save_reason.set(reason)
        self.run_button.configure(state="normal" if reason == "저장할 준비가 되었습니다." else "disabled")
        self.cancel_button.configure(state="normal" if self.busy else "disabled")
        self.update_edit_state()

    def current_matches(self):
        try:
            return self.analysis is not None and self.rendered_edit_revision == self.edit_revision and self.last_settings == self.parse_settings() and self.analysis.options == self.input_options()
        except ValueError:
            return False

    def on_generate(self):
        if self.modal_open:
            return
        self.update_save_state()
        if str(self.run_button.cget("state")) != "normal":
            if self.invalid_field:
                self._show_settings = True
                self._layout_panels()
                self.advanced_open.set(True)
                self.toggle_advanced()
                self.entries[self.invalid_field].focus_set()
            return
        with self.dialog_scope():
            output = filedialog.asksaveasfilename(parent=self.root, title="DXF 도면 저장", initialfile=(self.snapshot.path.stem if self.snapshot else "라벨") + ".dxf",
                                                 defaultextension=".dxf", filetypes=[("DXF 도면", "*.dxf")], confirmoverwrite=True)
        if not output:
            self.status.set("저장을 취소했습니다. 기존 출력 파일은 유지합니다.")
            return
        source, layout = self.snapshot, self.layout
        self.busy = self.saving = True
        self.success_actions.grid_remove()
        self.notice_scope = self.updates.defer_notices()
        self.notice_scope.__enter__()
        self.update_save_state()
        def action(token, report):
            report("도면 생성 중")
            if source and not source.unchanged():
                raise ValueError("Excel 원본이 변경되었습니다. 다시 읽기로 결과를 확인해 주세요.")
            doc = drawing_from_layout(layout, token)
            report("저장 중")
            if source and not source.unchanged():
                raise ValueError("Excel 원본이 변경되었습니다. 다시 읽기로 결과를 확인해 주세요.")
            save_drawing(doc, output, token)
            return output
        self.jobs.start("save", action)

    def cancel(self):
        if self.debounce_id and not self.saving:
            self.root.after_cancel(self.debounce_id)
            self.debounce_id = None
            self.jobs.invalidate()
            self.busy = False
            self.pending_read = None
            self._restore_selection()
            self.restore_pending_options()
            self.status.set("갱신을 취소했습니다. 편집 데이터는 유지합니다.")
            self.update_save_state()
            return
        if self.jobs.token and self.busy:
            cancelled = self.jobs.token.cancel()
            self.status.set("취소 요청을 받았습니다. 안전한 중단 지점까지 기다려 주세요." if cancelled else "파일 저장이 완료되었습니다. 완료 결과를 확인하는 중입니다.")

    def values(self):
        settings = self.parse_settings()
        if settings is None:
            raise SettingsError(self.form_error.get())
        return {**asdict(settings), "mode": "display" if self.mode.get() == "표시 형식 반영" else "legacy"}

    def apply_values(self, values):
        loading = self._loading
        self._loading = True
        for key in ("cell_w", "cell_h", "cols_per_row", "gap_x", "gap_y", "min_text_height"):
            self.vars[key].set(f"{values[key]:g}")
        self.vars["text_height"].set(f"{values['cell_h'] * values['text_scale']:g}")
        self.vars["font_key"].set(values["font_key"])
        for key in ("box_color", "text_color"):
            self.vars[key].set(next(name for name, number in CAD_COLORS.items() if number == values[key]))
        self.auto_fit.set(values["auto_fit"])
        self.mode.set("표시 형식 반영" if values["mode"] == "display" else "기존 해석")
        self._loading = loading
        self.parse_settings()
        if not loading:
            self.settings_changed()

    def _update_preset_state(self):
        try:
            current = self.values()
            baseline = defaults() if self.preset.get() == "기본 규격" else self.store.presets.get(self.preset.get(), self.store.last)
            self.preset_state.set("수정됨" if current != baseline else "선택 설정과 같음")
        except SettingsError:
            self.preset_state.set("입력 수정 필요")

    def load_preset(self, event=None):
        name = self.preset.get()
        self.apply_values(defaults() if name == "기본 규격" else self.store.presets.get(name, self.store.last))
        self._update_preset_state()

    def refresh_presets(self):
        self.preset_combo.configure(values=["마지막 설정", "기본 규격", *self.store.presets])
        self._update_preset_state()

    def save_preset(self):
        if self.modal_open:
            return
        try:
            values = self.values()
            with self.dialog_scope():
                name = simpledialog.askstring("프리셋 저장", "설정 이름", parent=self.root)
                if name is None:
                    return
                name = name.strip()
                overwrite = name in self.store.presets
                if overwrite and not messagebox.askyesno("프리셋 덮어쓰기", f"{name}의 설정을 바꿀까요?", parent=self.root):
                    return
            self.store.save(name, values, overwrite)
            self.preset.set(name)
            self.refresh_presets()
            self.status.set(f"프리셋 저장 완료: {name}")
        except (SettingsError, OSError) as error:
            self.status.set(f"프리셋 저장 실패: {error}")

    def rename_preset(self):
        if self.modal_open:
            return
        old = self.preset.get()
        with self.dialog_scope():
            name = simpledialog.askstring("프리셋 이름 변경", "새 이름", initialvalue=old, parent=self.root)
        if name is not None:
            try:
                self.store.rename(old, name)
                self.preset.set(name.strip())
                self.refresh_presets()
            except SettingsError as error:
                self.status.set(str(error))

    def delete_preset(self):
        if self.modal_open:
            return
        name = self.preset.get()
        if name not in self.store.presets:
            self.status.set("삭제할 사용자 프리셋을 선택해 주세요.")
            return
        with self.dialog_scope():
            confirmed = messagebox.askyesno("프리셋 삭제", f"{name}을 삭제할까요?", parent=self.root)
        if confirmed:
            try:
                self.store.delete(name)
                self.preset.set("마지막 설정")
                self.refresh_presets()
            except SettingsError as error:
                self.status.set(str(error))

    def recover_settings(self):
        if self.modal_open:
            return
        with self.dialog_scope():
            confirmed = messagebox.askyesno("설정 복구", "기존 설정 파일을 백업하고 기본 설정으로 복구할까요?", parent=self.root)
        if confirmed:
            try:
                backup = self.store.recover()
                self.apply_values(self.store.last)
                self.refresh_presets()
                self.status.set(f"설정 복구 완료. {'기존 설정 백업을 보존했습니다.' if backup else '기본 설정을 저장했습니다.'}")
            except (SettingsError, OSError) as error:
                self.status.set(f"설정 복구 실패: {error}")

    def remember(self):
        try:
            self.store.remember(self.values())
            self._update_preset_state()
        except (SettingsError, OSError) as error:
            self.status.set(self.status.get() + f" 설정 저장 안내: {error}")

    def open_output(self, folder=False):
        if self.output is None:
            return
        try:
            os.startfile(self.output.parent if folder else self.output)
        except OSError:
            self.status.set("DXF 저장은 완료되었습니다. 연결된 CAD 또는 폴더 열기 설정을 확인해 주세요.")

    def make_example(self):
        if self.saving or self.modal_open:
            return
        with self.dialog_scope():
            value = filedialog.asksaveasfilename(parent=self.root, title="합성 입력 예제 저장", initialfile="라벨 입력 예제.xlsx", defaultextension=".xlsx", filetypes=[("Excel 예제", "*.xlsx")])
        if value:
            from openpyxl import Workbook
            protected = [self.snapshot.path] if self.snapshot else []
            if self.excel_path.get():
                protected.append(Path(self.excel_path.get()).resolve())
            if self.pending_read:
                protected.append(Path(self.pending_read[0]).resolve())
            if Path(value).resolve() in protected:
                self.status.set("현재 Excel 원본을 예제로 덮어쓸 수 없습니다. 다른 파일 이름을 선택해 주세요.")
                return
            book = Workbook()
            try:
                sheet = book.active
                sheet.title = "라벨 예제"
                for index in range(20):
                    for text in (f"LABEL {index + 1:02}", "전원 입력", "확인"):
                        sheet.append([text])
                    sheet.append([None])
                book.save(value)
                self.select_file(value)
            except Exception as error:
                self.status.set(f"예제를 저장하지 못했습니다: {error}")
            finally:
                book.close()

    def _destroyed(self, event):
        if event.widget is self.root:
            self.shutdown()

    def shutdown(self):
        if self.closed:
            return
        self.closed = True
        self.jobs.close()
        for identifier in (self.after_id, self.debounce_id, *self.idle_ids):
            if identifier:
                self.root.after_cancel(identifier)
        self.after_id = self.debounce_id = None
        self.idle_ids.clear()
        if self.notice_scope:
            self.notice_scope.__exit__(None, None, None)
            self.notice_scope = None

    def close(self):
        if self.modal_open or not self.confirm_discard():
            return
        self.remember()
        self.shutdown()
        self.root.destroy()
