# r022: MIT 적용과 0.4.1 정식 배포

| 항목 | 값 |
|---|---|
| 문서리비전 | r022-mit-release-041 |
| 작성일시 | 2026-10-15 18:04 (KST) |
| 작성모델 | GPT-6 Codex |
| 담당에이전트 | Director와 읽기 전용 code-reviewer |

## 요약

- 관리자가 원개발자에게 소스 권리를 양도받았다고 명시 확인한 내용을 근거로 MIT를 적용했다. 계약 원문의 법적 효력을 독립 감정했다고 주장하지 않는다.
- 저작권자는 plcmanjp로 표시하고 원개발자 직장인의 크레딧과 외부 원문을 유지했다. 소스와 0.4.1 후속 앱의 MIT와 보관 원본 EXE 0.1.0의 기존 조건을 구분했다.
- Arial 기본값 변경과 함께 PR #25를 main에 병합하고 fresh clean main 정식 Windows 빌드/ZIP을 검수한 뒤 v0.4.1 latest로 공개했다.
- 공개 자산을 다시 내려받아 byte 일치를 확인하고 실제 이전 공개 0.4.0 EXE에서 최신 0.4.1 알림을 확인했다.

## 커밋 (이번 세션)

- e4ae8f825fe5b0be20ca86441842d967ec2c3e50: MIT 원문/고지와 LICENSE.txt 패키징 및 보호 회귀, 0.4.1 설정.
- 673d7a626331bc31dac9838f603759235ea2dcbd: PR #25 병합, 정식 빌드와 v0.4.1 tag 대상.
- 이 journal, CURRENT와 release041-results.json은 이후 기록 전용 commit에 포함한다. 공개 자산/tag는 변경하지 않는다.

## 작업번호

- [PR #25](https://github.com/plcmanjp/excel-cad-label-maker/pull/25): MERGED. #24와 #26은 CLOSED다.
- [Issue #26](https://github.com/plcmanjp/excel-cad-label-maker/issues/26): 권리 확인 입력, 적용 범위와 공개 작업지시.
- [v0.4.1](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.4.1): published 2026-10-15T09:01:41Z, 정식 latest, 두 자산 uploaded.
- #14는 소스 권리 양도에 대한 관리자 확인과 MIT 적용 범위를 exact readback으로 갱신했다. CAD/별도 PC/원본 빌드 대응은 OPEN이다.

## 검증

- Windows x64, Python 3.13.15/Tk 8.6과 잠금 의존성으로 OneDrive 밖 새 독립 checkout에서 수행했다. 합성 한글 workbook과 격리 설정을 사용했다.
- 변경 유형은 기본 글꼴과 라이선스/패키징 보호 및 공개 배포다. product 128개, harness 22개 PASS. 배포 보호 로컬 17 PASS/1 symlink 권한 SKIP, CI 18 PASS다.
- source head e4ae8f8의 push 38708976345와 PR 38708982670, merge main 38709393113 success를 실제 SHA와 대조했다. 독립 소스/실제 ZIP delta 검수의 미해결 finding은 0개다.
- LICENSE는 GitHub 표준 MIT 템플릿과 공백을 제외한 원문이 일치한다. GitHub의 저장소 license 감지도 MIT다. LICENSE.txt 원문, root LICENSE 및 manifest license=MIT와 hash 일치를 확인했다.
- `project/scripts/build-dev.ps1 -Release`와 `release/scripts/package-app-release.py --output release/artifacts/v0.4.1`: clean main 673d7a6, release-build/source_dirty=false. ZIP 1,130멤버와 receipt 1,128파일, 외부 원문 63개와 provenance, TXT/아이콘 검증 PASS.
- 실제 압축 해제 EXE는 0.4.1/Arial을 표시했다. 합성 한글 3라벨/8칸과 중간 빈 칸을 파일 선택으로 불러와 DXF 저장 후 issue22-verify-dxf.py로 문자/좌표/높이/폭과 audit 오류/수정 0을 확인했다. 모든 TEXT는 ARIAL/arial.ttf이고 입력 byte는 불변이다.
- ZIP 29,619,316 bytes, SHA-256 `046716e73c0c350245da02858fc2e25c6869d9ab11bdc55871399ccf459bfc16`. EXE SHA-256 `fe03ace5c6a51c6cddd0f7409ce070552db01978ffc13cac3acdffc54d5436eb`. LICENSE SHA-256 `7f480cc658b029e3d8f62115121093925bcdce2d33d9eeff5c0af76b57347492`.
- 공개 직전 저장소/버전/main/tag/라이선스 및 자산 hash를 확인하고 draft 업로드 후 본문과 두 자산 digest/state를 대조해 공개했다. 공개 latest와 remote peeled tag, ZIP/체크섬 재다운로드 byte 비교 PASS.
- 실제 공개 0.4.0 ZIP을 기존 검증 hash와 대조하고 실행해 최신 0.4.1 알림과 Escape 닫기를 확인했다. 현재 0.4.1의 수동 조회도 정상이다.
- 원격 feature 자동 삭제 후 source checkout의 ref/reflog 도달 가능성을 확인하고 전체 history bundle을 검증해 보존했다. 병합 조상 확인 후 로컬 feature와 stale remote-tracking ref를 정리했다. 새 정식 checkout도 main이며 원래 OneDrive checkout과 모든 자료는 보존했다.
- root LICENSE의 허용 목록 등록 누락은 저장소 검사에서 검출돼 보정했다. 잘못된 로컬 Python subprocess 경로는 검사가 시작되기 전 실패했고 sys.executable을 사용한 재실행이 통과했다. 제품 실행 실패로 집계하지 않았다.

## 미해결 이슈

- 독립 AutoCAD 렌더링, 실제 Explorer 간 드롭과 전체 Excel 왕복은 이번 artifact에서 재검증하지 않았다. 사용자 CAD에서 Arial/굴림 정상 보고와 이전 feature QC는 별도 근거다.
- #20의 초보 사용자/실제 OS 배율과 #14의 남은 현장 항목, 원래 OneDrive checkout의 예상 밖 변경/중복 worktree는 유지한다.

## 다음 우선순위

1. #20/#14의 남은 사용자/OS/CAD/별도 PC 검증을 해당 환경에서 수행한다.
2. 원래 OneDrive checkout의 변경 소유권과 복구 자료를 확인한 후 Git 동기화/정리를 재개한다.

## 자가점검 회고

- 관리자 권리 확인과 법적 독립 검증을 구분하고 원개발자/외부 구성요소/보관 EXE의 경계를 유지했다. 라이선스 포함을 문서뿐 아니라 패키징 거부 검사로 확인했다.
- 이전 배포물을 보존한 새 빌드와 공개 후 byte readback으로 실제 자산의 동일성을 확인했다. 남은 환경 검증을 완료로 확대하지 않았다.
