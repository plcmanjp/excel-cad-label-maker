import os
import tkinter as tk
import unicodedata
from tkinter import filedialog, messagebox, ttk
import pandas as pd

# CAD 표준 색상 매핑
CAD_COLORS = {
    기본 (WhiteBlack, 7) 7,
    빨강 (Red, 1) 1,
    노랑 (Yellow, 2) 2,
    초록 (Green, 3) 3,
    하늘 (Cyan, 4) 4,
    파랑 (Blue, 5) 5,
    분홍 (Magenta, 6) 6,
}

# 글꼴 매핑
CAD_FONTS = {
    맑은 고딕 (Malgun Gothic) (MALGUN, malgun.ttf),
    굴림 (Gulim) (GULIM, gulim.ttc),
    돋움 (Dotum) (DOTUM, dotum.ttc),
    바탕 (Batang) (BATANG, batang.ttc),
    Arial (ARIAL, arial.ttf),
    AutoCAD 표준 (Standard) (STANDARD, txt.shx),
}


def get_text_display_units(text)
    문자열의 CAD 표시 너비 단위 계산
    units = 0.0
    for ch in text
        if unicodedata.east_asian_width(ch) in (F, W)
            units += 1.15
        elif ch.isupper() or ch.isdigit()
            units += 0.70
        else
            units += 0.55
    return max(units, 1.0)


def extract_blocks_auto(excel_path)
    엑셀의 각 열(Column)에서 세로 방향으로 데이터를 읽어

    빈 셀을 구분자로 사용하여 연속된 텍스트 묶음을 가변 크기 라벨로 자동 추출합니다.
    
    df = pd.read_excel(excel_path, header=None).fillna()
    labels_data = []

    for col_idx in range(df.shape[1])
        current_block = []
        for val in df.iloc[, col_idx]
            txt = str(val).strip()
            if txt
                current_block.append(txt)
            else
                if current_block
                    labels_data.append(current_block)
                    current_block = []
        if current_block
            labels_data.append(current_block)

    return labels_data


def generate_dxf_string(
    excel_path,
    cell_w,
    cell_h,
    gap_x,
    gap_y,
    cols_per_row,
    text_scale,
    auto_fit=True,
    font_key=맑은 고딕 (Malgun Gothic),
    box_color=7,
    text_color=7,
)
    문자 개수에 맞게 가변적으로 사각형과 텍스트를 생성합니다.
    labels_data = extract_blocks_auto(excel_path)
    if not labels_data
        return , 0

    base_text_height = cell_h  text_scale
    style_name, font_file = CAD_FONTS.get(font_key, (STANDARD, txt.shx))

    # DXF 헤더 및 글꼴 정의
    dxf_lines = [
        0,
        SECTION,
        2,
        TABLES,
        0,
        TABLE,
        2,
        STYLE,
        70,
        1,
        0,
        STYLE,
        2,
        style_name,
        70,
        0,
        40,
        0.0,
        41,
        1.0,
        50,
        0.0,
        71,
        0,
        42,
        2.5,
        3,
        font_file,
        4,
        ,
        0,
        ENDTAB,
        0,
        ENDSEC,
        0,
        SECTION,
        2,
        ENTITIES,
    ]

    # 그리드 배치를 위한 행별 최대 높이 계산
    rows_max_height = {}
    for idx, block_texts in enumerate(labels_data)
        r = idx  cols_per_row
        block_h = len(block_texts)  cell_h
        rows_max_height[r] = max(rows_max_height.get(r, 0.0), block_h)

    # 행별 Y 시작 오프셋 누적 계산
    row_y_offsets = {}
    accum_y = 0.0
    for r in range(max(rows_max_height.keys()) + 1 if rows_max_height else 0)
        row_y_offsets[r] = accum_y
        accum_y += rows_max_height[r] + gap_y

    for idx, block_texts in enumerate(labels_data)
        col_pos = idx % cols_per_row
        row_pos = idx  cols_per_row

        bx = col_pos  (cell_w + gap_x)
        by = -row_y_offsets[row_pos]

        # 인식된 텍스트 줄 수만큼 개별 사각형 및 텍스트 생성
        for i, txt in enumerate(block_texts)
            cell_top = by - (i  cell_h)
            cell_bottom = cell_top - cell_h

            # 개별 사각형 (LWPOLYLINE)
            dxf_lines.extend(
                [
                    0,
                    LWPOLYLINE,
                    8,
                    LABEL_BOX,
                    62,
                    str(box_color),
                    90,
                    4,
                    70,
                    1,
                    10,
                    f{bx.3f},
                    20,
                    f{cell_top.3f},
                    10,
                    f{bx + cell_w.3f},
                    20,
                    f{cell_top.3f},
                    10,
                    f{bx + cell_w.3f},
                    20,
                    f{cell_bottom.3f},
                    10,
                    f{bx.3f},
                    20,
                    f{cell_bottom.3f},
                ]
            )

            # 정중앙 텍스트
            if txt
                cx = bx + (cell_w  2.0)
                cy = (cell_top + cell_bottom)  2.0

                final_h = base_text_height
                width_factor = 1.0

                if auto_fit
                    avail_w = cell_w  0.75
                    units = get_text_display_units(txt)
                    est_w = units  base_text_height  1.2

                    if est_w  avail_w
                        req_scale = avail_w  est_w
                        if req_scale = 0.65
                            width_factor = req_scale
                        else
                            width_factor = 0.65
                            final_h = base_text_height  (req_scale  0.65)

                    max_allowed_h = cell_h  0.75
                    if final_h  max_allowed_h
                        final_h = max_allowed_h

                dxf_lines.extend(
                    [
                        0,
                        TEXT,
                        8,
                        TEXT_DATA,
                        62,
                        str(text_color),
                        7,
                        style_name,
                        10,
                        f{cx.3f},
                        20,
                        f{cy.3f},
                        30,
                        0.0,
                        40,
                        f{final_h.3f},
                        41,
                        f{width_factor.3f},
                        1,
                        txt,
                        72,
                        1,
                        11,
                        f{cx.3f},
                        21,
                        f{cy.3f},
                        31,
                        0.0,
                        73,
                        2,
                    ]
                )

    dxf_lines.extend([0, ENDSEC, 0, EOF])
    return n.join(dxf_lines), len(labels_data)


class App

    def __init__(self, root)
        self.root = root
        self.root.title(엑셀 데이터 ➔ CAD 자동 가변 라벨 배치기)
        self.root.geometry(560x630)
        self.root.resizable(False, False)

        self.excel_path = tk.StringVar()
        self.auto_fit_var = tk.BooleanVar(value=True)

        self.create_widgets()

    def create_widgets(self)
        # 1. 파일 선택
        frm_file = ttk.LabelFrame(self.root, text= 1. 엑셀 파일 선택 , padding=10)
        frm_file.pack(fill=x, padx=15, pady=6)

        ttk.Entry(frm_file, textvariable=self.excel_path, width=46).pack(
            side=left, padx=5
        )
        ttk.Button(frm_file, text=파일 찾기, command=self.on_browse).pack(
            side=left
        )

        # 2. 규격 설정
        frm_opts = ttk.LabelFrame(
            self.root,
            text= 2. 라벨 규격 설정 (칸 수 자동 인식) (mm) ,
            padding=10,
        )
        frm_opts.pack(fill=x, padx=15, pady=4)

        ttk.Label(frm_opts, text=한 행당 배치할 라벨 수).grid(
            row=0, column=0, sticky=w, pady=4
        )
        self.ent_cols = ttk.Entry(frm_opts, width=10)
        self.ent_cols.insert(0, 5)
        self.ent_cols.grid(row=0, column=1, sticky=w, pady=4, padx=5)

        ttk.Label(frm_opts, text=기준 글자 크기 비율).grid(
            row=0, column=2, sticky=w, pady=4, padx=(15, 0)
        )
        self.ent_font_scale = ttk.Entry(frm_opts, width=10)
        self.ent_font_scale.insert(0, 0.45)
        self.ent_font_scale.grid(row=0, column=3, sticky=w, pady=4, padx=5)

        ttk.Label(frm_opts, text=개별 1칸 가로폭).grid(
            row=1, column=0, sticky=w, pady=4
        )
        self.ent_w = ttk.Entry(frm_opts, width=10)
        self.ent_w.insert(0, 60)
        self.ent_w.grid(row=1, column=1, sticky=w, pady=4, padx=5)

        ttk.Label(frm_opts, text=개별 1칸 높이).grid(
            row=1, column=2, sticky=w, pady=4, padx=(15, 0)
        )
        self.ent_h = ttk.Entry(frm_opts, width=10)
        self.ent_h.insert(0, 15)
        self.ent_h.grid(row=1, column=3, sticky=w, pady=4, padx=5)

        ttk.Label(frm_opts, text=라벨 간 가로 간격).grid(
            row=2, column=0, sticky=w, pady=4
        )
        self.ent_gx = ttk.Entry(frm_opts, width=10)
        self.ent_gx.insert(0, 20)
        self.ent_gx.grid(row=2, column=1, sticky=w, pady=4, padx=5)

        ttk.Label(frm_opts, text=라벨 간 세로 간격).grid(
            row=2, column=2, sticky=w, pady=4, padx=(15, 0)
        )
        self.ent_gy = ttk.Entry(frm_opts, width=10)
        self.ent_gy.insert(0, 20)
        self.ent_gy.grid(row=2, column=3, sticky=w, pady=4, padx=5)

        chk_autofit = ttk.Checkbutton(
            frm_opts,
            text=글자가 길면 박스 폭에 맞춰 자동 축소압축 (Auto-Fit),
            variable=self.auto_fit_var,
        )
        chk_autofit.grid(
            row=3, column=0, columnspan=4, sticky=w, pady=(6, 2)
        )

        # 3. 폰트 및 색상 설정
        frm_style = ttk.LabelFrame(
            self.root, text= 3. 글꼴(폰트) 및 도면 색상 설정 , padding=10
        )
        frm_style.pack(fill=x, padx=15, pady=4)

        ttk.Label(frm_style, text=글꼴(폰트) 스타일).grid(
            row=0, column=0, sticky=w, pady=4
        )
        self.cb_font = ttk.Combobox(
            frm_style,
            values=list(CAD_FONTS.keys()),
            state=readonly,
            width=25,
        )
        self.cb_font.current(0)
        self.cb_font.grid(
            row=0, column=1, columnspan=2, sticky=w, pady=4, padx=5
        )

        ttk.Label(frm_style, text=사각형 테두리 색상).grid(
            row=1, column=0, sticky=w, pady=4
        )
        self.cb_box_color = ttk.Combobox(
            frm_style,
            values=list(CAD_COLORS.keys()),
            state=readonly,
            width=25,
        )
        self.cb_box_color.current(4)
        self.cb_box_color.grid(
            row=1, column=1, columnspan=2, sticky=w, pady=4, padx=5
        )

        ttk.Label(frm_style, text=문자(텍스트) 색상).grid(
            row=2, column=0, sticky=w, pady=4
        )
        self.cb_text_color = ttk.Combobox(
            frm_style,
            values=list(CAD_COLORS.keys()),
            state=readonly,
            width=25,
        )
        self.cb_text_color.current(2)
        self.cb_text_color.grid(
            row=2, column=1, columnspan=2, sticky=w, pady=4, padx=5
        )

        # 4. 변환 버튼
        btn_run = tk.Button(
            self.root,
            text=CAD (.DXF) 도면 생성하기,
            bg=#2B579A,
            fg=white,
            font=(맑은 고딕, 11, bold),
            height=2,
            command=self.on_generate,
        )
        btn_run.pack(fill=x, padx=15, pady=10)

    def on_browse(self)
        file = filedialog.askopenfilename(
            title=엑셀 파일 선택,
            filetypes=[(Excel Files, .xlsx .xls)],
        )
        if file
            self.excel_path.set(file)

    def on_generate(self)
        path = self.excel_path.get().strip()
        if not path or not os.path.exists(path)
            messagebox.showerror(오류, 엑셀 파일을 먼저 선택해 주세요.)
            return

        try
            w = float(self.ent_w.get())
            h = float(self.ent_h.get())
            gx = float(self.ent_gx.get())
            gy = float(self.ent_gy.get())
            cols = int(self.ent_cols.get())
            scale = float(self.ent_font_scale.get())
            auto_fit = self.auto_fit_var.get()

            font_key = self.cb_font.get()
            box_col_num = CAD_COLORS.get(self.cb_box_color.get(), 7)
            text_col_num = CAD_COLORS.get(self.cb_text_color.get(), 7)
        except ValueError
            messagebox.showerror(
                오류, 모든 규격 설정값은 숫자로 입력해야 합니다.
            )
            return

        out_file = filedialog.asksaveasfilename(
            title=CAD 도면 저장 (.dxf),
            defaultextension=.dxf,
            filetypes=[(AutoCAD DXF, .dxf)],
        )
        if not out_file
            return

        try
            dxf_content, count = generate_dxf_string(
                path,
                w,
                h,
                gx,
                gy,
                cols,
                scale,
                auto_fit,
                font_key,
                box_col_num,
                text_col_num,
            )
            if count == 0
                messagebox.showwarning(
                    경고,
                    엑셀 파일에서 유효한 문자 데이터를 찾지 못했습니다.,
                )
                return

            with open(out_file, w, encoding=cp949, errors=replace) as f
                f.write(dxf_content)

            messagebox.showinfo(
                완료,
                f총 {count}개의 라벨이 자동 생성되었습니다!nn저장
                f 경로n{out_file},
            )
        except Exception as e
            messagebox.showerror(
                오류 발생, f도면 생성 중 오류가 발생했습니다n{str(e)}
            )


if __name__ == __main__
    root = tk.Tk()
    app = App(root)
    root.mainloop()