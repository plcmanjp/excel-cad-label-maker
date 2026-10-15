# 작업 저널 (CURRENT)

## 목표

- [Issue #22](https://github.com/plcmanjp/excel-cad-label-maker/issues/22)의 구현과 QC를 완료하고 [PR #23](https://github.com/plcmanjp/excel-cad-label-maker/pull/23)을 검토 대기 상태로 유지한다.

## 현재 상태

- feat/issue-22-spreadsheet의 제품 구현 커밋 c80b532를 원격에 반영하고 PR #23을 발행했다. 제품 구현과 로컬/원격 Windows QC가 완료됐다. 최종 진행 기록 커밋의 검사 상태는 PR checks가 기준이다.
- Writer와 독립 Reviewer의 작업은 종료됐다. 실제 Excel 합성 워크북과 검증용 앱은 닫았으며 원본과 사용자 설정은 유지됐다.
- main 병합, 버전 변경과 공개 릴리스는 수행하지 않았다. 원본, 기존 배포 자산과 법적 고지 및 과거 QC/journal은 유지한다.

## 주요 결정

- 새 기본값은 1행=1라벨, 열=한 줄이다. 앞쪽/중간 빈 셀은 유지하고 오른쪽 끝 빈 셀과 전체 빈 행은 제외한다. 기존 설정과 프리셋은 열 방식으로 읽는다.
- 추가/편집은 공통 그리드와 작업 복사본을 사용한다. 대상 행 수나 용량을 넘는 붙여넣기는 거부하고 취소는 기존 데이터를 보존한다. 원본 Excel에 쓰지 않는다.
- Excel 대상 범위는 텍스트 형식으로 지정한다. 셀 내부 탭/개행은 위치를 안내하고 거부한다. 실제 OS 배율과 native IME 조합은 이번 검증 결과로 확대 판정하지 않는다.

## 검증 결과

- [로컬 QC 기록](../../../project/qc/issue22-results.json)과 [성능 기록](../../../project/qc/issue22-performance.json)에 실행 환경, 실제 Excel 18셀 왕복, source/EXE DXF 17칸과 빈 칸 2개, 배율 및 10,000행 측정과 빌드 해시가 있다.
- 제품 커밋의 [Windows CI](https://github.com/plcmanjp/excel-cad-label-maker/actions/runs/38695062944): 제품 128개, 배포 보호 16개, 하네스 22개, 저장소/공개 문서와 Windows 빌드 PASS. 독립 검수의 미해결 확정 결함 0개.
- 개발용 EXE의 16개 소스 해시가 커밋된 Git 파일과 정확히 일치한다. 공개 버전은 여전히 0.3.0이며 신규 기능은 PR 검토 대상이다.

## 미해결 사항

- PR #23은 OPEN이며 main 병합과 공개 릴리스는 별도 작업이다.
- Issue #20의 초보 사용자와 실제 OS 배율, Issue #14의 실제 CAD/별도 PC/원본 대응/이용 조건은 별도 OPEN 범위다.
- 기존 청소 차단 상태는 유지한다. 이번 작업에 파일/캐시/작업트리 청소는 포함하지 않는다.

## 다음 작업

1. PR #23의 리뷰와 최종 head 검사 결과를 기준으로 병합 여부를 결정한다.
2. 별도 사용성/현장 QC는 Issue #20과 #14의 수용 조건으로 진행한다.
3. 릴리스 작업이 승인되면 버전과 자산을 새로 고정하고 배포 절차를 수행한다.
