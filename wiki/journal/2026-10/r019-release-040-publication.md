# r019: 0.4.0 정식 배포와 브랜치 정리

| 항목 | 값 |
|---|---|
| 문서리비전 | r019-release-040-publication |
| 작성일시 | 2026-10-15 17:11 (KST) |
| 작성모델 | GPT-6 Codex |
| 담당에이전트 | Director와 읽기 전용 code-reviewer |

## 요약

- 사용자가 대상을 PR #23으로 정정하고 main 병합, 0.4.0 공개 배포와 완료 이슈/병합 브랜치 정리를 승인했다.
- 배포 전 독립 검수가 찾은 ZIP README의 이전 열 입력 안내를 보정하고 최종 head a831f68의 push/PR CI를 확인했다. PR #23을 일반 merge commit 156b4b9로 병합했으며 Issue #22는 자동 CLOSED됐다.
- clean main에서 정식 빌드하고 ZIP 전체를 새 폴더에 풀어 실행했다. 정식 latest v0.4.0을 공개하고 공개 ZIP과 체크섬의 재다운로드 바이트 일치를 확인했다.
- 원격과 독립 빌드 checkout은 main만 남겼다. 원래 OneDrive 저장소의 index 읽기 오류가 해결되지 않아 그 로컬 ref와 index/HEAD/worktree는 보존했다.

## 커밋 (이번 세션)

- a831f687c1489632a3a06542c8fc143e06746ee8: 0.4.0 사용자 안내와 릴리스 노트 보정.
- 156b4b934dcfa7b6e717844e023d7c389807a527: PR #23의 main 병합 및 정식 빌드/tag 대상.
- 이 기록과 배포 QC JSON은 이후 기록 전용 commit에 포함한다. tag와 공개 자산은 변경하지 않는다.

## 작업번호

- [PR #23](https://github.com/plcmanjp/excel-cad-label-maker/pull/23): MERGED.
- [Issue #22](https://github.com/plcmanjp/excel-cad-label-maker/issues/22): CLOSED. [배포 결과 exact readback](https://github.com/plcmanjp/excel-cad-label-maker/issues/22#issuecomment-6187537717) PASS.
- [0.4.0 정식 릴리스](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.4.0): published 2026-10-15T08:06:07Z, latest, prerelease=false. ZIP과 SHA256SUMS.txt 두 자산 uploaded.

## 검증

- 환경: Windows x64, Python 3.13.15, Tk 8.6, 잠금 의존성. 사용자 설정을 분리하고 공개 가능한 합성 workbook만 사용했다. 원본과 이전 릴리스는 보존했다.
- 변경 유형: 배포 안내 보정, 정식 패키지/원격 공개 및 Git ref 정리. cwd는 OneDrive 밖 독립 clone이며 절대 개인 경로는 공개 기록에서 제외했다.
- a831f68의 push 38701972699와 PR 38701978030, merge main 38702539537 CI success를 실제 head SHA와 대조했다.
- `project/scripts/build-dev.ps1 -Release`: 128개 제품 검사 PASS, TXT/법적 고지와 아이콘 검사 PASS. receipt는 release-build, source_dirty=false, 제품 commit 156b4b9다.
- `release/scripts/package-app-release.py --output release/artifacts/v0.4.0`: ZIP 1,129멤버, 모든 manifest/file 해시와 경로 및 중복 이름 검증 PASS. 독립 검수가 README/NOTICE/CREDITS와 외부 원문 63개 및 provenance 일치를 확인했고 미해결 finding은 0개다.
- 압축 해제 EXE의 버전/아이콘과 안내 오른쪽 여백, 파일 선택 Excel 입력 PASS. 3라벨/8칸, 중간 빈 칸 1개를 DXF로 저장하고 `issue22-verify-dxf.py`로 문자/좌표/높이/폭을 대조했다. DXF audit 오류와 수정 0, 입력 workbook byte 불변 PASS.
- ZIP 29,620,001 bytes, SHA-256 `fe73d2a6e4cb1fe2cb1067add9d3a3d7f75db373778b5930b753ae8c5e047142`. EXE SHA-256 `78d8f58e9211b0d51581d0892aa861abfc90bc79684e12db994674d443d3f3d1`.
- 공개 직전 저장소, clean main, 버전/tag, 업로드 자산 digest/size/state와 본문을 확인했다. 공개 후 원격 tag의 peeled commit, latest API와 두 자산을 읽고 `gh release download`로 byte 비교 PASS.
- 정식 EXE 수동 업데이트 조회 PASS. 실제 이전 공개 0.3.0 ZIP EXE에서 최신 0.4.0 알림과 Escape 닫기 PASS. live API 비교도 available/v0.4.0과 고정된 릴리스 URL을 반환했다.
- 실제 Explorer 간 드롭은 Computer Use가 다른 창으로 향하는 드래그 끝점을 차단해 미검증이다. 파일 선택 경로 검증으로 구분했다. 전체 Excel clipboard 왕복과 Tk 배율 검증의 이전 기록은 issue22-results.json과 issue22-ui-results.json에 보존했다.
- 브랜치 정리 전 refs/reflog를 기록하고 모든 reflog commit이 전체 ref에서 도달 가능함을 확인했다. `git bundle create --all`과 `git bundle verify` PASS, 병합 조상 확인 후 feature를 `branch -d`하고 원격 추적 ref를 prune했다. 파일/폴더와 worktree 등록은 제거하지 않았다.
- 복구 bundle SHA-256 `898eacad24c4f7c52ba9155268ff1d42a6f4128b785b4b7ea448a84e8a0f2a8e`와 로컬 세부 로그/DXF/fixture는 Git 제외 증거 폴더에 보존한다.

## 미해결 이슈

- #20: 초보 사용자 수행 시간과 실제 OS 150/200% 배율 확인이 남아 OPEN이다. Tk 배율 시뮬레이션을 실제 OS 결과로 바꾸지 않았다.
- #14: 실제 CAD, Python 없는 별도 PC, 원본 대응 및 구체적인 이용 조건이 남아 OPEN이다.
- 원래 OneDrive index 읽기 복구와 그 로컬 브랜치 정리는 차단 상태다. index 재생성/삭제나 worktree 제거를 하지 않았다.
- 실제 Explorer 드롭은 자동화 도구의 창 경계 제한이 없는 사용자 환경에서 다시 확인한다.

## 다음 우선순위

1. #20의 사용자/OS 배율과 실제 Explorer 드롭을 실제 환경에서 확인한다.
2. #14의 CAD와 별도 PC 및 권리 근거를 확인한다.
3. 원래 index가 정상으로 읽힌 후 로컬 상태와 복구 자료를 확인하고 Git 동기화/브랜치 정리를 재개한다.

## 자가점검 회고

- 패키지 사용자 안내의 실제 포함 경로를 검수해 소스 UI와 배포 ZIP의 설명 차이를 수정했다. 제품 빌드와 공개 후 자산 readback을 각각 확인했다.
- 성공한 검사와 미검증 환경, 원격 ref 정리와 원래 저장소의 차단 상태를 분리했다. 이전 자산과 개인 자료를 정리 대상으로 확대하지 않았다.
