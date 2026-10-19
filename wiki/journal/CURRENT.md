# 작업 저널 (CURRENT)

## 목표

- 원격 main 동기화와 병합 브랜치 정리를 유지하고, [Issue #27](https://github.com/plcmanjp/excel-cad-label-maker/issues/27)의 남은 로컬 워크트리와 복구 근거를 보존한다.

## 현재 상태

- main의 내용과 같은 하네스 변경 커밋 7cd8dae를 사용자 승인으로 병합했다. 병합 커밋 06486bd의 전체 파일 트리는 직전 main c6b31f9와 같다. 로컬 및 원격 branch는 main 하나다.
- 원래 staged/unstaged/untracked 변경은 stash b6b5211과 OneDrive 및 OS Temp 밖의 파일 백업, Git metadata 및 독립 검증 bundle에 보존했다. stash를 최신 main에 적용하지 않았다.
- 완료된 .local QC/빌드 폴더 5개를 휴지통에 옮겼다. .local/baseline과 uia-qc-env 및 worktrees/issue-22는 남아 있다. 마지막 워크트리는 같은 커밋 7cd8dae의 detached HEAD이며 미커밋 변경을 유지한다.
- 공개 latest는 0.4.2다. 원본, 배포물, 법적 고지와 QC 요약 및 Notion의 소개 초안과 이미지 원본은 유지한다. 제품 변경과 새 공개 배포는 수행하지 않았다.

## 주요 결정

- .local 전체의 파일을 외부에 복사하고 SHA-256을 검증했다. 원시 감사 자료와 개인 절대 경로는 Git에 넣지 않는다. 백업과 stash, bundle 및 실제 휴지통 receipt는 정리 대상이 아니다.
- 브랜치 삭제는 main의 실제 ancestry와 원격 반영을 확인한 뒤 git branch -d로 수행했다. 남은 dirty 워크트리의 폴더와 Git 등록은 제거하지 않았다.
- .local/baseline의 실행 파일은 원본 0.1.0 패키징 입력이다. 재사용 환경과 함께 보존한다. 실제 Shell Restore는 실행하지 않았으며 bin/백업의 파일 동일성을 전체 ACL/cloud 동일 복원으로 확대하지 않는다.
- 종료된 #14의 실제 CAD와 회사 직원 PC 사용자 수용 및 #20의 배율 검사 제외를 유지한다. 원개발자 직장인과 후속 개발자 plcmanjp의 크레딧과 공개 0.4.2의 source/tag/자산은 유지한다.

## 검증 결과

- 병합 대상 커밋의 변경 경로 6개가 main과 동일한 blob/mode였다. 실제 병합 index tree와 병합 후 tree도 직전 main과 같다. 병합에 따른 파일 변경은 0개다.
- stash를 포함한 sync-preserved.bundle을 독립 bare 저장소에 읽어 fsck와 stash ref를 확인했다. 삭제한 branch들의 커밋도 bundle에 보존돼 있다.
- 휴지통의 5개 항목은 파일 3,969개, 414,325,757bytes다. 원경로 부재와 실제 $I 원경로, $R의 전체 파일/디렉터리 집합 및 모든 파일 SHA-256을 대조했다. 보존한 .local 경로도 백업 manifest와 일치했다.
- detached 전환 전후의 워크트리 status와 staged/unstaged diff 지문은 같다. 사용자 승인 범위의 branch 참조와 HEAD 연결만 변경했으며 소스와 검증 자료는 보존한다.
- 기록 변경의 저장소 및 공개 문서 검사와 diff-check는 PASS다. 최종 기록 commit의 CI와 동기화 상태는 실제 결과와 원격 readback을 기준으로 한다.

## 미해결 사항

- Issue #27은 OPEN이다. .local/worktrees/issue-22의 이전 운영 보존 planner는 pip의 공개 CA 인증서 cacert.pem을 비밀 파일로 분류해 차단했다. 해당 폴더의 회수는 재시도하지 않았고 차단 예외는 승인되지 않았다. 이번 승인은 내용 변경 없는 병합과 branch 삭제에 한정한다.
- 원래 미커밋 작업을 다시 사용할 필요가 있으면 검증된 백업과 stash를 확인한다. 최신 main으로 자동 복원하거나 폐기하지 않는다.

## 다음 작업

1. dirty 워크트리 회수는 차단 원인 해결 또는 명시적인 예외 결정 후 현재 원본과 전체 백업을 다시 대조해 진행한다. 그 전까지 폴더와 등록을 보존한다.
2. 이전 미커밋 작업의 재사용은 별도 범위로 결정하고 stash와 복구 자료를 유지한다.
3. 블로그 발행 시 기존 Notion 본문과 이미지 원본을 사용하고 공개 0.4.2와 기존 사용자 수용 범위를 유지한다.
