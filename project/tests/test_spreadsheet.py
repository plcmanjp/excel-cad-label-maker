"""Row import, lossless TSV, transaction limits and settings migration."""
from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from unittest.mock import Mock
from types import SimpleNamespace

from openpyxl import Workbook
import xlwt
import ezdxf
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from input_model import Cell, InputOptions, WorkbookInput, analyze, read_workbook
from spreadsheet_data import GridModel, MAX_CELLS, normalize_rows, parse_tsv, serialize_tsv
from settings_store import SettingsStore, SettingsError, defaults
from converter import LabelSettings, compute_layout, drawing_from_layout, save_drawing
from spreadsheet import SpreadsheetGrid


class SpreadsheetModelTests(unittest.TestCase):
    def test_windows_tk_clipboard_receives_lf_without_double_conversion(self):
        grid = SimpleNamespace(copy_text=lambda: 'A\tB\r\n"C"\tD\r\n', clipboard_clear=Mock(),
                               clipboard_append=Mock(), clear=Mock(), on_error=Mock())
        self.assertEqual(SpreadsheetGrid.copy(grid, cut=True), "break")
        grid.clipboard_append.assert_called_once_with('A\tB\n"C"\tD\n')
        grid.clear.assert_called_once()
        grid.on_error.assert_not_called()

    def test_copy_failure_does_not_cut_data(self):
        grid = SimpleNamespace(copy_text=lambda: "data\r\n", clipboard_clear=Mock(),
                               clipboard_append=Mock(side_effect=ValueError("busy")), clear=Mock(), on_error=Mock())
        SpreadsheetGrid.copy(grid, cut=True)
        grid.clear.assert_not_called()
        grid.on_error.assert_called_once_with("busy")

    def test_new_ui_korean_has_no_transport_replacement(self):
        for name in ("label_editor.py", "label_ui.py", "spreadsheet.py", "spreadsheet_data.py"):
            contents = (Path(__file__).resolve().parents[1] / "src" / name).read_text(encoding="utf-8")
            self.assertNotIn("??", contents, name)
            self.assertIn("라벨" if name != "spreadsheet_data.py" else "표", contents)

    def test_excel_tsv_roundtrip_keeps_rectangle_quotes_and_literal_strings(self):
        rows = (("001", "", "한글"), ("", 'say "hello"', "12345678901234567890"),
                ("2026-10-15", "=1+1", " spaced "), ("", "", ""))
        self.assertEqual(parse_tsv(serialize_tsv(rows)), rows)
        self.assertEqual(parse_tsv("a\tb\r\nc\r\n"), (("a", "b"), ("c", "")))
        self.assertEqual(parse_tsv("\t\r\n"), (("", ""),))
        self.assertEqual(parse_tsv(""), (("",),))

    def test_internal_newline_and_tab_are_addressed_without_splitting(self):
        for contents in ('A\t"B\nC"\r\nD\tE\r\n', 'A\t"B\tC"\r\n'):
            with self.subTest(contents=contents), self.assertRaisesRegex(ValueError, "B1"):
                parse_tsv(contents)
        for contents in ('"unclosed', '"closed"junk'):
            with self.subTest(contents=contents), self.assertRaises(ValueError):
                parse_tsv(contents)

    def test_blank_contract_and_whitespace_are_shared(self):
        self.assertEqual(normalize_rows((("AAA", "", "CCC", ""), ("", "B", ""), ("", ""), (" ",))),
                         (("AAA", "", "CCC"), ("", "B"), (" ",)))

    def test_paste_undo_redo_and_clear_are_single_transactions(self):
        grid = GridModel((("old", "keep"),))
        grid.paste(0, 1, (("001", ""), ("한글", "x")))
        after = (("old", "001", ""), ("", "한글", "x"))
        self.assertEqual(grid.rows, after)
        grid.undo()
        self.assertEqual(grid.rows, (("old", "keep"),))
        grid.redo()
        self.assertEqual(grid.rows, after)
        grid.clear(0, 1, 1, 2)
        self.assertEqual(grid.rows, (("old", "", ""), ("", "", "")))
        grid.undo()
        self.assertEqual(grid.rows, after)
        grid.paste(0, 0, (("different",),))
        self.assertFalse(grid.redo())

    def test_edit_row_limit_rejects_without_changing_rows_or_history(self):
        grid = GridModel((("original",), ("second",)), row_limit=2)
        before = grid.rows
        with self.assertRaisesRegex(ValueError, "행 추가"):
            grid.paste(1, 0, (("a",), ("b",)))
        self.assertEqual(grid.rows, before)
        self.assertEqual(grid.undo_stack, [])
        with self.assertRaises(ValueError):
            grid.delete_rows(0, 0)
        self.assertEqual(grid.rows, before)

    def test_capacity_character_and_control_rejections_are_atomic(self):
        grid = GridModel((("safe",),))
        for row, col, values in [(MAX_CELLS, 0, (("x",),)), (0, MAX_CELLS, (("x",),)),
                                 (0, 0, (("x" * 2_000_001,),)), (0, 0, (("x\x00y",),))]:
            with self.subTest(row=row, col=col), self.assertRaises(ValueError):
                grid.paste(row, col, values)
            self.assertEqual(grid.rows, (("safe",),))
            self.assertEqual(grid.undo_stack, [])
        with patch("spreadsheet_data.MAX_CELLS", 3), self.assertRaises(ValueError):
            parse_tsv("a\tb\nc\td")

    def test_row_delete_and_undo_preserve_other_rows(self):
        grid = GridModel((("A",), ("B",), ("C",)))
        grid.delete_rows(1, 1)
        self.assertEqual(grid.rows, (("A",), ("C",)))
        grid.undo()
        self.assertEqual(grid.rows, (("A",), ("B",), ("C",)))
        grid.delete_rows(0, 2)
        self.assertEqual(grid.rows, (("",),))

    def test_large_table_and_bounded_history(self):
        grid = GridModel()
        rows = tuple((str(index), "", "한글") for index in range(10_000))
        grid.paste(0, 0, rows)
        self.assertEqual(grid.shape, (10_000, 3))
        self.assertEqual(grid.rectangle(9999, 0, 9999, 2), (rows[-1],))
        grid.undo()
        self.assertEqual(grid.shape, (1, 1))
        grid.redo()
        self.assertEqual(grid.rows, rows)
        for index in range(40):
            grid.paste(0, 0, ((str(index),),))
        self.assertLessEqual(len(grid.undo_stack), 30)


class RowImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def file(self, rows, suffix):
        path = self.folder / ("synthetic" + suffix)
        if suffix == ".xlsx":
            book = Workbook()
            for row in rows:
                book.active.append(row)
            book.save(path)
            book.close()
        else:
            book = xlwt.Workbook()
            sheet = book.add_sheet("first")
            for r, row in enumerate(rows):
                for c, value in enumerate(row):
                    if value is not None:
                        sheet.write(r, c, value)
            book.save(str(path))
        return path

    def test_xlsx_xls_same_rows_blanks_headers_ranges_and_addresses(self):
        rows = (("AAA", "BBB", "CCC"), ("DDD", "EEE", None), ("", "FFF", ""),
                ("GGG", "", "III"), (None, None, None))
        for suffix in (".xlsx", ".xls"):
            with self.subTest(suffix=suffix):
                path = self.file(rows, suffix)
                before = path.read_bytes()
                source = read_workbook(path)
                result = analyze(source)
                self.assertEqual(result.blocks, (("AAA", "BBB", "CCC"), ("DDD", "EEE"), ("", "FFF"), ("GGG", "", "III")))
                self.assertEqual(result.labels[2].addresses, ("A3", "B3"))
                first = analyze(source, InputOptions("A1:C2"))
                self.assertEqual((len(first.labels), first.cell_count), (2, 5))
                selected = analyze(source, InputOptions("B1:C4", skip_header=True))
                self.assertEqual(selected.blocks, (("EEE",), ("FFF",), ("", "III")))
                self.assertEqual(selected.labels[-1].addresses, ("B4", "C4"))
                self.assertEqual(result.blocks, normalize_rows(tuple(tuple(v or "" for v in row) for row in rows)))
                self.assertEqual(path.read_bytes(), before)

    def test_row_values_do_not_intern_boolean_and_number_across_labels(self):
        for suffix in (".xlsx", ".xls"):
            result = analyze(read_workbook(self.file(((False, True), (0, 1), (True, False)), suffix)))
            self.assertEqual(result.blocks, (("False", "True"), ("0", "1"), ("True", "False")))

    def test_row_strings_preserve_whitespace_and_controls_block_at_address(self):
        for suffix in (".xlsx", ".xls"):
            result = analyze(read_workbook(self.file(((" 001 ", " ", "x"), ("safe", "line\nbreak")), suffix)))
            self.assertEqual(result.blocks[0], (" 001 ", " ", "x"))
            self.assertEqual([(d.code, d.address) for d in result.errors], [("cell-control", "B2")])

    def test_format_and_errors_still_have_exact_provenance(self):
        source = WorkbookInput(self.folder / "unused.xlsx", "", ("sheet",), "sheet",
                               (Cell(1, 1, 1, "number", "000"), Cell(1, 2, "#VALUE!", "error"),
                                Cell(1, 3, "tail", "text"), Cell(2, 1, None, "formula-missing", formula=True)), 2, 3)
        result = analyze(source, InputOptions(mode="display"))
        self.assertEqual(result.blocks, (("001", "", "tail"),))
        self.assertEqual([(d.address, d.label) for d in result.errors], [("B1", 0), ("A2", None)])
        self.assertEqual(result.labels[0].addresses, ("A1", "B1", "C1"))

    def test_empty_cell_geometry_matches_dxf(self):
        layout = compute_layout((("A", "", "C"), ("", "B")), LabelSettings())
        doc = drawing_from_layout(layout)
        self.assertEqual(len(layout.cells), 5)
        self.assertEqual(len(doc.modelspace().query("LWPOLYLINE")), 5)
        self.assertEqual([text.dxf.text for text in doc.modelspace().query("TEXT")], ["A", "", "C", "", "B"])
        self.assertFalse(doc.audit().has_errors)
        path = self.folder / "blanks.dxf"
        save_drawing(doc, path)
        loaded = ezdxf.readfile(path)
        self.assertEqual(len(loaded.modelspace().query("LWPOLYLINE")), 5)
        self.assertEqual([text.dxf.text for text in loaded.modelspace().query("TEXT") if text.dxf.text], ["A", "C", "B"])


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.path = self.folder / "settings.json"

    def test_v1_last_and_presets_preserve_column_semantics_without_load_write(self):
        old = {k: v for k, v in defaults().items() if k != "orientation"}
        old.update(cell_w=73, mode="display")
        data = {"version": 1, "last": old, "presets": {"내 규격": old}}
        self.path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        before = self.path.read_bytes()
        store = SettingsStore(self.folder)
        self.assertFalse(store.protected)
        self.assertEqual(store.last, {**old, "orientation": "columns"})
        self.assertEqual(store.presets["내 규격"], store.last)
        self.assertEqual(self.path.read_bytes(), before)
        store.remember(store.last)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8"))["version"], 2)
        self.assertEqual(SettingsStore(self.folder).last, store.last)

    def test_new_install_rows_and_v2_row_and_column_presets(self):
        store = SettingsStore(self.folder)
        self.assertEqual(store.last["orientation"], "rows")
        store.save("old", {**defaults(), "orientation": "columns"})
        store.save("new", defaults())
        reloaded = SettingsStore(self.folder)
        self.assertEqual(reloaded.presets["old"]["orientation"], "columns")
        self.assertEqual(reloaded.presets["new"]["orientation"], "rows")

    def test_unknown_version_or_direction_or_v1_extra_field_preserves_file(self):
        for version, last in [(3, defaults()), (True, defaults()), (2, {**defaults(), "orientation": "auto"}), (1, defaults())]:
            with self.subTest(version=version):
                self.path.write_text(json.dumps({"version": version, "last": last, "presets": {}}), encoding="utf-8")
                before = self.path.read_bytes()
                store = SettingsStore(self.folder)
                self.assertTrue(store.protected)
                with self.assertRaises(SettingsError):
                    store.remember(defaults())
                self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
