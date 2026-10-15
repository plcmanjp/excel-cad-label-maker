# 작업 저널 (CURRENT)

## 목표

- [Issue #28](https://github.com/plcmanjp/excel-cad-label-maker/issues/28)의 시작 시 업데이트 팝업 복원을 검토하고 병합과 정식 배포 여부를 결정한다.

## 현재 상태

- fix/issue-28-startup-update에서 구현과 로컬 검증을 완료했다. 앱 시작 시 새 버전이면 팝업을 표시하며 기존 수동 버튼으로 다시 열 수 있다. main과 공개 앱에는 아직 반영하지 않았다.
- [0.4.1](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.4.1)은 정식 latest로 유지한다. 원래 OneDrive checkout의 변경과 #27 청소 차단도 보존한다.

## 주요 결정

- 시작 시 기존 비동기 조회를 한 번 수행하고 새 버전일 때 기존 팝업을 연다. 모달이 열려 있으면 지연하고 최신/조회 실패의 자동 팝업은 표시하지 않는다.
- 낮은 비교 버전은 기존 별도 QC 진입점에서만 사용한다. 정상 앱에 버전 override를 추가하지 않는다. 새 공개 배포나 기존 자산 교체는 수행하지 않았다.

## 검증 결과

- [Issue #28 결과](../../../project/qc/issue28-results.json): 알림 10개와 전체 제품 130개, 저장소/공개 문서 및 diff 검사, 개발용/별도 업데이트 QC 빌드 PASS.
- source commit 5178777의 두 clean 빌드에서 각 1,126파일과 소스 hash 및 LICENSE 원문 일치를 확인했다. 소스와 QC EXE의 실제 GitHub 조회 후 자동 팝업/닫기/수동 재열기, 정상 개발 EXE의 최신 상태 수동 안내도 PASS다.

## 미해결 사항

- #28은 전용 branch의 검토 대상이며 병합과 정식 배포가 남아 있다. 원격 검사는 해당 PR의 최종 head를 기준으로 확인한다.
- #27은 청소 manifest 부재와 원래 checkout의 예상 밖 변경 및 중복 등록으로 OPEN이다. 실제 삭제는 0개다. #14와 #20의 현장 검증도 OPEN이다.

## 다음 작업

1. #28의 최종 PR 검사와 검토 결과를 기준으로 병합 및 정식 배포 여부를 결정한다.
2. #27의 manifest 범위와 변경 소유권 및 복구 자료를 확정한다. 그 전에는 reset, prune이나 회수를 하지 않는다.
3. #14와 #20의 현장 검증을 해당 환경에서 이어간다.
