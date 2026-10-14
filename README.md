# Excel CAD Label Maker

Excel에 입력한 글자를 전기함 덕트 라벨용 DXF 도면으로 만드는 Windows 앱입니다.

[Windows 앱 다운로드](https://github.com/plcmanjp/excel-cad-label-maker/releases/latest) | [사용 설명](wiki/guides/usage.md) | [문제 보고](https://github.com/plcmanjp/excel-cad-label-maker/issues)

## 시작하기

1. 최신 릴리스의 Windows ZIP을 내려받아 새 폴더에 압축을 풉니다.
2. Excel_CAD_Label.exe를 실행합니다. 함께 들어 있는 폴더와 파일도 유지하세요.
3. .xlsx 또는 .xls 파일 한 개를 앱에 끌어다 놓습니다. 파일 찾기로 선택할 수도 있습니다.
4. 라벨 크기, 간격, 글꼴과 색상을 정한 뒤 DXF 도면 생성 및 저장을 누릅니다.
5. 저장한 DXF를 사용하는 CAD에서 열어 확인합니다.

Windows 64비트용이며 Python을 별도로 설치할 필요가 없습니다.

공개 다운로드 0.2.2는 기존 생성 및 저장 화면을 제공합니다. 아래 미리보기와 프리셋 기능은 현재 소스의 새 화면에 해당하며 공개 패키지에 제공되면 업데이트 안내에서 확인할 수 있습니다.

## 주요 기능

- Excel의 각 열을 위에서 아래로 읽고 빈 셀을 기준으로 라벨을 구분합니다.
- 라벨 크기(mm), 한 행의 라벨 수와 가로 및 세로 간격을 설정합니다.
- 글꼴과 색상을 선택하고 긴 글자를 라벨 폭에 맞게 축소합니다.
- 한글을 포함한 DXF 도면을 저장합니다.
- 새 버전이 나오면 업데이트 알림에서 다운로드 페이지를 열 수 있습니다.
- 새 화면에서는 파일 선택 즉시 출력 문자와 원본 셀, 경고 및 도면을 확인합니다.
- 시트와 셀 범위를 선택하고 마지막 설정 및 이름 있는 프리셋을 재사용합니다.
- 입력 오류를 저장 전에 확인하고 작업을 취소해 기존 출력 파일을 보존합니다.

## 지원 형식

입력은 .xlsx와 .xls, 출력은 DXF입니다. DWG가 필요하면 DXF를 CAD에서 열어 다른 이름으로 저장하세요. 앱에서 DWG를 직접 생성하지는 않습니다.

글꼴 표시와 도면의 최종 치수는 사용하는 CAD에서 확인하세요. 상세 입력 규칙과 업데이트 방법은 [사용 설명](wiki/guides/usage.md)에 있습니다.

## 크레딧과 라이선스

원개발자: 직장인. 개발 및 관리: [plcmanjp](https://github.com/plcmanjp).

[크레딧](release/package/CREDITS.md)과 [이용 조건](release/package/NOTICE.md)을 확인하세요. 포함 라이브러리의 라이선스는 앱의 third_party 폴더에 있습니다.

개발에 참여하려면 [개발 안내](wiki/guides/development.md)를 참고하세요.
