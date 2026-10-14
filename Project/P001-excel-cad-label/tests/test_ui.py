"""Real Tk widgets, synthetic drop data; does not claim Explorer mouse QC."""
import ast
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from openpyxl import Workbook
from tkinterdnd2 import COPY, REFUSE_DROP, TkinterDnD
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from excel_cad_label import App


class UiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.file = Path(self.temp.name) / "드래그 공백 파일.xlsx"
        book = Workbook()
        book.active.append(["TEST"])
        book.save(self.file)
        book.close()
        self.root = TkinterDnD.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.app = App(self.root, check_updates=False)

    def test_drop_selects_file_without_browse_and_enables_generate(self):
        with patch("excel_cad_label.filedialog.askopenfilename", side_effect=AssertionError("browse called")):
            event = SimpleNamespace(data=self.root.tk.call("list", str(self.file)))
            self.assertEqual(self.app.on_drop(event), COPY)
        self.assertEqual(self.app.excel_path.get(), str(self.file.resolve()))
        self.assertEqual(str(self.app.run_button.cget("state")), "normal")
        self.assertIn(self.file.name, self.app.drop_area.cget("text"))

    def test_bad_drop_preserves_selection_and_clear_disables_generate(self):
        self.app.select_file(self.file)
        self.assertEqual(self.app.on_drop(SimpleNamespace(data="bad.txt")), REFUSE_DROP)
        self.assertEqual(self.app.excel_path.get(), str(self.file.resolve()))
        self.app.clear_file()
        self.assertEqual(self.app.excel_path.get(), "")
        self.assertEqual(str(self.app.run_button.cget("state")), "disabled")

    def test_browse_and_drop_share_selection(self):
        with patch("excel_cad_label.filedialog.askopenfilename", return_value=str(self.file)):
            self.app.on_browse()
        self.assertEqual(self.app.excel_path.get(), str(self.file.resolve()))

    def test_generate_saves_dxf_after_drop_without_open_dialog(self):
        import ezdxf
        output = Path(self.temp.name) / "output.dxf"
        self.app.on_drop(SimpleNamespace(data=self.root.tk.call("list", str(self.file))))
        with patch("excel_cad_label.filedialog.askopenfilename", side_effect=AssertionError("browse called")), \
             patch("excel_cad_label.filedialog.asksaveasfilename", return_value=str(output)), \
             patch("excel_cad_label.messagebox.showinfo"):
            self.app.on_generate()
        self.assertEqual(next(iter(ezdxf.readfile(output).modelspace().query("TEXT"))).dxf.text, "TEST")

    def test_registered_drops_on_entire_window(self):
        def check(widget):
            self.assertTrue(widget.dnd_bind("<<Drop>>"))
            for child in widget.winfo_children():
                check(child)
        check(self.root)

    def test_no_prohibited_ui_punctuation(self):
        forbidden = set("\u2014\u2013\u2015\u00b7\u30fb\u2022")
        for source in (Path(__file__).resolve().parents[1] / "src").glob("*.py"):
            for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    self.assertFalse(forbidden.intersection(node.value), (source.name, node.lineno))


if __name__ == "__main__":
    unittest.main()
