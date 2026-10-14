# 작업 저널 (CURRENT)

## 목표

- [Issue #12](https://github.com/plcmanjp/excel-cad-label-maker/issues/12)의 텍스트 출력과 런타임 경량화를 완료했다. 남은 실제 CAD 및 사용자 PC와 원본 이용 조건 검증은 Issue #2에서 관리한다.

## 현재 상태

- [PR #13](https://github.com/plcmanjp/excel-cad-label-maker/pull/13)은 main에 병합됐으며 Issue #12는 CLOSED다. pandas 제거와 직접 읽기 및 TXT 출력과 고지 충돌 거부를 구현하고 최종 빌드 및 압축 해제 앱 QC를 완료했다.
- 앱 구현은 project/src, 원본은 project/original, 제품과 빌드 보호 검사는 project/tests에서 관리한다. 문서는 wiki, 배포 자료는 release에 있으며 .venv와 .local은 루트에 유지한다.
- 공개 v0.2.0과 v0.1.0은 보존한다. 신규 검증 빌드는 공개 버전과 구분한다.

## 주요 결정

- [Issue #2](https://github.com/plcmanjp/excel-cad-label-maker/issues/2)는 실제 CAD, Python 없는 별도 PC와 원본 이용 조건 확인이 남아 있어 OPEN을 유지한다. 원본 소스와 제공된 EXE의 빌드 대응은 확인되지 않았다.
- 원본과 외부 고지의 byte를 보존한다. 빌드 출력의 Markdown 고지는 내용 변경 없이 .txt 이름으로 제공하고 출력 provenance를 맞춘다.
- numpy는 ezdxf의 필수 의존성이므로 유지한다. pandas 제거는 기존 읽기 결과와 날짜, bool, 오류 및 수식 캐시 대조를 통과해 채택했다.
- CURRENT 한글 전송 손상을 UTF-8 파일 편집으로 복구했다. 실제 CURRENT 구조를 기존 hook 파서로 확인하는 예방 검증을 추가한다.

## 검증 결과

- 개발, 업데이트 QC 및 clean main 정식 빌드와 로컬 ZIP 및 실제 앱 QC를 통과했다. CI77개가 모두 PASS이며 원본과 공개 자산을 보존했다. 결과와 hash 및 성능 측정의 범위는 [공개 QC 기록](../../project/qc/runtime-optimization-results.json)에 있다.

## 미해결 사항

- 실제 CAD, 별도 PC와 원본의 세부 이용 조건은 Issue #2의 미검증 범위다. DWG 직접 출력은 미지원이다.

## 다음 작업

1. 사용하는 실제 CAD에서 DXF의 글꼴과 정렬 및 도면 수용을 확인한다.
2. Python 없는 별도 사용자 PC에서 무설치 폴더 앱을 확인한다.
3. 원본 빌드 대응과 세부 이용 조건을 확인하고 다음 공개 버전의 범위를 정한다.
