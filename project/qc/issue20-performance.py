"""Synthetic, isolated baseline/candidate measurements for Issue 20."""
import argparse
import ctypes as ct
from ctypes import wintypes as wt
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import platform
from statistics import median
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "project/src"))


class MemoryCounters(ct.Structure):
    _fields_ = [("cb", wt.DWORD), ("faults", wt.DWORD)] + [(name, ct.c_size_t) for name in
                ("peak_rss", "rss", "peak_paged", "paged", "peak_nonpaged", "nonpaged", "pagefile", "peak_pagefile")]


def memory():
    kernel = ct.WinDLL("kernel32")
    kernel.GetCurrentProcess.restype = wt.HANDLE
    psapi = ct.WinDLL("psapi")
    psapi.GetProcessMemoryInfo.argtypes = [wt.HANDLE, ct.POINTER(MemoryCounters), wt.DWORD]
    counters = MemoryCounters()
    counters.cb = ct.sizeof(counters)
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ct.byref(counters), counters.cb):
        raise OSError("memory probe failed")
    return {"working_set_bytes": counters.rss, "peak_working_set_bytes": counters.peak_rss}


def fixture(path, labels, separated=True):
    from openpyxl import Workbook
    book = Workbook(write_only=True)
    sheet = book.create_sheet("synthetic")
    for index in range(labels):
        for text in (f"L{index:05}", "전원", "001"):
            sheet.append([text])
        if separated:
            sheet.append([None])
    book.save(path)
    book.close()


def baseline_module(path):
    spec = importlib.util.spec_from_file_location("issue20_baseline", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def worker(args):
    if args.mode == "baseline":
        engine = baseline_module(Path(args.directory) / "baseline-converter.py")
    else:
        import converter as engine
        from input_model import analyze, read_workbook
    path = Path(args.directory) / f"labels-{args.labels}.xlsx"
    before = memory()
    start = time.perf_counter()
    if args.mode == "baseline":
        blocks = engine.extract_blocks_auto(path)
        parsed = time.perf_counter()
        layout_seconds = None
        doc = engine.create_drawing(blocks, engine.LabelSettings())
    else:
        source = read_workbook(path)
        read_end = time.perf_counter()
        analysis = analyze(source)
        blocks = analysis.blocks
        parsed = time.perf_counter()
        layout = engine.compute_layout(blocks, engine.LabelSettings())
        layout_end = time.perf_counter()
        layout_seconds = layout_end - parsed
        doc = engine.drawing_from_layout(layout)
    created = time.perf_counter()
    output = Path(args.directory) / f"{args.mode}-{args.labels}-{os.getpid()}.dxf"
    engine.save_drawing(doc, output)
    saved = time.perf_counter()
    after = memory()
    import ezdxf
    reread = ezdxf.readfile(output)
    texts = list(reread.modelspace().query("TEXT"))
    assert len(blocks) == args.labels and len(texts) == args.labels * 3
    assert reread.dxfversion == "AC1024" and reread.units == ezdxf.units.MM
    assert not reread.audit().has_errors
    result = {"mode": args.mode, "labels": args.labels, "cells": len(texts), "read_and_analyze_seconds": parsed - start,
              "drawing_seconds": created - parsed, "preview_layout_seconds": layout_seconds,
              "save_seconds": saved - created, "total_seconds": saved - start,
              "memory_before": before, "memory_after": after, "dxf_audit_errors": 0}
    if args.mode == "candidate":
        result.update(read_seconds=read_end - start, analysis_seconds=parsed - read_end)
    print(json.dumps(result))


def ui_probe(directory, path, cancel=False):
    from tkinterdnd2 import TkinterDnD
    from label_ui import App
    root = TkinterDnD.Tk()
    app = App(root, check_updates=False, settings_dir=directory / "probe-settings")
    app.tabs.select(app.preview)
    root.update_idletasks()
    gaps, last_tick = [], [time.perf_counter()]
    tick_id = [None]
    def tick():
        now = time.perf_counter()
        gaps.append(now - last_tick[0])
        last_tick[0] = now
        if not app.closed:
            tick_id[0] = root.after(10, tick)
    tick_id[0] = root.after(10, tick)
    start = time.perf_counter()
    app.select_file(path)
    cancel_time = None
    while app.busy and time.perf_counter() - start < 30:
        root.update()
        if cancel and cancel_time is None and time.perf_counter() - start >= .1:
            cancel_time = time.perf_counter()
            app.cancel()
        time.sleep(.001)
    root.update()
    done = time.perf_counter()
    if app.busy:
        raise AssertionError("UI probe timeout")
    result = {"scope": "visible source Tk event loop, programmatic file selection, not physical-input acceptance", "cancel_requested": cancel,
              "elapsed_seconds": done - start, "max_heartbeat_gap_seconds": max(gaps, default=0),
              "cancel_to_terminal_seconds": done - cancel_time if cancel_time else None,
              "labels": len(app.analysis.labels) if app.analysis else None}
    if not cancel:
        draw_start = time.perf_counter()
        app.preview.draw()
        result["viewport_draw_seconds"] = time.perf_counter() - draw_start
        result["canvas_items"] = len(app.preview.canvas.find_all())
        assert result["canvas_items"] > 0
    if tick_id[0]:
        root.after_cancel(tick_id[0])
    app.shutdown()
    root.destroy()
    return result


def main(args):
    directory = Path(args.directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    raw = subprocess.check_output(["git", "show", args.baseline_ref + ":project/src/converter.py"], cwd=ROOT)
    (directory / "baseline-converter.py").write_bytes(raw)
    for labels in (20, 1000, 10000):
        fixture(directory / f"labels-{labels}.xlsx", labels)
    fixture(directory / "single-long-label.xlsx", 10000, separated=False)
    samples = []
    env = {**os.environ, "PYTHONUTF8": "1"}
    for labels in (1000, 10000):
        for _ in range(3):
            for mode in ("baseline", "candidate"):
                result = subprocess.check_output([sys.executable, "-B", __file__, "--worker", "--mode", mode,
                                                  "--labels", str(labels), "--directory", str(directory)], cwd=ROOT, env=env, timeout=90)
                sample = json.loads(result)
                samples.append(sample)
                print(f"measured {mode} {labels}: {sample['total_seconds']:.3f}s", flush=True)
    medians = []
    for labels in (1000, 10000):
        for mode in ("baseline", "candidate"):
            relevant = [sample for sample in samples if sample["labels"] == labels and sample["mode"] == mode]
            medians.append({"mode": mode, "labels": labels,
                            **{key: median(s[key] for s in relevant) for key in ("read_and_analyze_seconds", "drawing_seconds", "save_seconds", "total_seconds")},
                            "median_peak_working_set_bytes": median(s["memory_after"]["peak_working_set_bytes"] for s in relevant)})
    ui = {
        "labels_1000": ui_probe(directory, directory / "labels-1000.xlsx"),
        "labels_10000": ui_probe(directory, directory / "labels-10000.xlsx"),
        "single_30000_cells": ui_probe(directory, directory / "single-long-label.xlsx"),
        "cancel_10000": ui_probe(directory, directory / "labels-10000.xlsx", cancel=True),
    }
    report = {"schema_version": 1, "python": platform.python_version(), "windows": platform.platform(), "baseline_ref": args.baseline_ref,
              "baseline_converter_sha256": sha256(raw).hexdigest(), "repeats": 3,
              "conditions": "Alternating fresh processes; same synthetic fixtures; OS cache not flushed; peak working set includes imports and conversion, before DXF readback",
              "samples": samples, "medians": medians, "ui_event_loop": ui,
              "fixtures": {path.name: sha256(path.read_bytes()).hexdigest() for path in directory.glob("*.xlsx")}}
    Path(args.report).write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"medians": medians, "ui_event_loop": ui}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    parser.add_argument("--report", default="project/qc/issue20-performance.json")
    parser.add_argument("--baseline-ref", default="d8fa53c07ed1fc198e2e8b4beadf1996be50d3f5")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--mode", choices=("baseline", "candidate"))
    parser.add_argument("--labels", type=int)
    arguments = parser.parse_args()
    worker(arguments) if arguments.worker else main(arguments)
