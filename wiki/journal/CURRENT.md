# 작업 저널 (CURRENT)

## 목표

- 공개 0.4.2와 검증 근거를 유지하며, 남은 청소와 현장 검증을 각각의 이슈에서 이어간다.

## 현재 상태

- [0.4.2](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.4.2)를 정식 latest로 공개했다. [PR #29](https://github.com/plcmanjp/excel-cad-label-maker/pull/29)는 main에 병합됐고 #28은 CLOSED다.
- 원격과 세 독립 checkout의 병합 feature branch를 검증 후 정리했다. 원래 OneDrive checkout의 미커밋 작업과 중복 worktree 등록은 보존했다. #27의 승인된 C: 중간 파일 32개, 60,988,517bytes를 휴지통에 회수했고 실제 payload와 Git 보존 및 복원 사전 검사를 통과했다. D: 작업 폴더는 보존한다.
- 배포와 세션 마무리는 [#30](https://github.com/plcmanjp/excel-cad-label-maker/issues/30)이 소유한다. 최종 기록 commit의 CI와 동기화 readback은 해당 완료 댓글에서 확인한다.

## 주요 결정

- 시작 새 버전 팝업과 수동 재열기 및 모달 지연을 유지한다. 비교 버전은 별도 QC 진입점에서만 사용한다.
- 정식 tag의 source는 8498b03412e8a80c844967dca13803b145d11436으로 고정한다. 이후 기록 전용 commit은 공개 자산을 교체하지 않는다. 기존 공개 자산과 법적 고지 및 검증/복구 자료를 보존한다.
- 0.4.1 사용자는 수동 버튼이나 직접 다운로드로 한 번 갱신해야 한다. 시작 자동 팝업은 0.4.2부터 복원된다. 미지원 청소를 우회하지 않는다.

## 검증 결과

- [배포 QC](../../../project/qc/release042-results.json)의 제품 130개, 정식 ZIP/EXE와 실제 DXF 저장/재읽기, 별도 frozen QC의 무입력 시작 팝업/수동 재열기, 이전 공개 0.4.1의 새 버전 안내 및 공개 자산 재다운로드 대조는 PASS다. 독립 소스/패키지 검수의 미해결 finding은 0개다.
- 최종 PR의 push/PR CI와 공식 source main CI 38726264533 PASS. 실제 CAD/물리적 드롭/OS 현장 검증 범위와 로컬 release guard의 symlink 권한 skip 1개는 별도 명시했다.

## 미해결 사항

- #27의 선행 공용 도구 지원 개선은 [부모 #52](https://github.com/plcmanjp/.agents/issues/52)와 [draft PR #54](https://github.com/plcmanjp/.agents/pull/54)가 소유한다. 공개 manifest v2와 운영 linked 전체 보존 모드를 구현했고 C: 실제 수용 및 독립 검수를 통과했다. 실제 C: 캐시 회수는 완료했으며 원경로에 다시 쓰는 Restore는 실행하지 않았다. D: 수용은 OneDrive 정상화 완료 통보와 새 fixture 검증을 기다린다. 회수한 checkout은 복구 증거 보존을 위해 그대로 두고 진행 기록은 별도 clean checkout에 반영한다.
- 원래 checkout의 index/HEAD 및 작업 diff 지문은 사전/사후 같지만 원격 추적과 tag refs 변화가 관찰됐다. 이 세션은 그 폴더의 fetch/reset/prune/ref 쓰기를 실행하지 않았고 원인은 미확정이다. 전체 refs 무변경이나 동기화 완료로 판정하지 않는다.
- #14의 실제 CAD/별도 PC/원본 빌드 대응과 #20의 초보 사용자/실제 OS 배율 검증은 OPEN이다.

## 다음 작업

1. OneDrive 정상화 완료 후 D: 새 fixture의 실제 회수 및 복원 수용을 진행한다. #27의 D: 실제 대상은 정확한 계획과 승인 전까지 보존한다.
2. #14의 실제 CAD와 별도 PC 및 원본 실행 파일 대응을 확인한다.
3. #20의 실제 초보 사용자와 OS 배율 150/200%를 검증한다.
