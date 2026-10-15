# 릴리스 절차

## 버전과 빌드

1. project/src/app_version.py와 release/app-release.json의 버전 및 tag를 맞춥니다.
2. 사용자 안내와 릴리스 노트에는 사용자가 알아야 할 변경과 필요한 제한을 작성합니다.
3. 검증된 변경을 main에 병합하고 원격과 일치하는 깨끗한 checkout에서 정식 빌드를 실행합니다.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/build-dev.ps1 -Release
& .venv/Scripts/python.exe -B release/scripts/package-app-release.py --output release/artifacts/v0.4.0
~~~

패키저는 앱 버전과 source commit, 소스와 아이콘 및 모든 파일의 SHA-256을 대조합니다. 수정되거나 등록되지 않은 파일, 개발용 빌드, 링크 경로 및 기존 자산 덮어쓰기는 거부합니다. 출력에는 ZIP과 SHA256SUMS.txt가 생성됩니다.

## 배포물 확인

- ZIP을 새 폴더에 압축 해제해 앱 시작, Excel 드롭과 DXF 저장 및 읽기를 확인합니다.
- 아이콘과 업데이트 조회, 알림의 배치와 키보드 및 버튼 동작을 확인합니다.
- 사용자 안내는 TXT인지, 외부 고지 원문과 provenance의 hash가 일치하는지 확인합니다.
- CI와 독립 검수 및 실제 동작 결과를 해당 작업에 연결합니다. CAD 및 별도 PC 실행 결과는 확인한 환경에 한해 기록합니다.

## 공개와 확인

정확한 저장소와 공개 권한 및 버전, main commit과 ZIP/EXE hash를 대조한 뒤 해당 commit에 tag를 만듭니다. ZIP과 체크섬을 먼저 준비하고 두 자산이 uploaded 상태인 정식 릴리스를 latest로 공개합니다.

공개 후 원격 tag와 latest API 및 본문과 자산을 확인합니다. 업로드 ZIP과 체크섬을 다시 내려받아 로컬과 byte 및 SHA-256을 비교하고 이전 앱의 업데이트 안내를 확인합니다.

## 보존 자료

기존 공개 자산은 다른 빌드로 덮어쓰지 않습니다. 0.1.0은 제공된 원본 EXE를 변경 없이 포함하는 보관 버전입니다. release/baseline의 버전과 원본 hash 및 project/original은 유지합니다.

원개발자 직장인과 개발 및 관리자 plcmanjp의 크레딧을 유지하고 원본과 포함 라이브러리의 이용 조건은 NOTICE와 각 고지에 따릅니다.
