# 작업 저널 (CURRENT)

## 목표

- main 동기화와 병합 branch 및 작업트리 정리를 마친 상태로 세션을 종료하고 복구 자료를 보존한다.

## 현재 상태

- 로컬과 원격 branch는 main 하나이며 등록 worktree도 main 하나다. 동일한 내용의 7cd8dae는 병합 커밋 06486bd로 이력이 연결돼 있다.
- 사용자 추가 지시로 .local/worktrees/issue-22를 휴지통에 옮기고 백업된 비활성 등록을 정리했다. 이전에 회수한 QC/빌드 폴더와 함께 .local의 정리 대상 6개 처리를 마쳤다.
- .local/baseline의 원본 0.1.0 실행 파일과 재사용 uia-qc-env는 보존한다. 원래 미커밋 작업은 stash b6b5211, 파일 및 Git metadata 백업과 독립 검증 bundle에 있다.
- 공개 latest 0.4.2와 source/tag/자산, 법적 고지, QC 요약 및 Notion의 소개 초안과 이미지 원본은 유지한다. 제품 변경과 새 공개 배포는 수행하지 않았다.

## 주요 결정

- 최신 사용자 지시는 병합된 branch의 남은 worktree 정리를 명시한다. 전체 원본/백업을 다시 대조하고 공용 기본 selected-path 실행기로 정확한 폴더 하나를 회수했다.
- Git 등록 metadata를 별도로 백업하고 실제 휴지통 payload 검증 후 정확히 issue-22 한 개만 제시하는 prune dry-run을 확인했다. 해당 비활성 등록만 정리했으며 main과 stash 및 refs/index는 보존했다.
- 원래 .local 전체 백업과 최신 등록 백업, stash, bundle 및 실제 휴지통 receipt는 정리 대상이 아니다. 개인 절대 경로와 원시 감사 자료는 Git에 넣지 않는다.
- 실제 Shell Restore는 실행하지 않았다. worktree 복구가 필요하면 payload와 등록 백업을 함께 검토하며 옛 index/refs를 최신 main에 통째로 덮어쓰지 않는다.

## 검증 결과

- 회수한 6개 폴더는 총 11,817개 파일, 541,418,292bytes다. 마지막 worktree의 7,848개 파일과 708개 디렉터리, 127,092,535bytes도 실제 $I 원경로와 $R의 전체 집합 및 모든 파일 SHA-256이 백업 manifest와 일치한다.
- 마지막 회수 전 독립 읽기 전용 검수의 미해결 결함은 0개다. 회수와 등록 정리 전후 main의 refs/index가 같고 제외한 baseline 및 uia-qc-env의 파일 hash도 유지됐다.
- 기록 커밋 2e4cd31의 Windows CI 39274399078은 completed/success이며 verify와 product가 모두 통과했다. 최종 세션 기록 head의 CI는 해당 head의 실제 결과를 기준으로 한다.
- 세션 기록에는 제품/하네스 코드 변화가 없다. 저장소와 공개 문서 검사 및 diff-check는 PASS다. 최종 원격 동기화는 실제 head readback을 기준으로 한다.

## 미해결 사항

- [Issue #27](https://github.com/plcmanjp/excel-cad-label-maker/issues/27)은 OPEN 상태다. 이번 실제 회수와 백업 검증은 완료했으며 실제 Shell Restore와 전체 ACL/cloud 의미의 동일 복원은 검증하지 않았다. 과거 운영 보존 모드의 제한이 해결됐다고 확대하지 않는다.
- 원래 미커밋 작업은 최신 main에 적용하지 않은 보존 자료다. 재사용과 폐기는 별도 사용자 작업으로 결정한다.

## 다음 작업

1. 다음 세션은 최종 main과 CI 및 Issue #27의 현재 수용 범위를 확인한다. 추가 청소를 자동으로 시작하지 않는다.
2. 이전 작업이 필요하면 stash와 외부 파일/등록 백업 및 독립 bundle에서 필요한 부분을 확인한다. 모든 복구 자료를 보존한다.
3. 공개 0.4.2와 기존 사용자 수용 범위 및 Notion의 소개 자료를 유지한다.
