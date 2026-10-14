# Excel CAD Label Maker 0.2.2

Excel의 글자를 전기함 덕트 라벨용 DXF 도면으로 만드는 Windows 64비트 앱입니다. Python을 별도로 설치할 필요가 없습니다.

## 사용 방법

1. ZIP 전체를 새 폴더에 압축 해제합니다. EXE와 _internal 및 third_party 폴더를 함께 유지하세요.
2. Excel_CAD_Label.exe를 실행합니다.
3. .xlsx 또는 .xls 파일 한 개를 앱에 끌어다 놓거나 파일 찾기로 선택합니다.
4. 라벨 크기(mm), 간격, 글꼴과 색상을 지정하고 DXF 도면 생성 및 저장을 누릅니다.
5. 저장한 DXF를 CAD에서 열어 글꼴과 치수를 확인합니다.

첫 시트의 각 열을 위에서 아래로 읽으며 빈 셀이 라벨을 구분합니다. 수식을 사용하면 Excel에서 계산하고 저장한 파일을 선택하세요.

## 업데이트

새 버전이 있으면 앱 중앙에 알림이 표시됩니다. 릴리스 페이지에서 새 ZIP을 받아 별도 폴더에 풀어 사용하세요. 자동 설치는 하지 않으며 인터넷 연결이 없어도 라벨 작업은 가능합니다.

## 지원 형식과 이용 조건

입력은 .xlsx와 .xls, 출력은 DXF입니다. DWG는 CAD에서 변환해 주세요. CAD의 설치 글꼴에 따라 문자 표시가 달라질 수 있습니다. 글꼴 파일은 포함하지 않습니다.

원개발자는 직장인, 개발 및 관리자는 plcmanjp입니다. 이용 조건은 NOTICE.txt, 크레딧은 CREDITS.txt, 포함 라이브러리의 라이선스는 third_party 폴더에서 확인하세요.

[사용 설명](https://github.com/plcmanjp/excel-cad-label-maker/blob/main/wiki/guides/usage.md)

[문제 보고](https://github.com/plcmanjp/excel-cad-label-maker/issues)
