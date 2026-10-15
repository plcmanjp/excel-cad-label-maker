"""String-only spreadsheet transactions shared by file import and the editor."""
import csv
from io import StringIO

MAX_CELLS = 250_000
MAX_CHARACTERS = 2_000_000


def column_name(index):
    name = ""
    while index >= 0:
        index, digit = divmod(index, 26)
        name = chr(65 + digit) + name
        index -= 1
    return name


def validate_cell(value, row=0, column=0):
    if not isinstance(value, str):
        raise ValueError("표의 값은 문자열이어야 합니다.")
    if any(ord(char) < 32 or ord(char) == 127 or char in "\u0085\u2028\u2029" for char in value):
        raise ValueError(f"{column_name(column)}{row + 1}: 셀 안의 줄바꿈, 탭과 제어 문자는 사용할 수 없습니다. 한 줄씩 옆 열로 옮겨 주세요.")
    return value


def normalize_row(row):
    end = len(row)
    while end and row[end - 1] == "":
        end -= 1
    return tuple(row[:end])


def checked_rows(rows):
    rows = tuple(tuple(row) for row in rows)
    width = max(map(len, rows), default=0)
    if len(rows) * width > MAX_CELLS:
        raise ValueError(f"표는 {MAX_CELLS:,}셀 이내로 나누어 작업해 주세요.")
    if sum(len(value) for row in rows for value in row) > MAX_CHARACTERS:
        raise ValueError("표는 2,000,000자 이내로 나누어 입력해 주세요.")
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            validate_cell(value, r, c)
    return rows


def normalize_rows(rows):
    return tuple(value for row in checked_rows(rows) if (value := normalize_row(row)))


def parse_tsv(text):
    # Excel quotes cells containing tabs, quotes or newlines. Parse first, then
    # reject embedded controls with the actual cell address instead of splitting.
    if len(text) > MAX_CHARACTERS * 2 + MAX_CELLS * 2:
        raise ValueError("클립보드가 너무 큽니다. 범위를 나누어 붙여넣어 주세요.")
    previous_limit = csv.field_size_limit()
    try:
        csv.field_size_limit(MAX_CHARACTERS)
        rows = []
        width = 0
        for row in csv.reader(StringIO(text, newline=""), delimiter="\t", strict=True):
            row = row or [""]
            width = max(width, len(row))
            if (len(rows) + 1) * width > MAX_CELLS:
                raise ValueError(f"표는 {MAX_CELLS:,}셀 이내로 나누어 작업해 주세요.")
            rows.append(row)
        if not rows:
            rows = [[""]]
        # Ragged plain text is expanded as a rectangle without discarding blanks.
        return checked_rows(tuple(tuple(row) + ("",) * (width - len(row)) for row in rows))
    except csv.Error as error:
        raise ValueError("클립보드 표의 따옴표 또는 셀 길이를 확인해 주세요. Excel에서 셀 범위를 다시 복사해 주세요.") from error
    finally:
        csv.field_size_limit(previous_limit)


def serialize_tsv(rows):
    rows = checked_rows(rows)
    width = max(map(len, rows), default=0)
    stream = StringIO(newline="")
    writer = csv.writer(stream, delimiter="\t", lineterminator="\r\n")
    writer.writerows(row + ("",) * (width - len(row)) for row in rows)
    return stream.getvalue()


class GridModel:
    """Immutable rows and bounded undo snapshots; a failed edit changes nothing."""
    def __init__(self, rows=(), row_limit=None):
        self.row_limit = row_limit
        self.rows = checked_rows(rows) or (("",),)
        if row_limit is not None and len(self.rows) > row_limit:
            raise ValueError("편집 대상 행 수를 확인해 주세요.")
        self.undo_stack, self.redo_stack = [], []

    @property
    def shape(self):
        return len(self.rows), max(1, max(map(len, self.rows), default=1))

    def get(self, row, column):
        return self.rows[row][column] if row < len(self.rows) and column < len(self.rows[row]) else ""

    def _commit(self, rows):
        rows = checked_rows(rows) or (("",),)
        if self.row_limit is not None and len(rows) > self.row_limit:
            raise ValueError(f"선택한 {self.row_limit}개 라벨만 편집할 수 있습니다. 여러 라벨을 새로 넣으려면 행 추가를 사용하세요.")
        if rows == self.rows:
            return False
        self.undo_stack.append(self.rows)
        # Retain at least one complete transaction, bounded by cells and text.
        while len(self.undo_stack) > 1 and (len(self.undo_stack) > 30 or
                sum(sum(map(len, rows)) for rows in self.undo_stack) > MAX_CELLS * 4 or
                sum(sum(len(v) for row in rows for v in row) for rows in self.undo_stack) > MAX_CHARACTERS * 4):
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.rows = rows
        return True

    def paste(self, row, column, values):
        values = checked_rows(values)
        if row < 0 or column < 0 or not values:
            raise ValueError("붙여넣을 셀을 선택해 주세요.")
        height, width = len(values), max(map(len, values), default=0)
        nrows, ncols = max(len(self.rows), row + height), max(self.shape[1], column + width)
        if self.row_limit is not None and nrows > self.row_limit:
            raise ValueError(f"선택한 {self.row_limit}개 라벨의 행 수를 넘습니다. 새 라벨은 행 추가에서 붙여넣어 주세요.")
        if nrows * ncols > MAX_CELLS:
            raise ValueError(f"표는 {MAX_CELLS:,}셀 이내로 나누어 작업해 주세요.")
        rows = list(self.rows) + [()] * (nrows - len(self.rows))
        for offset, value in enumerate(values):
            current = list(rows[row + offset])
            current += [""] * max(0, column + width - len(current))
            current[column:column + width] = list(value) + [""] * (width - len(value))
            rows[row + offset] = tuple(current)
        return self._commit(rows)

    def rectangle(self, top, left, bottom, right):
        if (bottom - top + 1) * (right - left + 1) > MAX_CELLS:
            raise ValueError("선택 범위를 줄여 주세요.")
        return tuple(tuple(self.get(r, c) for c in range(left, right + 1)) for r in range(top, bottom + 1))

    def clear(self, top, left, bottom, right):
        # Empty visual cells do not expand the stored document.
        bottom, right = min(bottom, len(self.rows) - 1), min(right, self.shape[1] - 1)
        if bottom < top or right < left:
            return False
        return self.paste(top, left, tuple(("",) * (right - left + 1) for _ in range(bottom - top + 1)))

    def delete_rows(self, first, last):
        if self.row_limit is not None:
            raise ValueError("편집 창에서는 대상 행을 삭제할 수 없습니다. Delete는 선택 셀의 내용만 비웁니다.")
        return self._commit(self.rows[:first] + self.rows[last + 1:])

    def undo(self):
        if not self.undo_stack:
            return False
        self.redo_stack.append(self.rows)
        self.rows = self.undo_stack.pop()
        return True

    def redo(self):
        if not self.redo_stack:
            return False
        self.undo_stack.append(self.rows)
        self.rows = self.redo_stack.pop()
        return True
