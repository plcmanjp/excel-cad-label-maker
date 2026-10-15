"""Visible source-app QC with isolated settings and read-only state evidence."""
import argparse
import ctypes
import json
from pathlib import Path
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "project/src"))
from tkinterdnd2 import TkinterDnD
from label_ui import App


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True, type=Path)
    parser.add_argument("--scale", type=float)
    parser.add_argument("--geometry", default="1120x760+40+40")
    parser.add_argument("--input", type=Path, help="Optional programmatic preload; not physical file-open evidence")
    args = parser.parse_args()
    directory = args.directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    root = TkinterDnD.Tk()
    if args.scale:
        root.tk.call("tk", "scaling", args.scale)
    app = App(root, settings_dir=directory / "settings", check_updates=False)
    root.geometry(args.geometry)
    last = [None]

    def exception(*info):
        with (directory / "exceptions.log").open("a", encoding="utf-8") as stream:
            traceback.print_exception(*info, file=stream)

    root.report_callback_exception = exception

    def observe():
        if app.closed:
            return
        def bounds(widget):
            return {"geometry": widget.winfo_geometry(), "x": widget.winfo_rootx(), "y": widget.winfo_rooty(),
                    "width": widget.winfo_width(), "height": widget.winfo_height(),
                    "requested": [widget.winfo_reqwidth(), widget.winfo_reqheight()],
                    "mapped": bool(widget.winfo_ismapped()), "manager": widget.winfo_manager()}
        state = {"status": app.status.get(), "summary": app.summary.get(), "busy": app.busy,
                 "revision": app.edit_revision, "rendered_revision": app.rendered_edit_revision,
                 "labels": [list(label.texts) for label in app.analysis.labels[:30]] if app.analysis else [],
                 "label_count": len(app.analysis.labels) if app.analysis else 0,
                 "layout_cells": len(app.layout.cells) if app.layout else 0,
                 "geometry": root.winfo_geometry(), "minimum_size": root.minsize(),
                 "tk_scaling": float(root.tk.call("tk", "scaling")),
                 "screen": [root.winfo_screenwidth(), root.winfo_screenheight()],
                 "header": {name: bounds(widget) for name, widget in
                            (("header", app.header), ("update_outer", app.update_frame),
                             ("update_inner", app.updates.frame), ("update_button", app.updates.button),
                             ("help", app.help_button))},
                 "file_area": {"frame": bounds(app.drop_area.master), "drop": bounds(app.drop_area),
                               "last_button": bounds(app.drop_area.master.grid_slaves(row=1, column=4)[0])},
                 "os_dpi": ctypes.windll.user32.GetDpiForWindow(root.winfo_id())}
        editor = app.editor
        if editor and editor.winfo_exists() and hasattr(editor, "grid"):
            grid = editor.grid
            state["editor"] = {"shape": grid.model.shape, "active": grid.active, "selection": grid.selection,
                               "rows": [list(row) for row in grid.model.rows[:30]],
                               "editing": grid.editing, "entry": grid.entry.get(),
                               "geometry": editor.winfo_geometry(), "canvas_items": len(grid.canvas.find_all()),
                               "viewport": {"offset": [grid.row_offset, grid.col_offset], "visible": grid.visible(),
                                            "active_visible": grid.row_offset <= grid.active[0] < grid.row_offset + grid.visible()[0]
                                            and grid.col_offset <= grid.active[1] < grid.col_offset + grid.visible()[1]},
                               "error": editor.error.cget("text"), "preview": editor.preview.cget("text")}
        encoded = json.dumps(state, ensure_ascii=False, indent=2) + "\n"
        if encoded != last[0]:
            (directory / "state.json").write_text(encoded, encoding="utf-8")
            last[0] = encoded
        root.after(300, observe)

    root.after(300, observe)
    if args.input:
        root.after(100, lambda: app.select_file(args.input.resolve()))
    root.mainloop()


if __name__ == "__main__":
    main()
