"""In-memory output edits overlay immutable Excel analysis; never write Excel."""
from dataclasses import replace
from input_model import Analysis, InputOptions, Label, MAX_CELLS

MAX_EDITOR_CHARACTERS = 2_000_000


def parse_label_text(value):
    if len(value) > MAX_EDITOR_CHARACTERS:
        raise ValueError("한 라벨은 2,000,000자 이내로 입력해 주세요.")
    # Only CR/LF separate cells. Reject DXF control/tag injection and silent trimming.
    lines = tuple(value.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
    if not lines or any(not line.strip() for line in lines):
        raise ValueError("빈 줄 없이 한 줄에 한 칸의 문자를 입력해 주세요.")
    if len(lines) > MAX_CELLS:
        raise ValueError(f"한 라벨은 {MAX_CELLS:,}칸 이내로 입력해 주세요.")
    if any(ord(char) < 32 or ord(char) == 127 for line in lines for char in line):
        raise ValueError("탭과 제어 문자는 사용할 수 없습니다. 일반 공백으로 바꿔 주세요.")
    return lines


def edited_label(texts, original=None):
    if original is None:
        return Label(tuple(texts), ("직접 입력",) * len(texts), "manual")
    addresses = original.addresses[:len(texts)] + ("직접 입력",) * max(0, len(texts) - len(original.addresses))
    return Label(tuple(texts), addresses, "edited" if original.origin != "manual" else "manual")


def apply_edits(base, replacements=(), additions=(), options=None):
    base = base or Analysis(None, options or InputOptions(), "직접 입력", (), ())
    replacements = dict(replacements)
    if any(type(index) is not int or index < 0 or index >= len(base.labels) for index in replacements):
        raise ValueError("편집할 라벨을 다시 선택해 주세요.")
    labels = tuple(replacements.get(index, label) for index, label in enumerate(base.labels)) + tuple(additions)
    if sum(len(label.texts) for label in labels) > MAX_CELLS:
        raise ValueError(f"출력 데이터는 {MAX_CELLS:,}칸 이내로 나누어 작업해 주세요.")
    # Keep sheet-level diagnostics and unresolved source errors. A user edit replaces
    # cell-format warnings of that label, while layout warnings are recomputed later.
    diagnostics = tuple(d for d in base.diagnostics if d.severity == "error" or d.label not in replacements)
    return replace(base, labels=labels, diagnostics=diagnostics)
