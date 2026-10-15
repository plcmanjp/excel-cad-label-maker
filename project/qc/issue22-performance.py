"""Bounded spreadsheet/layout measurements using synthetic data and isolated Tk."""
import argparse
import json
from pathlib import Path
import platform
import sys
import time
import tkinter as tk

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "project/src"))
from converter import LabelSettings, compute_layout, drawing_from_layout, save_drawing
from spreadsheet import SpreadsheetGrid
from spreadsheet_data import GridModel, MAX_CELLS, normalize_rows, parse_tsv, serialize_tsv
import ezdxf


def measure(count, directory):
    rows = tuple((f"L{i:05}", "", "한글001") for i in range(count))
    stamp = time.perf_counter()
    tsv = serialize_tsv(rows)
    parsed = parse_tsv(tsv)
    parsed_at = time.perf_counter()
    model = GridModel()
    model.paste(0, 0, parsed)
    pasted_at = time.perf_counter()
    model.paste(count // 2, 0, (("수정",),))
    edited_at = time.perf_counter()
    assert model.undo() and model.rows == rows
    assert model.undo() and model.rows == (("",),)
    assert model.redo() and model.rows == rows
    history_at = time.perf_counter()
    before = model.rows
    try:
        model.paste(MAX_CELLS, 0, (("overflow",),))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected capacity refusal")
    assert model.rows == before
    refused_at = time.perf_counter()
    layout = compute_layout(normalize_rows(rows), LabelSettings())
    layout_at = time.perf_counter()
    assert len(layout.label_bounds) == count and len(layout.cells) == count * 3
    root = tk.Tk()
    root.geometry("800x520+20+20")
    grid = SpreadsheetGrid(root, rows=rows)
    grid.pack(fill="both", expand=True)
    root.update()
    canvas_items = len(grid.canvas.find_all())
    assert canvas_items < 1000
    grid.select(count - 1, 2)
    root.update()
    assert grid.active == (count - 1, 2)
    drawn_at = time.perf_counter()
    root.destroy()
    output = directory / f"labels-{count}.dxf"
    save_drawing(drawing_from_layout(layout), output)
    doc = ezdxf.readfile(output)
    assert not doc.audit().has_errors
    text_entities = list(doc.modelspace().query("TEXT"))
    # DXF preserves geometry for blank slots; blank TEXT handling is engine-owned.
    nonempty = [entity.dxf.text for entity in text_entities if entity.dxf.text]
    assert len(nonempty) == count * 2
    assert nonempty[:2] == ["L00000", "한글001"]
    return {"rows": count, "cells": count * 3, "tsv_roundtrip_seconds": parsed_at - stamp,
            "paste_seconds": pasted_at - parsed_at, "single_edit_seconds": edited_at - pasted_at,
            "undo_redo_seconds": history_at - edited_at, "capacity_refusal_seconds": refused_at - history_at,
            "layout_seconds": layout_at - refused_at, "grid_start_scroll_seconds": drawn_at - layout_at,
            "visible_canvas_items": canvas_items, "dxf_nonempty_texts": len(nonempty), "dxf_audit_errors": 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    args.directory.mkdir(parents=True, exist_ok=True)
    result = {"python": platform.python_version(), "platform": platform.platform(),
              "scope": "Synthetic model transactions, source Tk viewport and DXF reread; not OS input latency",
              "samples": [measure(count, args.directory) for count in (1000, 10000)]}
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
