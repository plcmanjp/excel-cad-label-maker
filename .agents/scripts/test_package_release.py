"""Verify refusal boundaries and deterministic packaging with synthetic binaries only."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('package_release.py')
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
        for folder in ['release', '.local/baseline', 'original']:
            (self.root / folder).mkdir(parents=True)
        (self.root / '.local/baseline/Excel_Cad_Label.exe').write_bytes(self.binary)
        (self.root / 'original/source.py').write_bytes(self.source)
        for name in ['README.md','CREDITS.md','NOTICE.md']:
            (self.root / name).write_text('Synthetic fixture\n', encoding='utf-8')
        (self.root / 'VERSION').write_text('0.1.0\n', encoding='utf-8')
        self.manifest = {'version':'0.1.0', 'redistribution_permission':'confirmed_by_repository_owner',
            'source_path':'original/source.py','source_sha256':hashlib.sha256(self.source).hexdigest(),
            'binary_name':'Excel_Cad_Label.exe','binary_sha256':hashlib.sha256(self.binary).hexdigest(),
            'binary_size':len(self.binary),'rebuild_from_imported_source':False}
        self.write_manifest()

    def write_manifest(self):
        (self.root / 'release/manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def invoke(self):
        with contextlib.redirect_stdout(io.StringIO()):
            module.main()

    def refused(self, message):
        with self.assertRaisesRegex(SystemExit, message):
            self.invoke()
        self.assertFalse((self.root / 'dist').exists())

    def test_unchanged_package_is_deterministic(self):
        self.invoke()
        archive = next((self.root / 'dist').glob('*.zip'))
        first = archive.read_bytes()
        self.invoke()
        self.assertEqual(first, archive.read_bytes())
        sums = (self.root / 'dist/SHA256SUMS.txt').read_text()
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
        (self.root / 'VERSION').write_text('0.2.0\n')
        self.refused('Version mismatch')

    def test_false_rebuild_claim_is_refused(self):
        self.manifest['rebuild_from_imported_source'] = True
        self.write_manifest()
        self.refused('must not claim a source rebuild')

if __name__ == '__main__':
    unittest.main()
