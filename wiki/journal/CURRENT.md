# 작업 저널 (CURRENT)

## 목표

- [Issue #20](https://github.com/plcmanjp/excel-cad-label-maker/issues/20): 빠른 시작, 미리보기, 프리셋과 안전한 저장 및 사용자 후속 지시의 간단한 UI와 작업 데이터 편집 구현.

## 현재 상태

- 후속 지시의 기본 Standard 글꼴과 기본(검정) 색상, 기본 규격 중심 UI, 공통 편집/추가 모달과 Excel 없는 직접 입력, 상단 업데이트 버튼 색상 안내 및 도움말 크레딧을 구현했다. 로컬 검증과 독립 검수 및 e2c6097 작업 브랜치 commit/push를 완료했다. [원격 CI](https://github.com/plcmanjp/excel-cad-label-maker/actions/runs/38599865631)의 verify/product도 PASS다. 최종 기록은 같은 브랜치에 반영한다. 상세 범위는 [Issue 댓글](https://github.com/plcmanjp/excel-cad-label-maker/issues/20#issuecomment-6172241897)에 있다.
- 작업 브랜치는 feat/issue-20-preview-presets이며 main 기준은 d8fa53c다. 선행 P1/P2와 GUI 보정은 7808086, 8e004a6, 16a60b9에 반영됐다. [기존 CI](https://github.com/plcmanjp/excel-cad-label-maker/actions/runs/38590746220)는 PASS다.
- [PR #18](https://github.com/plcmanjp/excel-cad-label-maker/pull/18)은 main에 병합됐고 v0.2.2는 최신 정식 공개 버전이다. Issue #17과 #2는 CLOSED다. 이번 개발 빌드는 동일한 공개 버전 기준의 후보이며 새 공개 릴리스는 생성하지 않았다.

## 주요 결정

- 출력 테이블의 한 행은 라벨 하나다. 더블클릭, 편집 버튼과 행 추가는 같은 모달을 사용하며 한 줄은 도면의 한 칸이다. 기존 전체 문자 버튼은 편집 모달로 대체했다. 원본 분석과 편집/추가를 분리하고 원본 Excel에 쓰지 않는다.
- 편집 결과는 메모리에 보관한다. 저장하지 않은 편집의 종료와 재불러오기, 새 작업, 파일/해석/범위 변경에는 데이터 소실을 확인한다. 실패와 취소는 작업 데이터를 유지하며 오래된 배치의 저장을 차단한다. 기존 사용자 설정과 프리셋은 재사용한다.
- 새 버전은 상단 오른쪽 버튼의 색상과 문구로 알리며 자동 팝업은 표시하지 않는다. 앱 소개, 버전과 원개발자 직장인 및 Fork/후속 개발 plcmanjp는 도움말에 표시한다.
- 원본과 외부 법적 고지, 기존 공개 자산과 과거 journal/QC 기록은 보존한다. 사용자 문서는 제품 사용에 필요한 정보만 제공한다. 신규 버전 부여, main 병합, tag 변경과 공개 릴리스는 현재 실행 범위에 포함되지 않는다.

## 검증 결과

- 제품99개 PASS, 배포16개 중15개 PASS 및1개 Windows 심볼릭 링크 권한 SKIP, 하네스22개 PASS다. 수정 빌드의 전체 로그에 ignored Tk 예외가 없다. 독립 누적 검수와 제한된 추가 검수의 남은 finding은 0개다.
- 새 개발 EXE 빌드와 소스14개 및 패키지1125개 hash 대조를 완료했다. 실제 frozen GUI에서 Excel 없는 추가/편집/저장과 Excel 입력20개 라벨의 수정/추가 및 저장을 확인했다. 원본 Excel bytes와 mtime은 동일하다. DXF4개의 문자, 배치와 Standard 및 색상7/7 재읽기가 일치한다. 근거는 [편집 결과](../../project/qc/issue20-editor-results.json)에 있다.
- DPI96에서 960x540 창의 실제 키보드 편집/저장/도움말을 확인했다. source의 합성 새 버전 응답은 색상 버튼으로만 안내하며 사용자가 클릭할 때 팝업을 표시했다. 합성 버전0.2.3을 공개 버전으로 취급하지 않는다.
- 선행 미리보기, 파일 드롭과 성능 근거는 [기존 결과](../../project/qc/issue20-results.json) 및 [기존 성능 비교](../../project/qc/issue20-performance.json)에 보존한다. 현재 기본 글꼴과 편집 추가 이후의 성능 측정으로 확대하지 않는다.

## 미해결 사항

- [Issue #20](https://github.com/plcmanjp/excel-cad-label-maker/issues/20)은 실제 초보 사용자 평가와 Windows150%/200% 배율 검증을 남겨 OPEN으로 유지한다. 실제 마우스 더블클릭은 공통 러너에 해당 action이 없어 미실행이며 매핑된 Tk 처리기와 실제 frozen Enter 편집은 별도 검증했다.
- [Issue #14](https://github.com/plcmanjp/excel-cad-label-maker/issues/14)의 실제 CAD와 별도 PC 및 원본 대응과 이용 조건은 OPEN 및 미검증이다. DWG 직접 출력은 미지원이다.
- 선행 자동화의 프리셋/색상/예제 대화상자 변경 관측은 최종 흐름에서 재현되지 않았다. 원인은 미확정이며 기존 QC 관측을 보존한다.

## 다음 작업

1. 실제 초보 사용자, 물리 마우스 더블클릭과 Windows150%/200% 배율 검증을 진행한다.
2. 실제 CAD/별도 PC와 글꼴 및 원본 대응은 Issue #14의 조건에 따라 검증한다.
3. 브랜치 검토 결과에 따라 main 병합과 신규 버전 및 공개 릴리스의 승인 범위를 결정한다.
