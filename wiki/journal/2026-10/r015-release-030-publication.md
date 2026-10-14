# r015 0.3.0 정식 배포와 공개 검증

| 항목 | 값 |
|---|---|
| 문서리비전 | r015-release-030-publication |
| 작성일시 | 2026-10-15 07:01 (KST) |
| 작성모델 | GPT-6 (Codex), GPT-6.1 (검수) |
| 담당에이전트 | Codex Director와 code-reviewer Specialist |

## 요약

- 사용자의 QC 후 배포 지시로0.3.0 버전과 사용자 안내 및 릴리스 노트를 준비하고 PR #21을 main에 통합했다. tag 대상은 clean main c7499c309a24dd48d83400e17983c03af98442f2다.
- 설정 보기 질문에는 왼쪽 설정과 좁은 창의 설정/결과 전환으로 답했고 팝업으로 바꾸지 않았다. 라벨 편집/추가와 도움말 모달은 기존 승인 구현을 유지했다.
- 정식 빌드와 압축 해제 QC, 독립 검수와 main CI 뒤 ZIP/체크섬을 업로드한 draft를 검증하고 v0.3.0을 latest 정식 릴리스로 공개했다. 기존 자산과 원본, 고지 및 과거 기록은 보존했다.

## 검증

| 경계 | 실행과 결과 |
|---|---|
| 버전/문서 | app_version.py와 app-release.json의0.3.0/v0.3.0 일치, 사용자 문서 검사 PASS. 독립 검수의 이전 앱 버튼 위치 안내1개를 보정했다. |
| Git/CI | canonical plcmanjp author/committer의 local merge commit으로 main을 push했고 PR21 MERGED를 API로 확인했다. feature push/PR와 main의 verify/product PASS. |
| 정식 빌드 | build-dev.ps1 -Release returncode0, 제품99개 PASS 및 ignored Tk 오류0개. clean main receipt와 source14개/아이콘2개/의존성 잠금 hash 일치. |
| 패키징 | package-app-release.py가 clean main, 버전/commit/파일 및 안전 경로를 검증했다. ZIP1129개, receipt1127개, manifest1128개, 필수 TXT와 Markdown0개 확인. |
| 독립 artifact | 실제 ZIP/EXE와 TXT, 외부/런타임 고지63개 및 기존95개 보호 hash가 일치하고 남은 finding0개. pandas PYZ 모듈 없음. |
| 실제 정식 앱 | 새 폴더에 ZIP을 풀고 실제 드롭으로20개/60칸 수용. 편집/추가 후21개/61칸 저장17단계10.115초, 새 작업과 직접 입력/편집/저장/도움말25단계13.226초 PASS. |
| 결과/보존 | DXF2개의 문자, 좌표와 글자 속성, Standard 및7/7, AC1024/mm와 audit0. 원본 Excel bytes/mtime과 패키지 파일 불변. |
| 공개 | 저장소/버전/c7499c3 및 ZIP/EXE SHA 재대조, annotated tag push. draft의 본문과 uploaded 자산2개 hash 확인 뒤 latest 공개. |
| 재다운로드 | 공개 ZIP/체크섬 bytes와1129개 멤버가 로컬과 같고 tag/본문/latest0.3.0/state/digest API readback PASS. |
| 실제 업데이트 |0.3.0 current,0.2.2 available API 결과. 같은 update_notice 코드의 이전 개발 UI0.2.2는 실제 공개 API의 파란 버튼만 표시하며 클릭 때0.3.0 안내. 기존 정식0.2.2도 실제0.3.0 알림을 표시하고 Esc 및 정상 종료. |

- 릴리스 URL은 https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.3.0, release ID는413214565다.
- ZIP SHA-256:6778fc0a101465b4ad4efc864732f8c89c8f8b44f07a349efc36daefbf905e2b, EXE SHA-256:adc30466690dd45a151bbc07898cacfadd1d838e4ac89e96a35fa820e9c821bf다. ZIP은29,590,511 bytes다.
- main CI는 [38641009174](https://github.com/plcmanjp/excel-cad-label-maker/actions/runs/38641009174)다. 근거와 hash는 [배포 QC](../../../release/qc/release-v0.3.0.json)에 있으며 원시 UI/경로와 합성 입력은 Git 제외 .local/release-0.3.0에 보존했다.

## 결정/판단 근거

- 미검증 환경을 PASS로 바꾸지 않고 확인한 Windows/DPI96의 배포물과 입력/저장 및 실제 업데이트만 판정했다. 실제 CAD와 별도 PC는 Issue14, 고배율/초보/마우스 제스처는 Issue20의 OPEN 경계다.
- Computer Use 초기화와 reset1회가 kernel assets 경로 오류로 입력 전 실패했다. 공용 UIA를 사용했고 실제 마우스 더블클릭은 미실행이다.
- 파일 드래그는 Explorer 상세 보기의 행 사각형이 창 밖까지 확장돼 입력 전에 중단했다. 현재 소유권/사각형과 정확한 title/PID를 측정하고 검수 복사본의 폴더만 목록 보기로 바꾼 뒤 INPUT_COMPLETED 및 별도 제품 수용을 확인했다. 실패 원시 기록도 보존했다.
- draft tag 조회404는 기존 draft를 목록에서 찾아 ID로 검증하는 방식으로 해결했다. release를 중복 생성하거나 불확실한 공개를 재시도하지 않았다.
- GitHub 원격 병합의 committer 대신 local merge의 검증된 plcmanjp 귀속을 사용했다. source와 기록을 합친 검증된 main commit에만 tag를 만들었고 force나 기존 자산 덮어쓰기를 하지 않았다.

## 커밋 (이번 세션)

- cd0f10e:0.3.0 버전과 공개 기능 안내 및 릴리스 노트 준비.
- 4fa9918:이전 앱의 업데이트 버튼 위치 안내 보정.
- [c7499c3](https://github.com/plcmanjp/excel-cad-label-maker/commit/c7499c309a24dd48d83400e17983c03af98442f2):PR21 통합과0.3.0 정식 소스. v0.3.0 tag 대상.
- 이 스냅샷과 CURRENT 및 공개 QC는 후속 기록 commit으로 main에 저장하며 릴리스 tag는 이동하지 않는다.

## 작업번호

- Issue20의 승인된 기능과 배포는 완료했고 실제 사용자/환경 수용은 부분 완료다. Issue20과14는 OPEN을 유지한다.

## 다음 우선순위

1. 물리 마우스 더블클릭과 초보 사용자 및 Windows150%/200%를 검증한다.
2. 실제 CAD/별도 PC와 Standard 한글 및 원본 대응을 Issue14 조건에 따라 확인한다.
3. 새 요구사항은 현재 승인 범위와 해당 GitHub Issue에서 처리한다.

## 자가점검 회고

- 후보 개발 EXE를 정식 배포물로 올리지 않고 clean main의 release-build를 별도로 만들고 ZIP 해제 및 동작을 확인했다.
- UIA 전달, 제품 수용과 DXF 의미, 시각/환경 수용을 분리했다. 실제 공개 API 결과와 합성 응답을 혼동하지 않았다.
- 호출 환경의 경로/인코딩과 화면 가림 오류를 제품 오류로 숨기거나 PASS로 바꾸지 않았다. 기존 자산과 고지/원본/기록을 보존하고 검사에 사용한 소유 앱과 새 Explorer 창만 정상 종료했다.
