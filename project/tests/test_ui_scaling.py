"""Tk scaling simulations, not an assertion about Windows display settings."""
import gc
from pathlib import Path
import sys
import tempfile
import time
import unittest

from tkinterdnd2 import TkinterDnD
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from label_ui import App


class ScalingTests(unittest.TestCase):
    def assert_top_edges_aligned(self, app):
        file_frame = app.drop_area.master
        drop_right = app.drop_area.winfo_x() + app.drop_area.winfo_width()
        self.assertLessEqual(abs(file_frame.winfo_width() - drop_right), 1)
        last_button = file_frame.grid_slaves(row=1, column=4)[0]
        self.assertLessEqual(abs(drop_right - last_button.winfo_x() - last_button.winfo_width()), 1)
        trailing = app.help_button if app._narrow else app.update_frame
        header_gap = app.header.winfo_width() - trailing.winfo_x() - trailing.winfo_width()
        self.assertLessEqual(header_gap, 5)

    def assert_visible(self, widget, window):
        self.assertTrue(widget.winfo_ismapped(), str(widget))
        self.assertGreater(widget.winfo_width(), 4)
        self.assertGreater(widget.winfo_height(), 4)
        self.assertGreaterEqual(widget.winfo_rootx(), window.winfo_rootx())
        self.assertGreaterEqual(widget.winfo_rooty(), window.winfo_rooty())
        self.assertLessEqual(widget.winfo_rootx() + widget.winfo_width(), window.winfo_rootx() + window.winfo_width())
        self.assertLessEqual(widget.winfo_rooty() + widget.winfo_height(), window.winfo_rooty() + window.winfo_height())

    def check_scale(self, percent):
        gc.collect()
        with tempfile.TemporaryDirectory() as folder:
            root = TkinterDnD.Tk()
            root.tk.call("tk", "scaling", 4 / 3 * percent / 100)
            errors = []
            root.report_callback_exception = lambda *args: errors.append(args)
            try:
                app = App(root, check_updates=False, settings_dir=Path(folder))
                root.geometry("640x420+10+10")
                root.update()
                self.assert_top_edges_aligned(app)
                for width in (round(1120 * percent / 100), round(640 * percent / 100)):
                    root.geometry(f"{width}x{round(540 * percent / 100)}")
                    root.update()
                    self.assert_top_edges_aligned(app)
                root.geometry("640x420")
                root.update()
                app.apply_rows(None, (("AAA", "", "CCC"), ("DDD", "EEE")))
                deadline = time.monotonic() + 4
                while (app.busy or app.debounce_id) and time.monotonic() < deadline:
                    root.update()
                    time.sleep(.003)
                self.assertFalse(app.busy or app.debounce_id)
                app.select_table_all()
                root.update()
                for widget in (app.data_tree, app.add_button, app.edit_button, app.run_button,
                               app.settings_button, app.help_button, app.update_frame, app.updates.frame, app.updates.button):
                    self.assert_visible(widget, root)
                self.assertGreater(app.data_tree.winfo_height(), 55 * percent / 100)
                self.assertLess(app.heading_label.winfo_rootx() + app.heading_label.winfo_width(), app.settings_button.winfo_rootx())
                app.add_row()
                editor = app.editor
                editor.geometry(f"{round(680 * percent / 100)}x{round(520 * percent / 100)}+20+20")
                root.update()
                grid = editor.grid
                grid.paste_text("A\tB\tC\nD\tE\tF\nG\tH\tI\nJ\tK\tL\nM\tN\tO\nP\tQ\tR")
                root.update()
                r, c = grid.active
                self.assertTrue(grid.row_offset <= r < grid.row_offset + grid.visible()[0])
                self.assertTrue(grid.col_offset <= c < grid.col_offset + grid.visible()[1])
                editor.geometry("480x360")
                root.update()
                self.assert_visible(grid.canvas, editor)
                self.assert_visible(editor.apply_button, editor)
                self.assertGreaterEqual(grid.canvas.winfo_height(), grid.header_h + grid.cell_h + 2)
                self.assertGreaterEqual(grid.canvas.winfo_width(), grid.header_w + grid.cell_w + 2)
                r, c = grid.active
                self.assertTrue(grid.row_offset <= r < grid.row_offset + grid.visible()[0])
                self.assertTrue(grid.col_offset <= c < grid.col_offset + grid.visible()[1])
                # The full preview grows after selecting a populated row. Resize
                # while a native cell editor is open must keep it at that cell.
                editor.geometry(f"{round(680 * percent / 100)}x{round(520 * percent / 100)}")
                root.update()
                grid.select(5, 2)
                grid.begin_edit()
                editor.geometry("480x360")
                root.update()
                self.assert_visible(grid.entry, editor)
                self.assertLessEqual(grid.entry.winfo_y() + grid.entry.winfo_height(), grid.canvas.winfo_height())
                self.assertFalse(errors)
                editor.destroy()
            finally:
                root.destroy()

    def test_100_percent_minimum_window(self):
        self.check_scale(100)

    def test_150_percent_minimum_window_and_active_cell_after_preview_resize(self):
        self.check_scale(150)

    def test_200_percent_minimum_window_and_active_cell_after_preview_resize(self):
        self.check_scale(200)


if __name__ == "__main__":
    unittest.main()
