"""Keep user entry points free of internal operating prose."""
from pathlib import Path
import re

USER_DOCUMENTS = (
    'README.md', 'wiki/INDEX.md', 'wiki/guides/usage.md',
    'release/package/README-Windows.md', 'release/package/README-baseline.md',
    'release/package/CREDITS.md', 'release/package/NOTICE.md',
    'wiki/reference/third-party.md',
)
INTERNAL_PROSE = re.compile(
    r'\b(?:Codex|Claude|SessionStart|QC|CI)\b|\.agents/|\.codex/|CURRENT\.md|'
    r'build-receipt|하네스|사용자\s*승인|독립\s*검수|(?:Issue|PR)\s*#\s*\d+'
)
INTERNAL_LINK = re.compile(r'\]\([^)]*(?:journal/|harness/|/qc/|CURRENT\.md|\.agents/)')


def public_document_errors(root):
    paths = [root / name for name in USER_DOCUMENTS]
    paths.extend((root / 'release/notes').glob('*.md'))
    errors = []
    for path in paths:
        if not path.is_file():
            errors.append('user document missing: ' + path.relative_to(root).as_posix())
            continue
        text = path.read_text(encoding='utf-8')
        if INTERNAL_PROSE.search(text) or INTERNAL_LINK.search(text):
            errors.append('internal prose in user document: ' + path.relative_to(root).as_posix())
    return errors


if __name__ == '__main__':
    errors = public_document_errors(Path(__file__).resolve().parents[2])
    if errors:
        raise SystemExit('\n'.join(errors))
    print('PASS: user-document audience boundary')
