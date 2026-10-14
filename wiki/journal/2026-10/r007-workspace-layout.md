# r007 - 문서와 개발 및 배포 경로 정리

| 항목 | 값 |
|---|---|
| 문서리비전 | r007-workspace-layout |
| 작성일시 | 2026-10-14 14:35 (KST) |
| 작성모델 | GPT-6 (Codex) |
| 담당에이전트 | Codex Director /root |

## 요약

루트 자료를 wiki, project와 release로 정리했다. 현재 문서와 참고 자료는 wiki/guides, wiki/reference 및 wiki/harness로, 앱 소스와 개발 도구 및 검수는 project로, 배포 구성과 패키징 도구 및 고지와 산출물은 release로 이동했다. 루트에는 README.md와 AGENTS.md 및 숨김 도구 설정을 유지한다.

Project의 소문자 변경은 임시 경로를 거치는 Git rename으로 기록했다. .venv와 .local은 기존 위치에 보존하고 개발 출력은 project/dist, 캐시는 project/build, 배포 출력은 release/artifacts를 사용한다. 빌드와 패키징 root 계산, CI, 보호 검사, manifest source_path와 현재 문서 링크를 함께 수정했다.

## 커밋 (이번 세션)

- `bbf2a10e3843833d0a1c6575734e42cf2254e8ba`: 경로 재구성 및 실행 도구와 CI, 문서 링크 수정.
- `49714469d8cb72aaa96399a97b79c00ae778ddea`: 검증된 PR #9의 main 병합.
- 완료 검수 기록과 이 스냅샷은 후속 한국어 문서 commit으로 기록한다.

## 검증

- 로컬 제품 33, 하네스 22, 빌드 보호 2 및 배포와 baseline 12개 중 68 PASS, native symlink 1개 권한 부족 SKIP다. PR CI와 병합 main CI에서 69개 모두 실제 통과했다. PR run은 38517021549, main run은 38517225202다.
- 저장소의 루트 분류, 현재 Markdown 링크, 원본 provenance와 UTF-8 및 역할 연결 검사가 PASS다. 문서 링크와 잘못 배치한 루트 자료를 검사하는 예방 검증을 기존 repository checker에 추가했다.
- 원본 Python, PNG와 ICO, 외부 고지 63개 및 기존 공개 ZIP 2개의 이동 전후 hash 68개가 일치했다. 제품 Python, 의존성 잠금, 과거 QC JSON과 journal, 릴리스 노트 및 기존 사용자 자료도 기준 Git byte와 일치했다.
- 새 경로의 개발, 정식 및 별도 업데이트 QC 빌드와 아이콘 검사 및 receipt 생성이 PASS다. 소스 실행 스크립트와 개발 및 정식 EXE의 실제 창과 정상 UI를 Computer Use로 확인했다.
- baseline ZIP을 실제 생성해 원본 EXE hash, flat README 링크와 ZIP 무결성을 확인했다. 독립 검수에서 발견한 baseline README 링크 회귀는 전용 사용자 안내와 flat 파일 매핑으로 수정했고 delta 검수가 PASS다.
- 깨끗한 병합 main에서 정식 앱과 검증 ZIP을 생성했다. receipt의 main commit과 source_dirty=false, ZIP 1,905개 파일 및 manifest hash를 대조했다. 이 ZIP은 release/artifacts/layout-qc-4971446에만 보관하고 공개하지 않았다.
- GitHub의 기존 v0.1.0 및 v0.2.0 ZIP 자산 ID, 크기와 digest가 유지됐다. 이번 작업에서 공개 릴리스를 새로 만들거나 교체하지 않았다.

상세 결과는 project/qc/workspace-layout-results.json, 원시 빌드 및 CI 로그와 hash 목록은 Git에서 제외되는 .local/layout-qc에 있다.

## 작업번호

- [Issue #8](https://github.com/plcmanjp/excel-cad-label-maker/issues/8): 경로 재구성, 병합 후 CLOSED.
- [PR #9](https://github.com/plcmanjp/excel-cad-label-maker/pull/9): 독립 검수와 CI 통과 후 main 병합 완료.

## 다음 우선순위

Issue #2의 실제 CAD에서 한글과 글꼴, mm 및 레이어 검증, Python 없는 별도 Windows PC 실행 및 원본 이용 조건 확인을 이어간다. 경로 정리 및 단일 PC 검사를 이 항목들의 PASS로 확대하지 않는다.

## 자가점검 회고

분류 이동과 실행 참조를 함께 검증했으며 불변 자료와 게시 파일은 보존했다. Windows의 case rename과 baseline ZIP의 flat 안내 경로는 일반 문서 링크 검사만으로 충분하지 않아 Git 경로와 실제 ZIP 대조 및 독립 검수로 확인했다.
