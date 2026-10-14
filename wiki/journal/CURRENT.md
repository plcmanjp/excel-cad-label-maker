# 작업 저널 (CURRENT)

## 목표

- [Issue #6](https://github.com/plcmanjp/excel-cad-label-maker/issues/6)의 승인된 main 병합과 복구 앱 v0.2.0 빌드 및 공개 릴리스를 완료한다.

## 현재 상태

- [공개 저장소](https://github.com/plcmanjp/excel-cad-label-maker)와 [0.1.0 기준 릴리스](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.1.0)가 공개되어 있다. 초기 구성은 [Issue #1](https://github.com/plcmanjp/excel-cad-label-maker/issues/1)이 소유한다.
- 900 기반 하네스, 원본 소스, Windows ZIP과 체크섬을 구성했다. 원개발자 직장인, Fork 및 후속 개발자 plcmanjp를 구분하며 공개 재배포 허락을 확인했다.

- 원본 소스의 현재 파일명은 excel_cad_label.py이며 manifest와 Git 원본 보존 속성이 같은 경로를 가리킨다. 파일 내용의 SHA-256은 원본과 동일하다.
- 별도 `src/` 복구 앱, Python 3.13.15 `.venv`, 의존성 잠금과 실행 및 Windows 개발 빌드가 구성되어 있다. `dist/Excel_CAD_Label_Dev/`는 공개 릴리스가 아닌 로컬 개발 앱이다.
- PR #4의 검증된 업데이트 알림과 ABC 아이콘을 main e20e952에 병합했다. 현재 사용자 승인에 따라 `release/v0.2.0`에서 정식 버전과 후속 패키징 및 공개 안내를 준비한다. 원본 v0.1.0은 보존한다.
- Issue #5의 투명 PNG와 10개 크기의 ICO를 개발 EXE 및 Tk 창에 적용했다. 정상 및 QC 빌드, 실제 앱과 탐색기의 아이콘 관찰을 완료했으며 결과는 `qc/app-icon-results.json`에 있다.
- Issue #6의 정식 0.2.0 버전과 후속 릴리스 패키징을 구현했다. 제품 33개, 빌드 및 패키징 7개, 하네스 22개와 기준선 6개가 통과했고 로컬 native symlink 1개는 생성 권한 부족으로 SKIP이다. 독립 검수의 체크섬 leaf 보호를 보정해 delta PASS를 받았으며 원격 CI와 최종 ZIP QC는 진행 중이다.

## 주요 결정

- 0.1.0은 제공된 기존 EXE의 변경 없는 기준 배포다. 원본 파일과 EXE hash를 고정하며 재빌드로 표현하지 않는다.
- 작업지시는 GitHub Issues가 소유한다. 원본 파일은 바이트 보존하고 복구 구현은 별도 src/에 추가한다. 임의 오픈소스 라이선스를 부여하지 않는다.

## 검증 결과

- 하네스 22개, 릴리스 경계 6개와 등록 훅 4조건이 통과했다. 공개 경계 검사와 독립 검수 및 보정 delta 검수를 통과했다. 초기 main과 tag의 GitHub Actions가 성공했다.
- 제품 18개, 하네스 22개 및 기준 릴리스 경계 6개 검사를 통과했다. 실제 탐색기 드래그로 한글과 공백이 있는 합성 Excel을 선택하고 빌드 EXE로 DXF 저장을 확인했다. 상세와 hash는 `qc/development-build.json`에 있다.
- Issue #3 제품 33개, 빌드 보호 2개, 하네스 22개와 기준 릴리스 6개 및 독립 검수가 통과했다. 실제 API, 정상 EXE의 무알림과 수동 확인, 검수 EXE의 팝업 및 나중에와 Chrome 릴리스 페이지 열기를 확인했다. 버전 입력 구분과 hash는 `qc/update-notice-results.json`에 있다. 해당 브랜치의 원격 CI 결과는 GitHub Actions에서 확인한다.
- Issue #5의 기존 63개 검사, 공개 경계 및 독립 delta 검수가 통과했다. 정상 및 QC EXE의 10개 실제 PE 아이콘 리소스와 포함 ICO가 원본과 일치한다. 실제 정상 앱 제목 표시줄과 탐색기 작은 및 큰 아이콘에서 ABC를 확인했다.

## 미해결 사항

- 원본 Python의 손상 상태는 보존하며 원본 소스와 기존 EXE의 대응 관계, 기존 EXE의 포함 라이브러리 및 원권리자의 구체적인 이용 조건은 미확인이다. 복구 앱의 고지는 `third_party/`에 별도로 보존한다.
- DXF 실제 CAD 열기와 글꼴 렌더링 및 Python 없는 별도 PC 실행은 미검증이다. DWG 직접 출력은 미지원이다. Claude 설정과 Codex trust 및 hooks 런타임 승인은 별도다.

## 다음 작업

1. 합성 DXF를 실제 사용 CAD에서 열고 한글, 글꼴, mm 규격 및 레이어를 확인한다.
2. 원본 빌드 자료와 구체적인 수정, 상업 이용 및 추가 재배포 조건을 확인한다.
3. Issue #6의 후속 릴리스 준비 PR을 검증해 main에 병합하고 최종 ZIP QC 및 v0.2.0 공개와 원격 hash readback을 완료한다.
