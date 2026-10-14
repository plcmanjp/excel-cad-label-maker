"""Verify refusal boundaries and deterministic packaging with synthetic binaries only."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/package-baseline-release.py'
spec = importlib.util.spec_from_file_location('baseline_packager', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ReleaseBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='excel-cad-release-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.previous = module.ROOT
        module.ROOT = self.root
        self.addCleanup(setattr, module, 'ROOT', self.previous)
        self.binary = b'SYNTHETIC-EXE-NOT-RUNNABLE'
        self.source = b'# synthetic source fixture\n'
        for folder in ['release/baseline', 'release/package', '.local/baseline', 'original']:
            (self.root / folder).mkdir(parents=True)
        (self.root / '.local/baseline/Excel_Cad_Label.exe').write_bytes(self.binary)
        (self.root / 'original/source.py').write_bytes(self.source)
        for name in ['release/package/README-baseline.md','release/package/CREDITS.md','release/package/NOTICE.md']:
            (self.root / name).write_text('Synthetic fixture\n', encoding='utf-8')
        (self.root / 'release/baseline/VERSION').write_text('0.1.0\n', encoding='utf-8')
        self.manifest = {'version':'0.1.0', 'redistribution_permission':'confirmed_by_repository_owner',
            'source_path':'original/source.py','source_sha256':hashlib.sha256(self.source).hexdigest(),
            'binary_name':'Excel_Cad_Label.exe','binary_sha256':hashlib.sha256(self.binary).hexdigest(),
            'binary_size':len(self.binary),'rebuild_from_imported_source':False}
        self.write_manifest()

    def write_manifest(self):
        (self.root / 'release/baseline/manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def invoke(self):
        with contextlib.redirect_stdout(io.StringIO()):
            module.main()

    def refused(self, message):
        with self.assertRaisesRegex(SystemExit, message):
            self.invoke()
        self.assertFalse((self.root / 'release/artifacts').exists())

    def test_unchanged_package_is_deterministic(self):
        self.invoke()
        archive = next((self.root / 'release/artifacts/baseline-build').glob('*.zip'))
        first = archive.read_bytes()
        with zipfile.ZipFile(archive) as package:
            self.assertEqual(package.read('Excel-CAD-Label-Maker/README.md'),
                             (self.root / 'release/package/README-baseline.md').read_bytes())
            self.assertIn('Excel-CAD-Label-Maker/CREDITS.md', package.namelist())
            self.assertIn('Excel-CAD-Label-Maker/NOTICE.md', package.namelist())
        self.invoke()
        self.assertEqual(first, archive.read_bytes())
        sums = (self.root / 'release/artifacts/baseline-build/SHA256SUMS.txt').read_text()
        self.assertIn(hashlib.sha256(first).hexdigest(), sums)

    def test_changed_binary_is_refused(self):
        (self.root / '.local/baseline/Excel_Cad_Label.exe').write_bytes(b'CHANGED')
        self.refused('executable integrity mismatch')

    def test_changed_source_is_refused(self):
        (self.root / 'original/source.py').write_bytes(b'CHANGED')
        self.refused('source integrity mismatch')

    def test_unapproved_redistribution_is_refused(self):
        self.manifest['redistribution_permission'] = 'pending'
        self.write_manifest()
        self.refused('permission is not confirmed')

    def test_version_mismatch_is_refused(self):
        (self.root / 'release/baseline/VERSION').write_text('0.2.0\n')
        self.refused('Version mismatch')

    def test_false_rebuild_claim_is_refused(self):
        self.manifest['rebuild_from_imported_source'] = True
        self.write_manifest()
        self.refused('must not claim a source rebuild')

if __name__ == '__main__':
    unittest.main()
