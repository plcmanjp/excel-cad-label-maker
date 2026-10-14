# 작업 저널 (CURRENT)

## 목표

- [Issue #2](https://github.com/plcmanjp/excel-cad-label-maker/issues/2)의 원본 소스 복구와 재현 가능한 Windows 빌드를 준비한다. 제품 구현은 해당 작업을 시작하는 세션에서 진행한다.

## 현재 상태

- [공개 저장소](https://github.com/plcmanjp/excel-cad-label-maker)와 [0.1.0 기준 릴리스](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.1.0)가 공개되어 있다. 초기 구성은 [Issue #1](https://github.com/plcmanjp/excel-cad-label-maker/issues/1)이 소유한다.
- 900 기반 하네스, 원본 소스, Windows ZIP과 체크섬을 구성했다. 원개발자 직장인, Fork 및 후속 개발자 plcmanjp를 구분하며 공개 재배포 허락을 확인했다.

## 주요 결정

- 0.1.0은 제공된 기존 EXE의 변경 없는 기준 배포다. 원본 파일과 EXE hash를 고정하며 재빌드로 표현하지 않는다.
- 작업지시는 GitHub Issues가 소유한다. 원본 파일은 바이트 보존하고 복구 구현은 별도 src/에 추가한다. 임의 오픈소스 라이선스를 부여하지 않는다.

## 검증 결과

- 하네스 22개, 릴리스 경계 6개와 등록 훅 4조건이 통과했다. 공개 경계 검사와 독립 검수 및 보정 delta 검수를 통과했다. 초기 main과 tag의 GitHub Actions가 성공했다.
- 실제 EXE 경로와 정확한 앱 창의 실행을 확인했다. 공개 ZIP 재다운로드 SHA-256이 로컬과 일치하며 ZIP 내부 EXE는 원본과 같다.

## 미해결 사항

- 원본 Python 소스의 문법 손상, 소스와 EXE의 빌드 대응 관계 및 외부 라이브러리 고지는 Issue #2에서 확인한다.
- 실제 엑셀 변환, CAD 호환성과 DWG 직접 출력은 미검증이다. 시각 캡처는 다른 창에 가려져 수용 검증 근거에서 제외했다. Claude 설정과 Codex trust 및 hooks 런타임 승인은 별도다.

## 다음 작업

1. Issue #2에서 정상 원본과 빌드 정보를 확인하고 복구 구현 범위를 정한다.
2. 합성 엑셀 및 DXF 회귀 검사와 재현 가능한 Windows 빌드를 구축한다.
3. 구체적인 이용 조건과 외부 라이브러리 고지를 확인한다.
