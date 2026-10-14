# r013 Excel 라벨 미리보기와 설정 재사용 구현

| 항목 | 값 |
|---|---|
| 문서리비전 | r013-preview-presets-implementation |
| 작성일시 | 2026-10-15 00:33 (KST) |
| 작성모델 | GPT-6 (Codex), GPT-6.1 (검수) |
| 담당에이전트 | Codex Director와 code-reviewer Specialist |

## 요약

- 사용자 q1 승인으로 Issue #20의 준비, P1, P2와 로컬 검증 및 작업 브랜치 일반 commit/push를 진행했다. 기준 main은 d8fa53c이고 브랜치는 feat/issue-20-preview-presets다.
- 파일 선택 후 입력 출처와 진단, 시트/범위 및 첫 행 제외, 데이터와 도면 미리보기, 최소 글자 높이 경고와 저장 차단 이유를 연결했다.
- 공통 배치 계산과 같은 스냅샷을 미리보기와 DXF 저장에 사용한다. 프리셋과 마지막 설정 복원, 작업 세대와 비동기 처리 및 원자적 저장의 취소 경계를 추가했다.
- 사용자 안내는 공개 0.2.2의 기존 화면과 현재 소스의 새 화면을 구분한다. 새 버전, main 병합과 공개 릴리스는 수행하지 않았다.

## 결정/판단 근거

- 기존 해석을 기본으로 보존한다. 표시 형식 반영은 명시적 선택이며 지원 형식만 적용하고 대체 문자를 경고한다. xls의 수식 출처와 캐시 누락 및 필터 탐지는 지원하지 않는다.
- 원본 변경을 SHA로 탐지하고 저장을 차단한다. 미리보기에서 확인한 결과를 다시 읽어 몰래 교체하지 않는다. 설정에는 Excel 내용과 경로 및 시트와 범위를 저장하지 않는다.
- 데이터 목록100개, 진단200개와 전체 문자100칸의 페이지, 보이는 미리보기 최대200개 라벨 및1200칸으로 화면 처리를 제한한다. 단일30000칸도 윤곽과 상세 페이지로 확인한다.
- Tk/ttk와 현재 고정 의존성을 유지한다. 문자 폭의 미리보기는 Windows GDI 비트맵으로 가로 배율을 반영하며 실제 CAD 렌더링의 완전 일치를 주장하지 않는다.
- 첫 독립 검수의8개 지적과 파생 좌표 overflow를 보정했다. 실제 GUI에서 발견한 숨김 탭의 최초 전체/선택 맞춤과 native 파일 대화상자의 단축키 재진입도 보정했다. 누적 검수 뒤 변경 hunk만 확인했으며 최종 남은 finding0개다.

## 검증

실행 위치는 저장소 루트다. Windows11, 제품 Python3.13.15/Tk8.6.15와 잠금 의존성, 하네스 Python3.14.3을 구분했다. 합성 Excel, 임시 출력과 격리 설정 경로만 사용했다. 원본과 기존 공개 ZIP 및 법적 고지는 보존했다.

| 변경 유형 | 명령과 통과 기준 | 실제 결과와 부작용 |
|---|---|---|
| 제품/동시성/설정 | .venv/Scripts/python.exe -B -m unittest discover -s project/tests -v | 81개 PASS. 임시 합성 입력과 출력 및 설정을 생성한다. |
| 배포 보호 | .venv/Scripts/python.exe -B -m unittest discover -s release/tests -v | 로컬15개 PASS, symlink 권한1개 SKIP. 원격 CI의16개는 통과했다. |
| 하네스/공개 경계 | py -3.14 -B .agents/scripts/test_session_start.py 및 check_repository.py | 22개 PASS, 링크와 원본 provenance 및 공개 문서와 인코딩 PASS. |
| 개발 빌드 | powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/build-dev.ps1 | 최종 returncode0. Git 제외 개발 산출물만 생성. 소스와 패키지1125개 hash, 아이콘과 고지 대조 PASS. |
| 실제 GUI | issue20-gui.py가 부모 공용 UIA 엔진을 호출 | 최종 source6.868초, frozen6.086초. 고급 설정 없이20개 라벨/60칸을 키보드로 저장. 초보 사용자 평가는 아니다. |
| 설정/모달 | 폭75 mm 저장 후 파일 교체, 재시작과 native 대화상자 중 Ctrl+O | 재시작 기본 흐름6.197초, 폭과 색상 복원 및 중첩 차단 PASS. 실제 No와 Cancel 뒤 보호 DXF hash 유지. UIA가 누락한 확인 창은 Win32 관측과 정확한 버튼 이름으로 처리. |
| 실제 드롭 | 부모 windows_file_drop_qc.py와 별도 제품 수용 확인 | source/frozen 모두 INPUT_COMPLETED 뒤 실제 시트와20개/60칸 확인. 입력과 보호 출력 hash 유지. 창 밖/가림과 숨김 Explorer 때문에 입력 전 중단한 기록은 PASS에 포함하지 않는다. |
| 결과 대조 | 실제 GUI의 DXF5개 재읽기와 공통 배치 비교 | 문자60개와 테두리60개, 좌표와 글자 속성 및 레이어 일치. AC1024/mm와 audit 오류0. |
| 응답/메모리 | issue20-performance.py의 교대 새 프로세스3회, UI 이벤트 루프와 취소 | 1000개/10000개와 단일30000칸 측정. 분석과 진단 비용 및 UI heartbeat와 viewport 작업 수를 기록했다. |
| 시작/크기 | 같은 호스트에서 frozen 교대5회, 전체 폴더 byte | 시작 중앙값 기존0.524초, 신규0.549초. 폴더65665215/65610404바이트. 공개 패키지와 개발 패키지의 README/VERSION/manifest 차이를 포함하므로 크기 최적화로 주장하지 않는다. |
| GDI 자원 | 문자 비트맵600회 반복 | GDI handle157에서157로 유지. 글꼴 파일이나 새 라이브러리를 추가하지 않는다. |
| 창 크기 | DPI96에서 외곽 창1366x768, 1280x720, 960x540 | 저장 버튼과 NaN 오류 및 수정 필드 접근, 좁은 창의 설정/결과 전환 확인. 실제 Windows150%/200% 검증은 아니다. |

- 10000개 라벨 전체 변환 중앙값은 기존2.938초, 신규3.523초다. peak working set은131686400에서162742272바이트로 늘었다. 값과 수식의 두 읽기 및 출처와 진단을 추가한 비용을 그대로 보고했다.
- 최초 원격 CI는 지연 주입 테스트가 Windows TEMP의 8.3 별칭과 정규화된 경로를 다르게 비교해 실패했다. 양쪽 resolve를 적용하고 로컬 UI25개 및 [원격 CI](https://github.com/plcmanjp/excel-cad-label-maker/actions/runs/38589845254)의 verify/product를 재확인했다. 제품 소스는 변경하지 않았다.
- 개발 EXE SHA-256은 1f1047c2a19d3f72c087399d1e5b71689b3093e03e86a07ba798571ede1eaf00이다. 빌드 시점 기준 commit과 dirty 상태는 receipt에 남기고 실제 소스 hash를 대조했다. 공개 정식 패키지로 취급하지 않는다.
- 수용 조건별 근거와 hash는 [결과 기록](../../../project/qc/issue20-results.json), 측정 원문 요약은 [성능 기록](../../../project/qc/issue20-performance.json)에 있다. 원시 화면과 절대 경로가 있는 기록은 Git 제외 .local/issue20에 보존한다.

## 미해결 이슈

- Issue #20은 실제 초보 사용자 평가와 Windows150%/200% 배율 환경 검증을 남겨 OPEN으로 유지한다. 실제 CAD와 별도 PC 및 원본 대응과 권리는 Issue #14의 미검증 경계를 유지한다.
- 초기 자동화에서 프리셋과 색상 및 고급 설정 변경과 예제 대화상자를 관측했다. 추적 source 및 최종 frozen 흐름에서는 재현되지 않았고 원인은 미확정이다. 별도로 측정해 수정한 native 대화상자 재진입과 같은 원인으로 단정하지 않는다.

## 커밋 (이번 세션)

- [7808086](https://github.com/plcmanjp/excel-cad-label-maker/commit/7808086d02b4535535e4b89ba41e9db4c6a2ecc9): 입력 진단과 도면 미리보기 및 프리셋과 비동기 저장 및 검증 근거.
- [8e004a6](https://github.com/plcmanjp/excel-cad-label-maker/commit/8e004a6aa9307a6ab42f5bd08920ab839123acdf): Windows 임시 경로 별칭을 정규화한 지연 주입 테스트.
- 이 스냅샷과 CURRENT 및 최종 CI와 패키지 비교 설명은 마무리 기록 commit으로 같은 작업 브랜치에 저장한다. 귀속 검증을 통과하고 force 없이 push한다.

## 작업번호

- [Issue #20](https://github.com/plcmanjp/excel-cad-label-maker/issues/20): 준비/P1/P2 구현과 로컬 검증, 브랜치 전달. 실제 환경과 사용자 검증은 부분 완료다.

## 다음 우선순위

1. 실제 초보 사용자와 Windows150%/200% 배율 환경에서 남은 수용 조건을 검증한다.
2. 초기 설정 변경 현상이 재현되면 보존한 원시 QC와 새 앱 이벤트 기록을 대조한다.
3. 작업 브랜치를 검토하고 main 병합 및 신규 버전과 공개 릴리스의 승인 범위를 결정한다.

## 자가점검 회고

- 구현, 자동 검사, 실제 입력 전달과 제품 수용, 도면 의미 및 실제 CAD 품질을 별도로 판정했다. 성능 악화와 배율 및 사용자 평가의 빈자리를 숨기지 않았다.
- 전체 리뷰를 반복하지 않고 신규 실패와 지적의 경계만 보정하고 확인했다. CI가 드러낸 테스트 경로 문제를 무조건 재실행으로 넘기지 않았다.
- 개인 설정과 고객 자료, 원본과 법적 원문 및 기존 공개 자산을 변경하지 않았다. 로컬 증거는 정리하지 않고 보존하며 사용자 승인 범위 안의 일반 commit/push까지만 수행했다.
