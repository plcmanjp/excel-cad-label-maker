# 작업 저널 (CURRENT)

## 목표

- [Issue #2](https://github.com/plcmanjp/excel-cad-label-maker/issues/2)의 복구 앱과 Excel 드래그 앤 드롭 UX를 개발 기준선으로 유지하고 CAD 및 권리 확인을 진행한다.

## 현재 상태

- [공개 저장소](https://github.com/plcmanjp/excel-cad-label-maker)와 [0.1.0 기준 릴리스](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.1.0)가 공개되어 있다. 초기 구성은 [Issue #1](https://github.com/plcmanjp/excel-cad-label-maker/issues/1)이 소유한다.
- 900 기반 하네스, 원본 소스, Windows ZIP과 체크섬을 구성했다. 원개발자 직장인, Fork 및 후속 개발자 plcmanjp를 구분하며 공개 재배포 허락을 확인했다.

- 원본 소스의 현재 파일명은 excel_cad_label.py이며 manifest와 Git 원본 보존 속성이 같은 경로를 가리킨다. 파일 내용의 SHA-256은 원본과 동일하다.
- 별도 `src/` 복구 앱, Python 3.13.15 `.venv`, 의존성 잠금과 실행 및 Windows 개발 빌드가 구성되어 있다. `dist/Excel_CAD_Label_Dev/`는 공개 릴리스가 아닌 로컬 개발 앱이다.

## 주요 결정

- 0.1.0은 제공된 기존 EXE의 변경 없는 기준 배포다. 원본 파일과 EXE hash를 고정하며 재빌드로 표현하지 않는다.
- 작업지시는 GitHub Issues가 소유한다. 원본 파일은 바이트 보존하고 복구 구현은 별도 src/에 추가한다. 임의 오픈소스 라이선스를 부여하지 않는다.

## 검증 결과

- 하네스 22개, 릴리스 경계 6개와 등록 훅 4조건이 통과했다. 공개 경계 검사와 독립 검수 및 보정 delta 검수를 통과했다. 초기 main과 tag의 GitHub Actions가 성공했다.
- 제품 18개, 하네스 22개 및 기준 릴리스 경계 6개 검사를 통과했다. 실제 탐색기 드래그로 한글과 공백이 있는 합성 Excel을 선택하고 빌드 EXE로 DXF 저장을 확인했다. 상세와 hash는 `qc/development-build.json`에 있다.

## 미해결 사항

- 원본 Python의 손상 상태는 보존하며 원본 소스와 기존 EXE의 대응 관계, 기존 EXE의 포함 라이브러리 및 원권리자의 구체적인 이용 조건은 미확인이다. 복구 앱의 고지는 `third_party/`에 별도로 보존한다.
- DXF 실제 CAD 열기와 글꼴 렌더링 및 Python 없는 별도 PC 실행은 미검증이다. DWG 직접 출력은 미지원이다. Claude 설정과 Codex trust 및 hooks 런타임 승인은 별도다.

## 다음 작업

1. 합성 DXF를 실제 사용 CAD에서 열고 한글, 글꼴, mm 규격 및 레이어를 확인한다.
2. 원본 빌드 자료와 구체적인 수정, 상업 이용 및 추가 재배포 조건을 확인한다.
3. 별도 PC 실행과 Issue #2의 남은 수용 조건을 확인한 뒤 신규 공개 버전 범위를 결정한다.
