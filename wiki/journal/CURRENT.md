# 작업 저널 (CURRENT)

## 목표

- [Issue #28](https://github.com/plcmanjp/excel-cad-label-maker/issues/28)의 시작 시 업데이트 팝업을 복원하고 수동 버튼과 모달 지연 동작을 검증한다.

## 현재 상태

- [0.4.1](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.4.1)은 MIT와 Arial 기본값을 포함한 정식 latest다. PR #25는 병합됐고 #24, #26은 CLOSED다.
- fix/issue-28-startup-update에서 자동 조회의 새 버전 결과를 기존 팝업에 연결하고 사용자 설명 및 회귀 검사를 수정했다. 실행 검증은 진행 중이다.
- 청소 사전 확인은 부분 완료다. 실제 삭제와 휴지통 이동은 0파일, 0bytes이며 #27은 OPEN이다. 원래 작업 폴더는 수정하지 않았고 두 독립 checkout의 작업 기준은 main이다.

## 주요 결정

- 미커밋 작업, 원본, 배포물, 검증 근거, 백업과 개발 환경을 보존한다. manifest 부재를 임시 allowlist나 다른 도구로 우회하지 않는다.
- tag v0.4.1과 공개 자산의 제품 commit은 673d7a6이다. 내부 마무리 기록은 제품과 공개 자산을 바꾸지 않는다.

## 검증 결과

- 기존 배포와 마무리 기록 d41f074의 원격 CI 38715132086은 PASS다. #28 변경은 별도 검증한다.
- 원래 checkout의 index, HEAD, refs 및 작업트리 등록 metadata, staged/unstaged diff와 status 지문이 사전 확인 전후 일치했다. 전체 untracked/ignored bytes의 백업이나 검증을 의미하지 않는다.

## 미해결 사항

- 세 checkout에 공용 도구가 요구하는 committed 청소 manifest가 없어 Scan/Plan/Recycle/Restore를 수행하지 않았다. 원래 OneDrive checkout에는 예상 밖 변경과 같은 브랜치를 가리키는 작업 폴더 등록 두 개가 남아 있다. 실제 운영 linked worktree 회수도 공용 도구 지원 밖이다.
- #14의 CAD/별도 PC/원본 빌드 대응과 #20의 실제 사용자/OS 배율 검증은 OPEN이다. 원개발자 소스 권리 양도에 대한 관리자 확인과 독립 계약 감정은 구분한다.

## 다음 작업

1. #28의 회귀 및 제품 검사, 실제 GitHub 조회를 이용한 자동 팝업/수동 재열기와 개발 빌드를 확인하고 PR을 발행한다.
2. #27에서 청소 정책과 manifest 범위 및 원래 작업 폴더의 변경 소유권과 복구 자료를 확정한다. 그 전에는 reset, prune이나 자료 회수를 하지 않는다.
3. #14와 #20의 현장 검증은 해당 환경에서 이어간다.
