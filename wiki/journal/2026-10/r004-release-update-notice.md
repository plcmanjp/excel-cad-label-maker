# r004: GitHub 업데이트 알림 구현과 실제 동작 검증

| 항목 | 값 |
|---|---|
| 문서리비전 | r004-release-update-notice |
| 작성일시 | 2026-10-14 12:58 (KST) |
| 작성모델 | GPT-6 기반 Codex 메인 + code-reviewer |
| 담당에이전트 | Director |

## 요약

사용자 승인에 따라 [Issue #3](https://github.com/plcmanjp/excel-cad-label-maker/issues/3)에 작업지시와 핸드오프를 등록하고 원격 body SHA-256 exact readback을 통과했다. main d06ca47과 원격 일치를 확인한 뒤 `feature/issue-3-release-update-notice`로 분기했다.

별도 개발 앱 버전 0.2.0.dev1과 고정 GitHub Releases 최신 조회, Tk 알림 및 수동 확인을 구현했다. TLS 검증, redirect 거부, 3초 요청 timeout과 응답 크기 제한 및 준비된 정식 Windows ZIP과 정확한 저장소 URL 검사를 적용한다. 작업 스레드는 조회와 큐만 사용하고 Tk 접근은 메인 루프에서 수행한다. Excel 대화상자 동안 알림을 지연하며 종료 및 중복 조회를 처리한다.

원본 VERSION, manifest, 소스와 EXE 및 공개 0.1.0을 보존했다. 자동 설치, main 병합과 신규 릴리스 공개는 수행하지 않았다.

## 검증

- 제품 33개, 빌드 보호 2개, 하네스 22개와 기준 릴리스 경계 6개가 통과했다. 공개 경계와 diff 검사도 통과했다. 기존 Excel 및 DXF 회귀를 포함한다.
- 실제 GitHub API는 공개 0.1.0과 준비된 Windows ZIP을 반환했다. 정상 0.2.0.dev1은 current, 검수 비교 입력 0.0.1은 available이었다. 인증 token과 테스트용 원격 릴리스 변경을 사용하지 않았다.
- 정상 Windows EXE의 시작 조회 후 무알림 및 하단 상태, 수동 확인의 새 정식 버전 없음 안내를 실제 화면으로 확인했다.
- 별도 QC EXE가 같은 제품 소스를 사용한다는 SHA-256을 대조했다. 비교 버전 0.0.1로 실제 API를 조회해 새 버전 알림의 현재 및 최신 버전을 확인했다. 나중에는 알림만 닫고 앱을 유지했으며 수동 조회로 알림을 다시 표시했다.
- 릴리스 페이지 열기 버튼이 실제 Chrome 탭에서 해당 저장소의 v0.1.0 페이지를 열었다. 브라우저 URL, 릴리스 제목과 Windows ZIP 링크를 확인했으며 내려받거나 실행하지 않았다.
- 정상 EXE SHA-256은 6bfdb7ef2d9495bd9e0438f0d7e2ea6be3487e9f3e6a91fff429702346dea495, QC EXE는 22ca0ba0f0494faf2d38ee6bfd11b4a346c994ee3b5e038e980bf4cc3a3860f4다. 각각 receipt 파일 1,900개 및 현재 제품 소스 hash를 검증했다. 공개 요약은 `qc/update-notice-results.json`, 원시 경로와 report는 `.local/`에만 보관한다.
- code-reviewer가 네트워크, URL, Tk lifecycle과 버전 경계를 독립 검수하고 수정 finding 없음으로 판정했다. 추가된 QC 패키징과 receipt 종류 및 진입점 hash도 delta 검수에서 통과했다.
- 깨끗한 Windows 환경의 CI는 이 브랜치 push 뒤 GitHub Actions에서 해당 commit으로 확인한다.

## 커밋 (이번 세션)

- 기준 HEAD는 d06ca475be267d08d610762b4a5bf096927d3bf0이다.
- 구현과 검증 기록의 commit은 이 journal 경로의 git log로 확인한다. 결과는 Issue #3 댓글과 검토용 PR로 핸드오프한다.

## 미해결 이슈

브랜치 구현을 main에 반영하거나 새 공개 릴리스를 발행하는 결정은 별도다. 원본 0.1.0 EXE에는 알림 기능을 소급 추가할 수 없으며 알림 포함 앱을 설치한 이후 사용자부터 새 릴리스를 안내받는다. Issue #2의 실제 CAD, 원본 빌드 대응과 권리 조건 및 별도 PC 실행 게이트를 통과한 것으로 확대하지 않는다.

## 다음 우선순위

1. Issue #3 검증 기록과 브랜치 CI를 확인해 main 반영을 판단한다.
2. 실제 CAD 및 원본 권리 조건을 확인한다.
3. 신규 공개 버전의 코드, 앱 버전, ZIP 이름과 hash를 확인한 뒤 해당 릴리스 승인을 받는다.

## 자가점검 회고

단위 검사, 정상 EXE, 별도 검수 비교 버전과 실제 GitHub 및 Chrome 근거를 구분했다. 정상 앱에 숨은 버전 override를 넣거나 실제 릴리스를 시험용으로 바꾸지 않았다. 원본과 공개 경계를 유지하며 재현 가능한 별도 QC 진입점으로 기능을 검증했다.
