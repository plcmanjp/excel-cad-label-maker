"""Create plain user guides and byte-preserved TXT legal notices in a guarded build."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def guard_output(root, output):
    root, output = root.absolute(), output.absolute()
    for path in (output, *output.parents):
        if path.is_symlink() or path.is_junction():
            raise ValueError('Linked material output is refused')
        if path == root:
            break
    if output == root or not output.resolve().is_relative_to(root.resolve()) or not output.is_dir():
        raise ValueError('Material output must be an existing build directory in the repository')
    if not any(output.glob('*.exe')):
        raise ValueError('Material output must contain a built executable')
    for path in output.rglob('*'):
        if path.is_symlink() or path.is_junction():
            raise ValueError('Linked material output is refused')
    return output


def plain_text(markdown):
    def link(match):
        name, target = match.groups()
        if not target.startswith(('https://', 'http://')) and target.endswith('.md'):
            target = target[:-3] + '.txt'
        return name + ' (' + target + ')'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, markdown)
    lines = []
    for line in text.splitlines():
        line = re.sub(r'^#{1,6}\s+', '', line)
        if line.startswith('|'):
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if all(re.fullmatch(r'[-: ]+', cell) for cell in cells):
                continue
            line = ' / '.join(cells)
        line = line.replace('**', '').replace('`', '')
        line = re.sub(r'(?<![/\w])(README|NOTICE|CREDITS)\.md\b', r'\1.txt', line)
        lines.append(line)
    return '\n'.join(lines).strip() + '\n'


def prepare_materials(root, output, release=False):
    output = guard_output(root, output)
    third_party = output / 'third_party'
    writes, renames, targets = [], [], set()
    existing = {path.relative_to(output).as_posix().casefold(): path
                for path in output.rglob('*')}

    def reserve(target):
        name = target.relative_to(output).as_posix().casefold()
        if name in targets or name in existing:
            raise ValueError('TXT material name collision: ' + str(target.relative_to(output)))
        for parent in target.parents:
            if parent == output:
                break
            previous = existing.get(parent.relative_to(output).as_posix().casefold())
            if previous is not None and not previous.is_dir():
                raise ValueError('Material parent must be a directory')
        targets.add(name)

    def notice_name(name):
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe legal notice path')
        if relative.suffix.lower() == '.md':
            relative = relative.with_suffix('.txt')
        return relative.as_posix()

    def add_write(target, content):
        reserve(target)
        writes.append((target, content))

    provenance = json.loads((root / 'release/third_party/provenance.json').read_text(encoding='utf-8'))
    for source in (root / 'release/third_party/notices').rglob('*'):
        if source.is_symlink() or source.is_junction():
            raise ValueError('Linked legal notice source is refused')
        if not source.is_file():
            continue
        relative = source.relative_to(root / 'release/third_party/notices')
        add_write(third_party / 'notices' / notice_name(relative.as_posix()), source.read_bytes())
    recorded = set()
    for item in provenance.values():
        if 'files' in item:
            mapped = {}
            for name, info in item['files'].items():
                target_name = notice_name(name)
                if target_name.casefold() in recorded:
                    raise ValueError('Legal provenance name collision: ' + name)
                recorded.add(target_name.casefold())
                mapped[target_name] = info
            item['files'] = mapped
    add_write(third_party / 'provenance.json',
              (json.dumps(provenance, ensure_ascii=True, indent=2) + '\n').encode('utf-8'))
    guides = {'NOTICE.txt': root / 'release/package/NOTICE.md',
              'CREDITS.txt': root / 'release/package/CREDITS.md',
              'third_party/README.txt': root / 'wiki/reference/third-party.md'}
    if release:
        guides['README.txt'] = root / 'release/package/README-Windows.md'
    for name, source in guides.items():
        add_write(output / name, plain_text(source.read_text(encoding='utf-8')).encode('utf-8'))
    # Also preserve notices embedded by dependency hooks, changing only the extension.
    for path in list(output.rglob('*')):
        if path.is_file() and path.suffix.lower() == '.md':
            target = path.with_suffix('.txt')
            reserve(target)
            renames.append((path, target))
    # Validate the complete name plan and legal hashes before changing the output.
    planned = {path: content for path, content in writes}
    for item in provenance.values():
        for name, info in item.get('files', {}).items():
            content = planned.get(third_party / 'notices' / name)
            if content is None or hashlib.sha256(content).hexdigest() != info['sha256']:
                raise ValueError('Legal notice hash mismatch: ' + name)
    for name, filename in {'Python': 'Python-LICENSE.txt', 'Tk': 'Tk-LICENSE.txt', 'TkDnD': 'TkDnD-source-notice.tcl'}.items():
        content = planned.get(third_party / 'notices' / filename)
        if name in provenance and (content is None or hashlib.sha256(content).hexdigest() != provenance[name]['sha256']):
            raise ValueError('Runtime notice hash mismatch: ' + name)
    for target, content in writes:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    for source, target in renames:
        source.rename(target)
    return {'status': 'PASS', 'markdown_files': 0, 'legal_original_bytes_preserved': True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--release', action='store_true')
    args = parser.parse_args()
    print(json.dumps(prepare_materials(ROOT, ROOT / args.output, args.release)))
