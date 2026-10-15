# 작업 저널 (CURRENT)

## 목표

- [Issue #24](https://github.com/plcmanjp/excel-cad-label-maker/issues/24): 새 기본 글꼴을 Arial로 바꾸고 기존 설정/프리셋의 글꼴을 보존한다.

## 현재 상태

- 사용자가 AutoCAD에서 표준 글꼴의 한글은 물음표, 굴림과 Arial의 한글은 정상임을 확인하고 Arial 기본값을 선택했다. fix/issue-24-default-arial에서 제품 기본값과 DXF 문자열 API의 출처를 통일하고 관련 검사 및 사용자 안내를 수정했다. 제품 128개와 저장소/공개 문서 및 diff 검사가 통과했고 개발 빌드 검증이 남았다.
- 공개 latest는 v0.4.0이고 제품 commit은 156b4b9다. 이번 작업은 새 정식 버전의 공개 승인을 포함하지 않으며 기존 tag와 자산을 유지한다.
- 원래 OneDrive checkout은 예상 밖 staged/unstaged/untracked 변경과 중복 worktree로 보존한다. clean main adc5e9d에서 분기한 OneDrive 밖 독립 checkout에서 수행한다.

## 주요 결정

- 새 설정만 Arial을 기본으로 사용한다. 기존 마지막 설정과 프리셋의 명시적 Standard/굴림 선택은 유지하며 자동으로 덮어쓰지 않는다.
- DXF는 AC1024/UTF-8로 한글 문자열을 보존한다. 현재 사용자의 CAD에서 Arial 한글 표시 확인과 모든 CAD/PC에서의 글꼴 호환성은 구분한다.

## 검증 결과

- 변경 전 메모리상 DXF 직렬화/재읽기에서 Standard/굴림/맑은 고딕의 합성 한글이 모두 보존됐다. Standard는 txt.shx만 지정하고 bigfont는 비어 있었다. 원본 문자 손상으로 단정하지 않는다.
- 제품 128개 PASS: 기본 UI/DXF의 Arial, 한글/영문 문자열 보존, 명시적 Standard 출력, 기존 버전의 굴림과 현재 Standard 프리셋/마지막 설정 보존을 확인했다. 저장소/공개 문서와 diff 검사도 PASS다. 개발 빌드 검증이 남았다.
- 이전 배포의 근거는 project/qc/release040-results.json에 보존했다.

## 미해결 사항

- Arial 기본 DXF 스타일과 UI, 기존 설정/프리셋 보존 및 개발 빌드를 확인하고 PR에 연결한다.
- Issue #20의 사용자/실제 OS 배율, #14의 실제 CAD/별도 PC/권리 조건과 원래 checkout 보존 상태는 유지한다.

## 다음 작업

1. 관련 회귀와 저장소/공개 문서 검사를 실행한다.
2. 이전 빌드를 덮어쓰지 않는 개발 산출물을 생성하고 receipt 및 DXF 스타일을 확인한다.
3. 검증 결과를 기록하고 commit/push와 PR을 준비한다.
