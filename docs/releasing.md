# 릴리스 절차

현재 릴리스 0.1.0은 기존 Windows EXE의 변경 없는 배포입니다. 원본 재배포 허락과 원개발자 및 후속 개발자 표기를 확인합니다. 현재 Python 원본으로 다시 빌드했다고 표현하지 않습니다.

1. VERSION과 release/manifest.json의 버전을 맞춥니다.
2. 원본 EXE를 Git에서 제외되는 .local/baseline/Excel_Cad_Label.exe에 준비합니다.
3. 저장소 루트에서 python -B .agents/scripts/package_release.py를 실행합니다.
4. dist/의 ZIP, SHA256SUMS.txt와 내부 파일 목록을 확인합니다.
5. 하네스 회귀 검사, 저장소 검사와 EXE 실행 검증 결과를 해당 Issue에 기록합니다. 변환 및 CAD 호환성 검증 여부도 구분합니다.
6. 사용자 승인 대상이 plcmanjp/excel-cad-label-maker의 v0.1.0인지 확인하고, 확인된 commit에 tag를 생성합니다.
7. 해당 tag에 ZIP과 SHA256SUMS.txt를 첨부해 GitHub Release를 공개합니다. 업로드 파일을 다시 다운로드해 SHA-256을 비교합니다.

추가 기능을 포함한 후속 버전은 실제 소스 복구, 회귀 검사와 재현 가능한 빌드가 선행되어야 합니다. 원본과 다른 EXE로 manifest의 hash만 바꾸어 0.1.0을 덮어쓰지 않습니다. 공개 릴리스의 삭제, 교체나 force push는 별도 승인이 필요합니다.

Windows PowerShell 5.1에서 GitHub Issue에 한국어를 보낼 때 native CLI stdin을 사용하지 않습니다. 관리형 부모 환경에서는 부모 github-issue-text 공용 helper를 직접 호출합니다. 독립 환경은 UTF-8 BOM 없는 body-file을 gh에 전달하고 API로 원문을 다시 읽어 정확히 비교합니다.
