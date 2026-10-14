# Excel CAD Label Maker

엑셀에 입력한 문자를 전기함 작업용 덕트 라벨 DXF 도면으로 배치하는 Windows 무설치 앱입니다.

- 원개발자: **직장인** (닉네임)
- Fork 및 후속 개발: **[plcmanjp](https://github.com/plcmanjp)**
- 현재 배포 버전: **0.1.0**

[릴리스 다운로드](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.1.0) | [개발 작업](https://github.com/plcmanjp/excel-cad-label-maker/issues) | [크레딧](CREDITS.md)

## 사용 방법

1. 릴리스의 Windows ZIP 파일을 내려받아 압축을 풉니다.
2. Excel_Cad_Label.exe를 실행하고 엑셀 파일을 선택합니다.
3. 라벨 크기(mm), 한 행에 배치할 라벨 수, 간격, 글꼴과 색상을 지정합니다.
4. DXF 도면을 저장하고 사용하는 CAD에서 열어 확인합니다.

엑셀의 각 열을 위에서 아래로 읽으며 빈 셀이 라벨 묶음을 구분합니다. 한 묶음 안의 각 문자는 라벨 한 칸이 됩니다. 라벨 줄 수에 따라 높이가 달라집니다. 글자가 길면 자동 축소 및 압축 옵션을 사용할 수 있습니다.

현재 원본은 **DXF를 생성**합니다. DWG 파일이 필요하면 DXF를 연 CAD의 다른 이름으로 저장 기능을 이용하세요. 앱 자체의 DWG 직접 생성과 CAD별 호환성은 검증되지 않았습니다.

## 0.1.0의 범위

0.1.0은 전달받은 기존 EXE를 변경 없이 배포하는 기준 릴리스입니다. 배포 버전 0.1.0은 이 프로젝트에서 부여한 번호이며, EXE 내부 버전이나 이 저장소에서 새로 빌드한 결과를 의미하지 않습니다.

가져온 Python 원본은 따옴표, 콜론과 연산자 일부가 누락되어 현재 그대로는 실행하거나 다시 빌드할 수 없습니다. 원본은 Project/P001-excel-cad-label/original/에 보존합니다. 원본 소스와 EXE의 빌드 대응 관계도 확인되지 않았습니다. 후속 개발은 이 원본을 보존한 별도 구현에서 진행합니다.

## 개발 중인 복구 앱

별도 `src/` 구현은 Excel 파일 드래그 앤 드롭, 입력 검사와 UTF-8 DXF 생성을 지원합니다. 탐색기에서 `.xlsx` 또는 `.xls` 한 개를 앱에 놓으면 파일 찾기 없이 선택할 수 있습니다. 규격을 확인한 뒤 `DXF 도면 생성 및 저장`을 누르세요.

`.venv` 구성, 소스 실행과 Windows 무설치 개발 빌드는 [개발 안내](CONTRIBUTING.md)를 따릅니다. 이 개발 빌드는 0.1.0 릴리스로 배포되지 않았으며 CAD에서 직접 열기와 원본 이용 조건 확인이 남아 있습니다.

## 개발 저장소

이 공개 저장소에서 개발, 이슈와 릴리스를 함께 관리합니다. 하네스는 900 스타터의 단일 AGENTS.md, 중립 규칙, Codex 어댑터와 SessionStart 검증 구조를 사용합니다.

- [개발 안내](https://github.com/plcmanjp/excel-cad-label-maker/blob/main/CONTRIBUTING.md)
- [릴리스 절차](https://github.com/plcmanjp/excel-cad-label-maker/blob/main/docs/releasing.md)
- [배포와 권리 범위](NOTICE.md)
- [현재 진행 상태](https://github.com/plcmanjp/excel-cad-label-maker/blob/main/wiki/journal/CURRENT.md)

실제 고객의 엑셀 자료와 도면은 공개 저장소나 Issue에 올리지 마세요.
