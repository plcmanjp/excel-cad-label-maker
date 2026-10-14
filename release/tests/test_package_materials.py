import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/package-materials.py'
spec = importlib.util.spec_from_file_location('package_materials', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PlainMaterialsTests(unittest.TestCase):
    def test_plain_guides_and_legal_bytes_keep_valid_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / 'release/artifacts/app'
            output.mkdir(parents=True)
            (output / 'app.exe').write_bytes(b'SYNTHETIC-EXE')
            (output / '_internal').mkdir()
            embedded = b'# Embedded original license\n'
            (output / '_internal/LICENSE.md').write_bytes(embedded)
            notice = root / 'release/third_party/notices/demo/00-LICENSE.md'
            notice.parent.mkdir(parents=True)
            legal = b'# Original terms\r\nDo not modify these bytes.\r\n'
            notice.write_bytes(legal)
            provenance = {'demo': {'files': {'demo/00-LICENSE.md': {'sha256': hashlib.sha256(legal).hexdigest()}}}}
            (root / 'release/third_party/provenance.json').write_text(json.dumps(provenance))
            for name in ['release/package/NOTICE.md', 'release/package/CREDITS.md',
                         'release/package/README-Windows.md', 'wiki/reference/third-party.md']:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('# Guide\n\nRead **NOTICE.md** and [credits](CREDITS.md).\n', encoding='utf-8')
            module.prepare_materials(root, output, True)
            self.assertEqual((output / 'README.txt').read_text(), 'Guide\n\nRead NOTICE.txt and credits (CREDITS.txt).\n')
            self.assertEqual((output / 'third_party/notices/demo/00-LICENSE.txt').read_bytes(), legal)
            self.assertEqual((output / '_internal/LICENSE.txt').read_bytes(), embedded)
            self.assertEqual(notice.read_bytes(), legal)
            final = json.loads((output / 'third_party/provenance.json').read_text())
            self.assertEqual(final['demo']['files']['demo/00-LICENSE.txt']['sha256'], hashlib.sha256(legal).hexdigest())
            self.assertFalse(list(output.rglob('*.md')))

    def test_source_directory_or_outside_path_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'repo'; root.mkdir()
            source = root / 'project/src'; source.mkdir(parents=True)
            sentinel = source / 'README.md'; sentinel.write_bytes(b'preserve')
            with self.assertRaises(ValueError): module.prepare_materials(root, source)
            with self.assertRaises(ValueError): module.guard_output(root, root.parent)
            self.assertEqual(sentinel.read_bytes(), b'preserve')

    def test_collisions_are_refused_before_any_output_mutation(self):
        for collision in ['notice', 'case', 'existing', 'embedded', 'provenance']:
            with self.subTest(collision=collision), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                output = root / 'release/artifacts/app'
                output.mkdir(parents=True)
                (output / 'app.exe').write_bytes(b'SYNTHETIC-EXE')
                notices = root / 'release/third_party/notices/demo'
                notices.mkdir(parents=True)
                (notices / '00-LICENSE.md').write_bytes(b'Original markdown')
                provenance = {'demo': {'files': {}}}
                if collision in ['notice', 'case']:
                    name = '00-LICENSE.txt' if collision == 'notice' else '00-license.TXT'
                    (notices / name).write_bytes(b'Distinct original text')
                elif collision == 'existing':
                    target = output / 'third_party/notices/demo/00-license.TXT'
                    target.parent.mkdir(parents=True)
                    target.write_bytes(b'Existing output')
                elif collision == 'embedded':
                    (output / 'NOTICE.MD').write_bytes(b'Embedded notice')
                else:
                    provenance['demo']['files'] = {'demo/00-LICENSE.md': {}, 'demo/00-LICENSE.txt': {}}
                (root / 'release/third_party/provenance.json').write_text(json.dumps(provenance))
                for name in ['release/package/NOTICE.md', 'release/package/CREDITS.md',
                             'release/package/README-Windows.md', 'wiki/reference/third-party.md']:
                    source = root / name
                    source.parent.mkdir(parents=True, exist_ok=True)
                    source.write_text('# Guide\n', encoding='utf-8')
                before = {p.relative_to(output).as_posix(): p.read_bytes()
                          for p in output.rglob('*') if p.is_file()}
                with self.assertRaisesRegex(ValueError, 'collision'):
                    module.prepare_materials(root, output, True)
                after = {p.relative_to(output).as_posix(): p.read_bytes()
                         for p in output.rglob('*') if p.is_file()}
                self.assertEqual(after, before)
