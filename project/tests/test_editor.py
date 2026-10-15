"""Working data protection, modal transactions and Excel-free export."""
from pathlib import Path
import gc
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from threading import Event

import ezdxf
from openpyxl import Workbook
from tkinterdnd2 import TkinterDnD
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from label_ui import App
from label_editor import LabelEditor
from converter import LabelSettings
from input_model import Analysis, Diagnostic, InputOptions, Label
from working_data import apply_edits, edited_label, parse_label_text


class WorkingDataTests(unittest.TestCase):
    def test_literal_text_preserves_zeros_and_spaces_and_refuses_empty_controls(self):
        self.assertEqual(parse_label_text("001\r\n 한글 ABC "), ("001", " 한글 ABC "))
        self.assertEqual(parse_label_text("a\n\nB\n"), ("a", "", "B"))
        for value in ("", "a\tB", "a\x00B", "a\x7fB"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_label_text(value)

    def test_overlay_keeps_original_and_unresolved_errors(self):
        original = Label(("OLD",), ("A1",))
        base = Analysis(None, InputOptions(), "A1:A2", (original,),
                        (Diagnostic("warning", "format", "format warning", "A1", 0),
                         Diagnostic("error", "error", "unresolved", "A2")))
        changed = apply_edits(base, [(0, edited_label(("NEW", "001"), original))], [edited_label(("ADD",))])
        self.assertEqual(base.labels, (original,))
        self.assertEqual(changed.blocks, (("NEW", "001"), ("ADD",)))
        self.assertEqual(len(changed.errors), 1)
        self.assertEqual(len(changed.diagnostics), 1)
        self.assertEqual(changed.labels[0].addresses, ("A1", "직접 입력"))

    def test_capacity_and_stale_target_are_refused(self):
        base = Analysis(None, InputOptions(), "직접 입력", (edited_label(("a",)),), ())
        with self.assertRaises(ValueError):
            apply_edits(base, [(4, edited_label(("b",)))])
        with patch("working_data.MAX_CELLS", 1), self.assertRaises(ValueError):
            apply_edits(base, additions=(edited_label(("b",)),))


class EditorUiTests(unittest.TestCase):
    def setUp(self):
        # Retire previous Tk fixture cycles on their owner thread before workers.
        gc.collect()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.file = self.folder / "synthetic.xlsx"
        book = Workbook()
        for row in (("FIRST", "001"), (None,), (None,), ("SECOND",)):
            book.active.append(row)
        book.save(self.file)
        book.close()
        self.root = TkinterDnD.Tk()
        self.root.withdraw()
        self.errors = []
        self.root.report_callback_exception = lambda *args: self.errors.append(args)
        self.addCleanup(self.root.destroy)
        self.app = App(self.root, check_updates=False, settings_dir=self.folder / "settings")

    def pump(self):
        until = time.monotonic() + 5
        while time.monotonic() < until:
            self.root.update()
            if not self.app.busy and self.app.debounce_id is None:
                self.assertFalse(self.errors)
                return
            time.sleep(.003)
        self.fail("job timed out: " + self.app.status.get())

    def apply_editor(self, text):
        editor = self.app.editor
        self.assertIsInstance(editor, LabelEditor)
        editor.grid.model._commit((tuple(text.split("\n")),))
        editor.grid.changed()
        editor.apply()
        self.pump()

    def test_defaults_header_help_and_empty_start(self):
        settings = self.app.parse_settings()
        self.assertEqual((settings.font_key, settings.box_color, settings.text_color), ("Arial", 7, 7))
        self.assertEqual(LabelSettings().box_color, 7)
        self.assertEqual(str(self.app.add_button.cget("state")), "normal")
        self.assertEqual(self.app.data_tree.get_children(), ())
        self.assertFalse(hasattr(self.app, "detail_button"))
        self.assertEqual(self.app.update_frame.master.winfo_class(), "TFrame")
        self.app.show_help()
        dialog = self.app.editor
        self.assertTrue(self.app.modal_open)
        def texts(widget):
            result = []
            for child in widget.winfo_children():
                if child.winfo_class() == "TLabel":
                    result.append(child.cget("text"))
                result.extend(texts(child))
            return result
        combined = "\n".join(texts(dialog))
        self.assertIn("원개발자: 직장인", combined)
        self.assertIn("Fork 및 후속 개발: plcmanjp", combined)
        dialog.destroy()
        self.assertFalse(self.app.modal_open)

    def test_add_edit_and_export_without_excel(self):
        self.app.add_row()
        self.apply_editor("MANUAL\n001\n한글")
        self.assertIsNone(self.app.snapshot)
        self.assertEqual(self.app.analysis.blocks, (("MANUAL", "001", "한글"),))
        self.app.select_label(0)
        self.app.edit_selected()
        self.apply_editor("EDITED\n001")
        self.app.add_row()
        self.apply_editor("NEXT")
        self.assertEqual(self.app.analysis.blocks, (("EDITED", "001"), ("NEXT",)))
        self.assertEqual(self.app.analysis.cell_count, 3)
        output = self.folder / "manual.dxf"
        with patch("excel_cad_label.filedialog.asksaveasfilename", return_value=str(output)):
            self.app.on_generate()
            self.pump()
        doc = ezdxf.readfile(output)
        self.assertEqual([e.dxf.text for e in doc.modelspace().query("TEXT")], ["EDITED", "001", "NEXT"])
        self.assertEqual(doc.layers.get("TEXT_DATA").dxf.color, 7)
        self.assertFalse(self.app.unsaved_edits)

    def test_import_edit_add_style_preserves_source_and_reuses_editor(self):
        before = self.file.read_bytes()
        self.app.select_file(self.file)
        self.pump()
        self.app.select_label(0)
        self.app.edit_selected()
        self.apply_editor("CHANGED\n001\nEXTRA")
        self.app.add_row()
        self.apply_editor("APPENDED")
        self.app.vars["cell_w"].set("75")
        self.pump()
        self.assertEqual(self.app.analysis.blocks, (("CHANGED", "001", "EXTRA"), ("SECOND",), ("APPENDED",)))
        self.assertEqual(self.app.analysis.labels[0].origin, "edited")
        self.assertEqual(self.file.read_bytes(), before)
        self.assertEqual(self.app.layout.settings.cell_w, 75)
        self.assertIn("(수정)", self.app.data_tree.item("0", "values")[3])

    def test_cancel_validation_and_modal_shortcuts_leave_data_unchanged(self):
        self.app.add_row()
        self.app.editor.grid.paste_text("cancel me")
        with patch("excel_cad_label.filedialog.askopenfilename") as browse:
            self.app._shortcut(self.app.on_browse)
            self.app.select_file(self.file)
            browse.assert_not_called()
        self.app.editor.destroy()
        self.assertFalse(self.app.has_edits)
        self.app.add_row()
        editor = self.app.editor
        editor.grid.model._commit((("",),))
        editor.apply()
        self.assertTrue(editor.winfo_exists())
        self.assertIn("입력", editor.error.cget("text"))
        self.assertFalse(self.app.has_edits)
        editor.destroy()
        self.assertEqual(self.app.updates._defer_depth, 0)

    def test_discard_decline_and_corrupt_replacement_keep_working_data(self):
        self.app.select_file(self.file)
        self.pump()
        self.app.select_label(0)
        self.app.edit_selected()
        self.apply_editor("KEEP")
        blocks = self.app.analysis.blocks
        with patch("excel_cad_label.messagebox.askyesno", return_value=False):
            self.app.clear_file()
            self.app.reload()
            self.app.close()
        self.assertTrue(self.root.winfo_exists())
        self.assertEqual(self.app.analysis.blocks, blocks)
        corrupt = self.folder / "corrupt.xlsx"
        corrupt.write_bytes(b"not an excel workbook")
        with patch("excel_cad_label.messagebox.askyesno", return_value=True):
            self.app.select_file(corrupt)
            self.pump()
        self.assertEqual(self.app.analysis.blocks, blocks)
        self.assertEqual(self.app.snapshot.path, self.file.resolve())

    def test_reload_after_dxf_save_still_requires_discard_confirmation(self):
        self.app.select_file(self.file)
        self.pump()
        self.app.select_label(0)
        self.app.edit_selected()
        self.apply_editor("KEEP")
        with patch("excel_cad_label.filedialog.asksaveasfilename", return_value=str(self.folder / "saved.dxf")):
            self.app.on_generate()
            self.pump()
        self.assertFalse(self.app.unsaved_edits)
        with patch("excel_cad_label.messagebox.askyesno", return_value=False) as confirm:
            self.app.reload()
        confirm.assert_called_once()
        self.assertEqual(self.app.analysis.blocks[0], ("KEEP",))

    def test_cancel_before_range_rebuild_preserves_edits(self):
        self.app.select_file(self.file)
        self.pump()
        self.app.select_label(0)
        self.app.edit_selected()
        self.apply_editor("KEEP")
        with patch("excel_cad_label.messagebox.askyesno", return_value=True):
            self.app.cell_range.set("A4:A4")
        self.assertIsNotNone(self.app.debounce_id)
        self.app.cancel()
        self.assertIsNone(self.app.debounce_id)
        self.assertEqual(self.app.cell_range.get(), "")
        until = time.monotonic() + .4
        while time.monotonic() < until:
            self.root.update()
            time.sleep(.005)
        self.assertEqual(self.app.analysis.blocks[0], ("KEEP",))
        self.assertTrue(self.app.has_edits)

    def test_preset_mode_decline_keeps_edits_and_rebuilds_new_geometry(self):
        self.app.select_file(self.file)
        self.pump()
        self.app.select_label(0)
        self.app.edit_selected()
        self.apply_editor("KEEP")
        values = {**self.app.values(), "mode": "display", "cell_w": 81}
        with patch("excel_cad_label.messagebox.askyesno", return_value=False):
            self.app.apply_values(values)
        self.pump()
        self.assertEqual(self.app.analysis.options.mode, "legacy")
        self.assertEqual(self.app.analysis.blocks[0], ("KEEP",))
        self.assertEqual(self.app.layout.settings.cell_w, 81)
        self.assertTrue(self.app.current_matches())

    def test_native_update_feedback_uses_shared_modal_guard(self):
        from update_check import UpdateResult
        self.app.updates.checker = lambda version: UpdateResult("unavailable")
        def show(*args, **kwargs):
            self.assertTrue(self.app.modal_open)
            self.app.on_browse()
            self.app.on_generate()
        with patch("update_notice.messagebox.showinfo", side_effect=show), patch("excel_cad_label.filedialog.askopenfilename") as browse:
            self.app.updates.check(manual=True)
            until = time.monotonic() + 2
            while self.app.updates._active and time.monotonic() < until:
                self.root.update()
                time.sleep(.005)
            self.assertFalse(self.app.updates._active)
            browse.assert_not_called()
        self.assertFalse(self.app.modal_open)

    def test_input_options_discard_is_transactional_and_cancel_restores_values(self):
        self.app.select_file(self.file)
        self.pump()
        self.app.select_label(0)
        self.app.edit_selected()
        self.apply_editor("KEEP")
        with patch("excel_cad_label.messagebox.askyesno", return_value=False):
            self.app.cell_range.set("A4:A4")
        self.assertEqual(self.app.cell_range.get(), "")
        self.assertEqual(self.app.analysis.blocks[0], ("KEEP",))
        with patch("excel_cad_label.messagebox.askyesno", return_value=True):
            self.app.cell_range.set("A4:A4")
            self.assertTrue(self.app.has_edits)
            self.pump()
        self.assertFalse(self.app.has_edits)
        self.assertEqual(self.app.analysis.blocks, (("SECOND",),))

    def test_failed_or_cancelled_edit_layout_cannot_save_old_revision(self):
        self.app.add_row()
        self.apply_editor("ONE")
        self.app.add_row()
        started, release = Event(), Event()
        import label_ui
        actual = label_ui.compute_layout
        def delayed(*args):
            started.set()
            release.wait(3)
            return actual(*args)
        with patch("label_ui.compute_layout", side_effect=delayed):
            self.app.editor.grid.paste_text("TWO")
            self.app.editor.apply()
            until = time.monotonic() + 2
            while not started.is_set() and time.monotonic() < until:
                self.root.update()
                time.sleep(.005)
            self.assertTrue(started.is_set())
            self.app.cancel()
            release.set()
            self.pump()
        self.assertFalse(self.app.current_matches())
        self.assertEqual(str(self.app.run_button.cget("state")), "disabled")
        self.app.vars["cell_w"].set("61")
        self.pump()
        self.assertEqual(self.app.analysis.blocks, (("ONE",), ("TWO",)))

    def test_real_double_click_target_opens_complete_editor(self):
        self.app.select_file(self.file)
        self.pump()
        self.root.deiconify()
        self.root.update()
        x, y, width, height = self.app.data_tree.bbox("0")
        self.app.edit_from_table(SimpleNamespace(x=x + 10, y=y + height // 2))
        self.assertIsInstance(self.app.editor, LabelEditor)
        self.assertEqual(self.app.editor.grid.model.rows, (("FIRST", "001"),))
        self.app.editor.destroy()

    def test_keyboard_can_select_first_or_last_row_and_edit_without_mouse(self):
        self.app.select_file(self.file)
        self.pump()
        self.root.deiconify()
        self.root.update()
        self.app.data_tree.focus_force()
        self.app.data_tree.event_generate("<End>")
        self.root.update()
        self.assertEqual(self.app.selected, 1)
        self.app.data_tree.event_generate("<Home>")
        self.root.update()
        self.assertEqual(self.app.selected, 0)
        self.assertEqual(str(self.app.edit_button.cget("state")), "normal")
        self.app.data_tree.event_generate("<Return>")
        self.root.update()
        self.assertIsInstance(self.app.editor, LabelEditor)
        self.assertEqual(self.app.editor.grid.model.rows, (("FIRST", "001"),))
        self.app.editor.destroy()

    def test_destroy_root_with_editor_has_no_callback_errors(self):
        self.app.add_row()
        self.root.destroy()
        self._cleanups.pop()
        self.assertFalse(self.errors)
        self.assertTrue(self.app.closed)

    def test_batch_add_edit_keeps_unselected_labels_and_rejects_overflow(self):
        self.app.add_row()
        self.app.editor.grid.paste_text("AAA\t\tCCC\r\nDDD\tEEE\r\nKEEP\r\n")
        self.app.editor.apply()
        self.pump()
        self.assertEqual(self.app.analysis.blocks, (("AAA", "", "CCC"), ("DDD", "EEE"), ("KEEP",)))
        self.app.data_tree.selection_set(("0", "2"))
        self.app.list_selected()
        self.app.edit_selected()
        grid = self.app.editor.grid
        self.assertEqual(grid.model.row_limit, 2)
        original = grid.model.rows
        with self.assertRaisesRegex(ValueError, "행 추가"):
            grid.paste_text("a\nb\nc")
        self.assertEqual(grid.model.rows, original)
        grid.paste_text("CHANGED\t\tEND\nLAST\t001\t")
        self.app.editor.apply()
        self.pump()
        self.assertEqual(self.app.analysis.blocks, (("CHANGED", "", "END"), ("DDD", "EEE"), ("LAST", "001")))
        self.assertEqual(tuple(cell.text for cell in self.app.layout.cells), ("CHANGED", "", "END", "DDD", "EEE", "LAST", "001"))
        self.assertEqual(self.app.edit_revision, self.app.rendered_edit_revision)

    def test_direction_change_decline_and_cancel_restore_direction_and_edits(self):
        self.app.select_file(self.file)
        self.pump()
        self.app.open_editor((0,))
        self.apply_editor("KEEP")
        with patch("label_ui.messagebox.askyesno", return_value=False):
            self.app.orientation.set("기존 열 방식")
        self.pump()
        self.assertEqual(self.app.input_options().orientation, "rows")
        self.assertEqual(self.app.analysis.blocks[0], ("KEEP",))
        with patch("label_ui.messagebox.askyesno", return_value=True):
            self.app.orientation.set("기존 열 방식")
        self.app.cancel()
        self.assertEqual(self.app.input_options().orientation, "rows")
        self.assertEqual(self.app.analysis.blocks[0], ("KEEP",))

    def test_grid_keyboard_edit_apply_selection_and_undo_without_clipboard(self):
        self.root.deiconify()
        self.app.add_row()
        editor = self.app.editor
        grid = editor.grid
        self.root.update()
        grid.canvas.focus_force()
        grid.canvas.event_generate("<F2>")
        self.root.update()
        self.assertTrue(grid.editing)
        grid.entry.delete(0, "end")
        grid.entry.insert(0, "한글001")
        grid.entry.event_generate("<Tab>")
        self.root.update()
        self.assertEqual(grid.model.get(0, 0), "한글001")
        self.assertEqual(grid.active, (0, 1))
        grid.paste_text("B\tC")
        grid.select(0, 0)
        grid.canvas.event_generate("<Shift-Right>")
        self.root.update()
        self.assertEqual(grid.selection, (0, 0, 0, 1))
        grid.canvas.event_generate("<Delete>")
        self.root.update()
        self.assertEqual(grid.model.rows, (("", "", "C"),))
        grid.canvas.event_generate("<Control-z>")
        self.root.update()
        self.assertEqual(grid.model.rows, (("한글001", "B", "C"),))
        grid.canvas.event_generate("<Control-y>")
        self.root.update()
        self.assertEqual(grid.model.rows, (("", "", "C"),))
        grid.canvas.event_generate("<F2>")
        self.root.update()
        grid.entry.delete(0, "end")
        grid.entry.insert(0, "EDIT")
        grid.entry.event_generate("<Control-Return>")
        self.pump()
        self.assertIsNone(self.app.editor)
        self.assertEqual(self.app.analysis.blocks, (("", "EDIT", "C"),))

    def test_blank_edit_refused_cancel_preserves_original_and_add_row_delete_undo(self):
        self.app.add_row()
        grid = self.app.editor.grid
        grid.paste_text("ONE\nTWO\nTHREE")
        grid.select(1, 0)
        grid.delete_rows()
        self.assertEqual(grid.model.rows, (("ONE",), ("THREE",)))
        grid.history()
        self.assertEqual(grid.model.rows, (("ONE",), ("TWO",), ("THREE",)))
        self.app.editor.apply()
        self.pump()
        before = self.app.analysis.blocks
        self.app.open_editor((1,))
        self.app.editor.grid.clear()
        self.app.editor.apply()
        self.assertIsNotNone(self.app.editor)
        self.assertIn("비어", self.app.editor.error.cget("text"))
        self.app.editor.destroy()
        self.assertEqual(self.app.analysis.blocks, before)

    def test_oversized_selected_rectangle_refused_before_creating_modal(self):
        self.app.add_row()
        self.apply_editor("OK")
        with patch("label_ui.checked_rows", side_effect=ValueError("범위를 나누어 주세요.")):
            self.app.open_editor((0,))
        self.assertIsNone(self.app.editor)
        self.assertFalse(self.app.modal_open)
        self.assertIn("나누어", self.app.status.get())
        self.assertEqual(self.app.analysis.blocks, (("OK",),))

    def test_main_table_batch_keyboard_selection_keeps_anchor(self):
        self.app.add_row()
        self.app.editor.grid.paste_text("ONE\nTWO\nTHREE\nFOUR")
        self.app.editor.apply()
        self.pump()
        self.root.deiconify()
        self.root.update()
        table = self.app.data_tree
        table.focus_force()
        table.event_generate("<Home>")
        table.event_generate("<Shift-Down>")
        self.root.update()
        self.assertEqual(table.selection(), ("0", "1"))
        table.event_generate("<Shift-End>")
        self.root.update()
        self.assertEqual(table.selection(), ("0", "1", "2", "3"))
        table.event_generate("<Shift-Up>")
        self.root.update()
        self.assertEqual(table.selection(), ("0", "1", "2"))
        table.event_generate("<End>")
        table.event_generate("<Shift-Home>")
        self.root.update()
        self.assertEqual(table.selection(), ("0", "1", "2", "3"))
        table.event_generate("<Home>")
        table.event_generate("<Control-a>")
        self.root.update()
        self.assertEqual(table.selection(), ("0", "1", "2", "3"))
        table.event_generate("<Return>")
        self.root.update()
        self.assertEqual(self.app.editor.max_rows, 4)
        self.app.editor.destroy()


if __name__ == "__main__":
    unittest.main()
