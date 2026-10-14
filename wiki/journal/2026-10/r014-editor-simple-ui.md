# r014 출력 라벨 편집과 간단한 화면 구현

| 항목 | 값 |
|---|---|
| 문서리비전 | r014-editor-simple-ui |
| 작성일시 | 2026-10-15 01:42 (KST) |
| 작성모델 | GPT-6 (Codex), GPT-6.1 (검수) |
| 담당에이전트 | Codex Director와 code-reviewer Specialist |

## 요약

- 사용자 후속 지시를 Issue #20 댓글에 기록하고 같은 작업 브랜치에서 적용했다. 고급 기본값은 AutoCAD 표준 (Standard), 테두리와 문자 색상은 기본(검정), DXF 색상7이다. 기존 사용자 설정과 프리셋을 보존한다.
- 기본 규격을 먼저 배치하고 고급 설정을 접었다. 파일 표시는 이름만 보여주고 입력 범위는 Excel이 있을 때 표시한다. 표의 페이지 버튼 행 오른쪽에 편집과 행 추가를 두고 기존 전체 문자 버튼을 공통 편집창으로 대체했다.
- 표 더블클릭과 편집 및 행 추가는 같은 모달을 사용한다. 한 줄은 한 칸이며 Excel 없이도 빈 표에서 직접 입력하고 DXF를 저장한다. 작업 데이터만 수정하고 원본 Excel에 쓰지 않는다.
- 하단 버전과 크레딧을 제거했다. 상단 오른쪽 업데이트 확인은 새 버전일 때 색상과 문구로 알리며 자동 팝업은 없다. 도움말에서 앱 소개, 버전, 원개발자 직장인과 Fork/후속 개발 plcmanjp를 표시한다.

## 결정/판단 근거

- 원본 분석과 편집/추가를 분리했다. 해석/범위 변경과 재불러오기는 데이터 소실을 확인하며 실패/취소는 작업 데이터를 유지한다. DXF를 저장한 뒤에도 재불러오기는 원본 값을 복원하므로 확인한다.
- 새 편집 revision과 렌더링 revision을 대조해 갱신 취소 뒤의 오래된 배치를 저장하지 않는다. 수정한 라벨의 대체된 형식 경고만 제거하고 해결되지 않은 원본 오류와 시트 진단은 유지한다.
- 전체 문자를 스크롤 가능한 Text에 표시한다. 빈 줄과 탭/제어 문자를 거부하고 입력 문자, 공백과 선행0을 보존한다. 한 라벨2,000,000자 및 전체250,000칸 한계를 적용한다. 작업 데이터는 닫을 때 보관하지 않으며 필요한 결과는 DXF로 저장한다.
- Tk Treeview의 초기 키보드 선택 부재를 실제로 관측해 현재 페이지 Home/End 선택을 추가했다. Return 편집과 Ctrl+Enter 적용 및 Esc 취소를 검증했다.

## 검증

합성 Excel과 격리 설정 및 Git 제외 .local/issue20의 출력만 사용했다. 원본, 법적 고지, 기존 공개0.2.2 자산과 과거 QC 및 journal은 보존했다.

| 변경 유형 | 명령 또는 경로 | 실제 결과 |
|---|---|---|
| 제품/편집/보호 | .venv/Scripts/python.exe -B -m unittest discover -s project/tests -v, build-dev.ps1 | 최종99개 PASS. 전체 stdout/stderr에 ignored Tk 예외와 traceback 없음. |
| 배포/하네스 | py -3.14 -B -m unittest discover -s release/tests -v, test_session_start.py | 배포15개 PASS와 symlink 권한1개 SKIP, 하네스22개 PASS. |
| 저장소/공개 경계 | py -3.14 -B .agents/scripts/check_repository.py | provenance, 링크, 사용자 문서와 UTF-8 및 규칙 검사 PASS. |
| 개발 빌드 | powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/build-dev.ps1 | returncode0. 소스14개와 패키지1125개 hash 일치, commit된 소스 blob도 동일. |
| 실제 frozen 편집 | 부모 selector-only UIA 러너 editor-frozen-excel | 23단계13.503초 PASS. 불러온20개/60칸에서 첫 라벨을2칸으로 수정하고2칸 새 라벨을 추가해21개/61칸 저장. |
| 작은 창 전체 흐름 | editor-frozen-final, 외곽960x540/DPI96 | 24단계12.758초 PASS. Excel 없는 추가, Home/Return 편집, 저장, 도움말과 종료. 화면 육안 검토에서 입력/적용/취소와 주요 버튼 접근 가능. |
| 원본/결과 | 원본 SHA와 byte/mtime 및 GUI DXF4개 재읽기 | Excel bytes/mtime 동일. 모든 문자와 좌표 및 글자 속성, Standard/txt.shx, 레이어 색상7/7, AC1024/mm와 audit 오류0. |
| 업데이트/도움말 | source 합성 available0.2.3 응답과 수동 버튼 | 자동 파란 버튼만 표시, 클릭 시 중앙 안내. 도움말 개발자2명과 버전 확인. 합성0.2.3을 공개 릴리스로 취급하지 않는다. |
| 독립 검수 | code-reviewer의 누적 및 변경 hunk 검수 | 취소/재불러오기/프리셋/모달 경계 보정 뒤 finding0개. 실행 결과는 Director 별도 확인. |
| 원격 CI | [38599865631](https://github.com/plcmanjp/excel-cad-label-maker/actions/runs/38599865631) | e2c6097의 verify/product SUCCESS. 제품99개와 원격 배포16개 및22개 하네스 통과. 로그에 ignored Tk 오류 없음. |

- 첫99개 테스트 빌드에는 닫힌 편집창의 StringVar finalizer가 worker에서 실행되어 timeout1건과 ignored 예외가 있었다. 안내와 오류를 Label text/configure로 변경하고 이전 테스트의 Tk 객체를 owner thread에서 수집하도록 보정했다. 대기 시간을 늘리거나 예외를 숨기지 않았다.
- 초기 UIA 프로필에는 한국어 stdin 인코딩, 접근성 이름과 native save 경로 문제가 있었다. UTF-8 전송과 정확한 selector를 적용했으며 Windows 절대 경로와 실제 키보드 수정 통지 뒤 Enter로 저장한다. 실패한 원시 기록도 보존하고 최종 전체 흐름 PASS와 구분한다.
- 개발 EXE SHA-256은 4bcd4075f536403bd7a7c05f8974915359162ea2c06b5d9be99f6dd8157ab5e2다. 빌드 기준16a60b9의 dirty snapshot과 실제 소스 hash를 기록했고 이후 e2c6097 blob과 대조했다. 신규 버전, main 병합, tag와 공개 릴리스는 수행하지 않았다.
- [결과 기록](../../../project/qc/issue20-editor-results.json)에 근거와 hash를 남겼다. 원시 화면과 프로필은 개인 경로가 있어 Git 제외 위치에 보존한다. 선행 성능 값을 변경된 기본 글꼴과 편집 추가의 새 측정으로 확대하지 않는다.

## 미해결 이슈

- 공통 selector-only 러너에는 OS 더블클릭 action이 없다. 매핑된 실제 Tk 행 좌표의 처리기 회귀와 frozen의 물리 키보드 Enter 편집을 구분하며 OS 마우스 더블클릭은 미실행이다.
- 실제 초보 사용자와 Windows150%/200% 검증은 남아 Issue #20을 OPEN으로 유지한다. 실제 CAD, 별도 PC, 원본 대응과 이용 조건은 Issue #14의 경계다.

## 커밋 (이번 세션)

- [e2c6097](https://github.com/plcmanjp/excel-cad-label-maker/commit/e2c6097e0b2c176bd3f112f60a1b02c4f5ac57c7): 출력 라벨 편집, 직접 입력, 간단한 UI, 회귀와 GUI 및 빌드 근거.
- 이 스냅샷과 CURRENT 및 CI readback은 후속 기록 commit으로 같은 작업 브랜치에 반영한다. 일반 push만 수행한다.

## 작업번호

- [Issue #20](https://github.com/plcmanjp/excel-cad-label-maker/issues/20): 사용자 추가 범위의 구현과 로컬 검증, 브랜치 push 및 CI 완료. 환경과 사용자 수용은 부분 완료다.

## 다음 우선순위

1. 실제 마우스 더블클릭과 초보 사용자 및 Windows150%/200% 배율을 검증한다.
2. 실제 CAD와 별도 PC 및 Standard 한글 표시를 Issue #14의 조건에 따라 검증한다.
3. 브랜치 검토 뒤 main 병합과 신규 버전 및 공개 릴리스 범위를 결정한다.

## 자가점검 회고

- 구현과 검사, 실제 GUI 입력, DXF 의미와 CAD 렌더링을 별도로 판정했다. source의 합성 업데이트 응답을 원격 공개 상태로 보고하지 않았다.
- PASS 개수만 보고 Tk finalizer 예외를 놓치지 않도록 전체 stdout/stderr도 확인했다. 실제 GUI가 드러낸 키보드 선택 문제를 결정적인 바인딩과 회귀로 보완했다.
- 요구 범위의 변경과 실패 보정만 수행했고 고객 파일, 개인 설정과 고지 원문 및 기존 배포 자산은 보존했다. 남은 물리/배율 검증을 자동 검사 PASS로 대체하지 않았다.
