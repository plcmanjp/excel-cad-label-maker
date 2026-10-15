# r025: 0.4.2 정식 배포와 세션 마무리

| 항목 | 값 |
|---|---|
| 문서리비전 | r025-release-042-wrap |
| 작성일시 | 2026-10-15 20:34 (KST) |
| 작성모델 | GPT-6 Codex |
| 담당에이전트 | Director + code-reviewer |

## 요약

- 사용자 승인에 따라 PR #29를 main에 병합하고, 시작 업데이트 팝업 복원을 포함한 0.4.2 정식 Windows x64 ZIP을 공개 latest로 배포했다. #28은 병합으로 종료됐다.
- 원격과 세 독립 checkout의 병합 브랜치는 독립 복구 bundle 검증 및 main 조상 확인 후 정리했다. 원래 작업 폴더의 미커밋 변경과 중복 등록은 보존했다.
- 파일 청소는 공용 도구의 필수 manifest 부재와 linked worktree 지원 경계 때문에 차단됐다. 삭제/휴지통 이동은 0파일, 0bytes이며 #27을 OPEN으로 유지한다.

## 커밋 (이번 세션)

- 08db8db0176934b07c9c765a8ad0956a7528752a: 앱과 배포 설정의 0.4.2 버전, 릴리스 노트와 사용자 안내 준비.
- 715446731bdc00d48ae41e4df2e96534bff8e286: PR #29 병합.
- 8498b03412e8a80c844967dca13803b145d11436: 병합과 브랜치 정리 진행 상태. 정식 build/tag의 고정 source commit이다.
- 이 journal과 CURRENT 및 release042-results.json의 기록 전용 commit은 공개 tag/자산을 변경하지 않는다. 정확한 최종 head CI와 동기화 결과는 #30의 완료 댓글에서 확인한다.

## 작업번호

- [#30](https://github.com/plcmanjp/excel-cad-label-maker/issues/30): 이번 병합/배포/세션 마무리 작업지시. 최종 기록의 CI와 readback 후 완료 댓글과 종료를 수행한다.
- [PR #29](https://github.com/plcmanjp/excel-cad-label-maker/pull/29)는 병합됐고 #28은 CLOSED다. #14/#20의 미충족 현장 조건과 #27의 실제 청소 조건은 남긴다.

## 검증

- 최종 PR head의 push CI 38725828637, PR CI 38725833267과 공식 source main CI 38726264533이 PASS다. 독립 읽기 전용 소스 및 실제 패키지 검수는 미해결 finding 0개다.
- fresh clean main, Python 3.13.15와 고정 의존성의 표준 정식 빌드에서 제품 130개 PASS. 알림 회귀 10개 근거는 issue28-results.json에 있다. 로컬 release guard는 17개 PASS, symlink 생성 권한으로 1개 SKIP이다.
- 정식 ZIP 1,130멤버와 receipt 1,128파일, runtime source 16개, 외부 고지 원본 63개, provenance/라이선스 byte와 모든 hash를 대조했다. 실제 실행 후에도 압축 해제된 공식 파일 전부가 ZIP과 같고, 별도 QC 빌드의 1,126파일 receipt 및 source hash도 일치했다.
- 공개 ZIP은 29,621,887bytes, SHA-256 `2f65466d66a94d01ba9c427ce6f89e42dde90c8a1514381e8710a93e7d6db6af`다. EXE는 `a25e37bd0417e8a963fa32f84a8fe2dbfc0cf637f9d22e5fcf9463b232f9df36`이다.
- 실제 정식 ZIP EXE의 버전/아이콘/Arial 기본값을 확인했다. 합성 Excel을 native 파일 선택기로 읽고 경고를 확인한 뒤 3라벨/8칸/중간 빈칸 1개 DXF 저장에 성공했다. 재읽기 결과 한글과 영문/숫자, 배치/치수/외곽선 및 ARIAL/arial.ttf가 일치했고 audit error/fix는 0개다. 원본 workbook bytes는 같았다.
- 실제 저장 DXF는 18,368bytes이며 SHA-256 `ec8c1cf5110dfdf748aae4c803f71717195cf3ac507be681f46592f37e1ad6a4`다. 정식 EXE의 수동 조회에서는 더 새로운 정식 버전 없음 안내를 확인했다.
- 공식 source에서 만든 별도 frozen QC 앱은 비교 버전 0.0.1과 실제 GitHub API로 공개 0.4.2를 찾아 입력 전 시작 팝업을 표시했다. 나중에 닫기와 수동 재열기도 확인했다. 정상 공식 앱에는 비교 버전 override가 없다.
- 기존 공개 0.4.1 ZIP을 다시 내려받아 기존 hash/EXE bytes가 같음을 확인했다. 그 앱의 수동 버튼에서 현재 0.4.1/최신 0.4.2 안내를 확인했다. 기존 0.4.1은 한 번 수동 갱신해야 하며 시작 자동 알림은 0.4.2부터 적용된다.
- draft 본문/저장소/tag/source/두 asset의 이름/크기/hash를 확인한 후 2026-10-15T11:24:35Z에 공개했다. latest API와 remote annotated tag의 peeled source를 재확인했고 공개 ZIP과 checksum 재다운로드 bytes도 같다. 기존 공개 배포물은 교체하지 않았다.
- 최초 artifact 검증 helper가 내부 중첩 함수 조회 KeyError로 추출 전 중단했다. 별도 helper가 실제 .md에서 .txt로 변환되는 이름 규칙을 독립 적용해 모두 통과했다. draft의 tag 조회 404는 list/id endpoint에서 같은 draft를 확인해 해결했고 중복 배포를 만들지 않았다.
- 모든 이번 GUI 검증 앱을 닫았고 사용자 Explorer와 Paseo는 유지했다. 원시 로그, 합성 fixture, 설정 격리 폴더와 bundle/독립 복구 검증본은 OneDrive 밖 로컬 증거 폴더에 보존했다.

## 미해결 이슈

- #27: 네 checkout 모두 committed cleanup manifest가 없다. 공용 v1의 workspace identity와 실제 운영 linked worktree 회수도 지원 확인이 필요하다. Scan/Plan/Recycle/Restore를 실행하지 않았고 정책/manifest를 추정하거나 경로 별칭/등록 제거로 우회하지 않았다.
- 원래 checkout의 index/HEAD, staged/unstaged diff와 status 내용 지문은 사전/사후 같았다. 원격 추적 main/feature와 tag refs 변화는 관찰됐다. 이 세션은 그 폴더에서 fetch/reset/prune/ref 쓰기를 실행하지 않았고 갱신 원인은 미확정이다. 전체 refs 무변경이나 원래 폴더의 동기화 완료를 주장하지 않는다.
- #14/#20: 실제 AutoCAD 렌더링, 별도 PC/원본 빌드 대응과 초보 사용자/실제 OS 배율 검증은 남아 있다. Arial/Gulim 한글 표시 정상은 사용자 보고이며 독립 CAD 렌더링 근거와 구분한다.
- 물리적 Explorer 드롭은 도구 차단으로 NOT_RUN이다. 이번 패치는 파일 선택기 가져오기를 확인했다. Excel 왕복은 기존 #22 근거를 유지하며 재실행하지 않았다. native 모달 타이밍과 물리적 네트워크 차단도 재실행하지 않았고 실제 Tk grab 지연과 결정적 실패 검사를 별도로 유지한다.
- MIT는 사용자의 원본 소스 권리 양도 확인에 근거하며 계약서의 독립 법률 검토를 뜻하지 않는다. 보관 원본 EXE 0.1.0과 외부 구성요소는 개별 조건을 유지한다.

## 다음 우선순위

1. #27의 지원 정책/manifest와 원래 checkout 소유권/중복 등록/ref 갱신 주체를 확정하고 검증 가능한 회수/복원 계획을 마련한다.
2. #14와 #20의 실제 현장 조건을 각각 충족한 뒤 해당 이슈를 종료한다.

## 자가점검 회고

- 정식 source/tag와 이후 기록 commit을 구분하고 공개 bytes를 재다운로드해 검증했다. 기존 앱의 수동 알림과 새 코드의 자동 팝업도 각각 확인했다.
- 청소 요청을 근거 없이 완료 처리하지 않고 파일 0개 및 refs 관찰 차이를 기록했다. 배포 PASS와 미실행 CAD/드롭/현장 항목을 분리했다.
