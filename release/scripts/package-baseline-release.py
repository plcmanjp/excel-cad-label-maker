"""Package the authorized unchanged baseline; never rebuild or publish."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    manifest = json.loads((ROOT / 'release/baseline/manifest.json').read_text(encoding='utf-8'))
    version = (ROOT / 'release/baseline/VERSION').read_text(encoding='utf-8').strip()
    if version != manifest['version'] or version != '0.1.0':
        raise SystemExit('Version mismatch: baseline packaging only supports 0.1.0')
    if manifest['redistribution_permission'] != 'confirmed_by_repository_owner':
        raise SystemExit('Redistribution permission is not confirmed')
    source = (ROOT / manifest['source_path']).read_bytes()
    if digest(source) != manifest['source_sha256']:
        raise SystemExit('Original source integrity mismatch')
    binary = (ROOT / '.local/baseline' / manifest['binary_name']).read_bytes()
    if digest(binary) != manifest['binary_sha256'] or len(binary) != manifest['binary_size']:
        raise SystemExit('Original executable integrity mismatch')
    if manifest['rebuild_from_imported_source'] is not False:
        raise SystemExit('Baseline must not claim a source rebuild')
    output = ROOT / 'release/artifacts/baseline-build'
    output.mkdir(parents=True, exist_ok=True)
    name = f'Excel-CAD-Label-Maker-{version}-windows-x64.zip'
    archive = output / name
    members = {manifest['binary_name']: binary,
               'README.md': (ROOT / 'release/package/README-baseline.md').read_bytes()}
    for relative in ['release/package/CREDITS.md', 'release/package/NOTICE.md', 'release/baseline/VERSION', 'release/baseline/manifest.json']:
        members[Path(relative).name] = (ROOT / relative).read_bytes()
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for member, data in members.items():
            info = zipfile.ZipInfo('Excel-CAD-Label-Maker/' + member, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            package.writestr(info, data)
    with zipfile.ZipFile(archive) as package:
        if package.testzip() is not None:
            raise SystemExit('ZIP integrity failure')
        if digest(package.read('Excel-CAD-Label-Maker/' + manifest['binary_name'])) != manifest['binary_sha256']:
            raise SystemExit('Packaged executable integrity mismatch')
    checksum = digest(archive.read_bytes())
    (output / 'SHA256SUMS.txt').write_text(checksum + '  ' + name + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'archive': name, 'sha256': checksum, 'size': archive.stat().st_size, 'exe_unchanged': True, 'members': list(members)}, ensure_ascii=True))

if __name__ == '__main__':
    main()
