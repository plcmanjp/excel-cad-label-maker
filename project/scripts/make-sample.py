"""Generate only synthetic local Excel QC assets, never customer data."""
from pathlib import Path
import sys
from openpyxl import Workbook

if __name__ == "__main__":
    path = Path(sys.argv[1])
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    for row in [["전원 입력", "차단기", "001"], ["MOTOR 01", "출력"],
                ["긴 한글과 English 라벨 자동 축소 검증", "", "예비"], [None, None]]:
        workbook.active.append(row)
    workbook.save(path)
    workbook.close()
    print("PASS: synthetic sample created")
