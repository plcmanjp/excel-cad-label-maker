# 작업 저널 (CURRENT)

## 목표

- 0.4.1 배포 세션을 마무리하고 [Issue #27](https://github.com/plcmanjp/excel-cad-label-maker/issues/27)의 안전한 워크스페이스 청소 재개 조건을 유지한다.

## 현재 상태

- [0.4.1](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.4.1)은 MIT와 Arial 기본값을 포함한 정식 latest다. PR #25는 병합됐고 #24, #26은 CLOSED다.
- 청소 사전 확인은 부분 완료다. 실제 삭제와 휴지통 이동은 0파일, 0bytes이며 #27은 OPEN이다. 원래 작업 폴더는 수정하지 않았고 두 독립 checkout의 작업 기준은 main이다.

## 주요 결정

- 미커밋 작업, 원본, 배포물, 검증 근거, 백업과 개발 환경을 보존한다. manifest 부재를 임시 allowlist나 다른 도구로 우회하지 않는다.
- tag v0.4.1과 공개 자산의 제품 commit은 673d7a6이다. 내부 마무리 기록은 제품과 공개 자산을 바꾸지 않는다.

## 검증 결과

- [정식 배포 검증](../../../project/qc/release041-results.json)과 ab12be0의 원격 CI 38710693104는 PASS다. 최신 release와 로컬 ZIP/EXE hash를 다시 대조했다.
- 원래 checkout의 index, HEAD, refs 및 작업트리 등록 metadata, staged/unstaged diff와 status 지문이 사전 확인 전후 일치했다. 전체 untracked/ignored bytes의 백업이나 검증을 의미하지 않는다.

## 미해결 사항

- 세 checkout에 공용 도구가 요구하는 committed 청소 manifest가 없어 Scan/Plan/Recycle/Restore를 수행하지 않았다. 원래 OneDrive checkout에는 예상 밖 변경과 같은 브랜치를 가리키는 작업 폴더 등록 두 개가 남아 있다. 실제 운영 linked worktree 회수도 공용 도구 지원 밖이다.
- #14의 CAD/별도 PC/원본 빌드 대응과 #20의 실제 사용자/OS 배율 검증은 OPEN이다. 원개발자 소스 권리 양도에 대한 관리자 확인과 독립 계약 감정은 구분한다.

## 다음 작업

1. #27에서 대상 저장소의 청소 정책과 지원되는 manifest 범위를 확정한다.
2. 원래 작업 폴더의 변경 소유권과 복구 자료 및 작업트리 연결을 확인한다. 그 전에는 reset, prune이나 자료 회수를 하지 않는다.
3. 지원 조건이 충족되면 새 inventory와 정확한 휴지통 계획으로 청소 및 복원 검증을 진행한다. #14와 #20의 현장 검증은 해당 환경에서 이어간다.
