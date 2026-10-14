# 작업 저널 (CURRENT)

## 목표

- Excel CAD Label Maker의 공개0.3.0을 유지하고 [Issue #20](https://github.com/plcmanjp/excel-cad-label-maker/issues/20)과 [Issue #14](https://github.com/plcmanjp/excel-cad-label-maker/issues/14)의 실제 환경 검증을 진행한다.

## 현재 상태

- [v0.3.0](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.3.0)은 latest 정식 릴리스다. tag와 정식 빌드의 소스 commit은 c7499c309a24dd48d83400e17983c03af98442f2이며 PR #21은 MERGED다. 배포 기록 commit의 [CI](https://github.com/plcmanjp/excel-cad-label-maker/actions/runs/38644767001)는 PASS다.
- 입력/도면 미리보기, 시트/범위 진단, 프리셋, 비동기 취소와 안전한 저장, 공통 라벨 편집/추가 및 Excel 없는 직접 입력을 제공한다. 기본 규격은 Standard와 검정이며 기존 사용자 설정은 재사용한다.
- 설정 보기는 넓은 창의 왼쪽 설정과 좁은 창의 설정/결과 전환이다. 설정을 팝업으로 변경하지 않았다. 편집/추가와 도움말은 팝업이며 업데이트는 상단 색상 버튼으로 안내한다.
- 배포와 공개 업데이트 검증 근거는 [배포 QC](../../release/qc/release-v0.3.0.json)에 있다. 세션 검증 앱은 종료했고 로컬 원시 증거와 배포물을 보존한다.
- 사용자 요청에 따른 캐시 청소는 차단이다. tracked cleanup manifest가 없고 일반 휴지통 실행기는 이 OneDrive cloud 경로를 지원하지 않는다. project/build와 조사한 캐시를 이동하거나 삭제하지 않았다. main worktree 하나만 있으며 Git 등록과 브랜치를 보존했다.

## 주요 결정

- 작업 테이블 한 행은 라벨 하나이며 공통 편집창의 한 줄은 도면의 한 칸이다. 편집/추가는 작업 데이터에만 반영하고 원본 Excel에 쓰지 않는다. 작업 데이터는 닫을 때 보관하지 않으므로 필요한 결과를 DXF로 저장한다.
- 데이터가 바뀌는 재불러오기, 파일/해석/범위 변경과 새 작업은 소실을 확인한다. 실패와 취소는 편집을 유지하고 revision이 다른 오래된 배치의 저장을 차단한다.
- 공개 자산과 tag를 다른 빌드로 덮어쓰지 않는다. 원본과 고지,0.1.0 보관 버전과 과거 QC/journal은 보존한다. 원개발자 직장인 및 Fork/후속 개발 plcmanjp와 확인된 이용 조건을 유지한다.
- 사용자 문서와 릴리스 노트는 사용/다운로드와 실제 제한을 안내한다. 내부 운영과 검증 이력은 별도 QC 및 journal에 보존한다.

## 검증 결과

- 정식 빌드의 제품99개, 배포 보호16개와 하네스22개 및 저장소/공개 문서 검사 PASS다. ignored Tk 오류와 독립 검수의 남은 finding은0개다.
- 정식 ZIP의 구성/hash와 재다운로드 일치, 실제 드롭, 편집/추가 및 직접 입력/저장과 업데이트를 확인했다. DXF 재읽기와 원본 Excel 및 패키지 보존 검증은 배포 QC에 있다.
- 청소 조사 전후 HEAD/refs/index/status가 같고 기존 보호 파일95개 및0.3.0 ZIP hash가 일치한다. project/build는34개 파일60,732,416 bytes이며 조사한 Python 캐시와 .cache는 없다. 휴지통 이동0개, 삭제0개, 회수 용량0 bytes다. 상세 inventory는 Git 제외 .local/session-wrap-20261015에 보존한다.
- 선행 구현과 성능 비교는 [이전 결과](../../project/qc/issue20-results.json), [편집 결과](../../project/qc/issue20-editor-results.json)와 [이전 성능](../../project/qc/issue20-performance.json)에 보존한다. 과거 측정을0.3.0 전체 환경의 새 성능 측정으로 확대하지 않는다.

## 미해결 사항

- 캐시 청소에는 이 저장소의 manifest와 지원되는 OneDrive 부분 정리/복구 경로가 필요하다. 현재 공용 도구의 경계를 완화하거나 전체 저장소 퇴역 모드로 우회하지 않는다.
- Issue #20은 실제 초보 사용자와 Windows150%/200%, 물리 마우스 더블클릭 검증을 남겨 OPEN이다. DPI96의 창 크기 및 실제 키 입력과 매핑된 Tk 처리기를 다른 증거로 구분한다.
- Computer Use 런타임은 kernel assets 경로 오류(OS error3)로 초기화되지 않았다. 공용 UIA의 제품 동작 검증을 Computer Use나 초보자 시각 수용으로 확대하지 않는다.
- Issue #14의 실제 CAD, 별도 PC, 원본 대응과 이용 조건은 OPEN 및 미검증이다. Standard의 한글 표시와 최종 도면 치수는 실제 CAD에서 확인한다. DWG 직접 출력은 미지원이다.
- 선행 자동화의 프리셋/색상/예제 대화상자 변경은 최종 흐름에서 재현되지 않았고 원인은 미확정이다. 기존 관측을 보존한다.

## 다음 작업

1. 실제 초보 사용자와 물리 더블클릭 및 Windows150%/200% 배율 검증을 진행한다.
2. Issue #14의 실제 CAD와 별도 PC 및 원본 대응과 이용 조건을 확인한다.
3. 캐시 청소를 재개할 때 별도 하네스 작업 범위에서 manifest와 OneDrive 부분 정리/복구 지원을 먼저 확인한다. 새 제품 요구사항은 GitHub Issue와 현재 사용자 승인 범위에 따라 처리한다.
