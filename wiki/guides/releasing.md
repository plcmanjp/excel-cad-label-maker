# 릴리스 절차

0.1.0은 기존 Windows EXE의 변경 없는 기준 배포이고 0.2.0은 별도 src 복구 구현의 후속 배포입니다. 원개발자 직장인과 후속 개발자 plcmanjp의 표기를 유지합니다. 후속 앱을 공급받은 원본 EXE의 동일한 재빌드라고 표현하지 않습니다.

## 후속 복구 앱

1. 정확한 저장소, 버전과 공개 승인을 확인하고 release/app-release.json 및 APP_VERSION을 일치시킵니다. release/baseline/VERSION과 release/baseline/manifest.json은 0.1.0 기준선으로 보존합니다.
2. 검증된 PR을 main에 병합하고 원격과 일치하는 깨끗한 main에서 project/scripts/build-dev.ps1 -Release를 실행합니다.
3. release/scripts/package-app-release.py --output release/artifacts/candidate-0.2.1으로 ZIP과 SHA256SUMS.txt를 만듭니다. release receipt, source commit과 모든 패키지 hash를 대조합니다.
4. 최종 ZIP을 별도 로컬 폴더에 풀고 EXE, Excel 드롭, DXF 저장 및 읽기, 아이콘과 업데이트 조회를 실제 확인합니다. 실제 CAD 및 별도 PC 검증 범위는 확대하지 않습니다.
5. 독립 읽기 전용 검수, CI와 실제 QC를 통과한 commit, 버전 및 EXE와 ZIP hash를 해당 Issue에 기록합니다.
6. 정확한 main commit의 tag를 생성하고 ZIP 및 SHA256SUMS.txt가 준비된 정식 릴리스를 최신 버전으로 공개합니다. 준비되지 않은 ZIP이나 draft를 업데이트 대상으로 삼지 않습니다.
7. 원격 tag 및 latest API와 자산 목록을 확인하고 업로드 ZIP 및 체크섬을 다시 내려받아 SHA-256을 비교합니다.

원본의 구체적인 수정, 상업 이용과 추가 재배포 조건은 확인 범위에 맞게 NOTICE와 릴리스 노트에서 설명합니다. 임의 오픈소스 라이선스를 부여하지 않습니다. 신규 공개는 현재 사용자의 해당 범위 승인이 있어야 합니다.

## 보존된 0.1.0 기준 배포

아래 절차는 원본 기준 배포에만 적용합니다. 후속 앱을 기존 v0.1.0에 덮어쓰지 않습니다.

1. release/baseline/VERSION과 manifest.json이 0.1.0인지 확인합니다.
2. 원본 EXE를 Git에서 제외되는 .local/baseline/Excel_Cad_Label.exe에 준비합니다.
3. 저장소 루트에서 python -B release/scripts/package-baseline-release.py를 실행합니다.
4. release/artifacts/baseline-build/의 ZIP, SHA256SUMS.txt와 내부 파일 목록을 확인합니다. 이미 공개한 release/artifacts/v0.1.0/ 파일은 보존합니다.
5. 하네스 회귀 검사, 저장소 검사와 EXE 실행 검증 결과를 해당 Issue에 기록합니다. 변환 및 CAD 호환성 검증 여부도 구분합니다.
6. 사용자 승인 대상이 plcmanjp/excel-cad-label-maker의 v0.1.0인지 확인하고, 확인된 commit에 tag를 생성합니다.
7. 해당 tag에 ZIP과 SHA256SUMS.txt를 첨부해 GitHub Release를 공개합니다. 업로드 파일을 다시 다운로드해 SHA-256을 비교합니다.

추가 기능을 포함한 후속 버전은 실제 소스 복구, 회귀 검사와 재현 가능한 빌드가 선행되어야 합니다. 원본과 다른 EXE로 manifest의 hash만 바꾸어 0.1.0을 덮어쓰지 않습니다. 공개 릴리스의 삭제, 교체나 force push는 별도 승인이 필요합니다.

Windows PowerShell 5.1에서 GitHub Issue에 한국어를 보낼 때 native CLI stdin을 사용하지 않습니다. 관리형 부모 환경에서는 부모 github-issue-text 공용 helper를 직접 호출합니다. 독립 환경은 UTF-8 BOM 없는 body-file을 gh에 전달하고 API로 원문을 다시 읽어 정확히 비교합니다.
