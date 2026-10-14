"""Check public-repository boundaries and original provenance, without importing damaged source."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
ICON_ROOT = Path('Project/P001-excel-cad-label/src/assets')
ICON_SIGNATURES = {'app-icon.png': b'\x89PNG\r\n\x1a\n', 'app-icon.ico': b'\x00\x00\x01\x00'}

def main():
    errors = []
    try:
        icons = json.loads((ROOT / ICON_ROOT / 'manifest.json').read_text(encoding='utf-8'))
        for name, signature in ICON_SIGNATURES.items():
            asset = (ROOT / ICON_ROOT / name).read_bytes()
            if not asset.startswith(signature) or hashlib.sha256(asset).hexdigest() != icons['sha256'][name]:
                errors.append('icon signature or hash mismatch: ' + name)
    except (OSError, ValueError, KeyError, TypeError):
        errors.append('icon asset manifest missing or invalid')
    manifest = json.loads((ROOT / 'release/manifest.json').read_text(encoding='utf-8'))
    if (ROOT / 'VERSION').read_text().strip() != manifest['version']:
        errors.append('version mismatch')
    raw = (ROOT / manifest['source_path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest['source_sha256']:
        errors.append('original source changed')
    try:
        ast.parse(raw.decode('utf-8'))
    except SyntaxError as exc:
        print(f'KNOWN LIMITATION: imported original syntax error at line {exc.lineno}; not a build target')
    else:
        errors.append('source status changed: reassess baseline claims')
    entry = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
    for rule in (ROOT / '.agents/rules').glob('*.md'):
        relative = rule.relative_to(ROOT).as_posix()
        if entry.count('@' + relative + '\n') != 1:
            errors.append('rule import mismatch: ' + relative)
        if len(rule.read_bytes()) > 32768 or len(rule.read_text(encoding='utf-8').splitlines()) > 500:
            errors.append('rule size exceeded: ' + relative)
    for adapter in (ROOT / '.codex/agents').glob('*.toml'):
        data = tomllib.loads(adapter.read_text(encoding='utf-8'))
        if not all(key in data for key in ['name','description','model','model_reasoning_effort','developer_instructions']):
            errors.append('adapter fields missing: ' + adapter.name)
        if 'Do not spawn child agents.' not in data['developer_instructions']:
            errors.append('leaf boundary missing: ' + adapter.name)
        if not (ROOT / '.agents/agents' / (adapter.stem + '.md')).is_file():
            errors.append('role missing: ' + adapter.name)
    tomllib.loads((ROOT / '.codex/config.toml').read_text(encoding='utf-8'))
    ignored = {'.git','.local','.venv','venv','.cache','dist','build','__pycache__'}
    # Prune local environments before traversal; dependency files are not public sources.
    paths = []
    for directory, folders, files in os.walk(ROOT):
        folders[:] = [name for name in folders if name not in ignored]
        paths.extend(Path(directory) / name for name in files)
    for path in paths:
        rel = path.relative_to(ROOT)
        if any(part in ignored for part in rel.parts) or not path.is_file() or rel.as_posix() == '.codex/hooks.json':
            continue
        data = path.read_bytes()
        if rel.parent == ICON_ROOT and rel.name in ICON_SIGNATURES:
            continue  # Only these hash-verified product images may bypass UTF-8 decoding.
        if data.startswith(b'\xef\xbb\xbf'):
            errors.append('UTF-8 BOM: ' + rel.as_posix())
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            errors.append('non UTF-8 tracked content: ' + rel.as_posix())
            continue
        if re.search(r'[A-Za-z]:[\\/](?:OneDrive|Users)', text):
            errors.append('private machine path: ' + rel.as_posix())
        if rel.parts[:2] == ('third_party', 'notices'):
            continue  # Preserved external legal originals, not authored UI prose.
        if rel.parts[0] not in {'.agents','.codex','wiki','Project'} and path.suffix in {'.md','.txt'}:
            if re.search('[\u2014\u2013\u2015\u00b7\u30fb\u2022]', text):
                errors.append('display punctuation: ' + rel.as_posix())
    for forbidden in ['CLAUDE.md','CODEX.md','AGENTS.override.md']:
        if (ROOT / forbidden).exists():
            errors.append('duplicate entry: ' + forbidden)
    for error in errors:
        print('FAIL: ' + error, file=sys.stderr)
    if errors:
        raise SystemExit(1)
    print('PASS: original provenance, public boundaries, encoding, rule imports and adapters')

if __name__ == '__main__':
    main()
