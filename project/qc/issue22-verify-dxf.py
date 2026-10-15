"""Compare a GUI-saved synthetic DXF to row data and the default preview layout."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import ezdxf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "project/src"))
from converter import LabelSettings, compute_layout
from spreadsheet_data import normalize_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", required=True, type=Path, help="JSON array of synthetic string rows")
    parser.add_argument("--dxf", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    rows = normalize_rows(json.loads(args.rows.read_text(encoding="utf-8")))
    layout = compute_layout(rows, LabelSettings())
    document = ezdxf.readfile(args.dxf)
    audit = document.audit()
    outlines = list(document.modelspace().query("LWPOLYLINE"))
    texts = list(document.modelspace().query("TEXT"))
    assert len(outlines) == len(texts) == len(layout.cells)
    assert [text.dxf.text for text in texts] == [value for row in rows for value in row]
    for outline, text, cell in zip(outlines, texts, layout.cells):
        assert tuple((float(x), float(y)) for x, y, *_ in outline.get_points()) == cell.corners
        assert tuple(text.dxf.align_point)[:2] == cell.center
        assert text.dxf.height == cell.text_height
        assert text.dxf.width == cell.width_factor
    assert not audit.errors and not audit.fixes
    report = {"status": "PASS", "labels": len(rows), "cells": len(layout.cells),
              "blank_cells": sum(not value for row in rows for value in row),
              "text_and_geometry_match": True, "audit_errors": 0, "audit_fixes": 0,
              "settings": "default 60x15 mm cells, 5 labels per row, 20 mm gaps",
              "dxf_bytes": args.dxf.stat().st_size,
              "dxf_sha256": hashlib.sha256(args.dxf.read_bytes()).hexdigest()}
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
