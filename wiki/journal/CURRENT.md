# 작업 저널 (CURRENT)

## 목표

- [Issue #24](https://github.com/plcmanjp/excel-cad-label-maker/issues/24): 새 기본 글꼴을 Arial로 바꾸고 기존 설정/프리셋의 글꼴을 보존한다.

## 현재 상태

- 사용자가 AutoCAD에서 표준 글꼴의 한글은 물음표, 굴림과 Arial의 한글은 정상임을 확인하고 Arial 기본값을 선택했다. fix/issue-24-default-arial의 제품 commit 5d3b144에서 기본값을 통일하고 검사/안내를 수정했다. [PR #25](https://github.com/plcmanjp/excel-cad-label-maker/pull/25)는 OPEN이며 최종 head의 원격 결과는 PR checks가 기준이다.
- 제품 128개와 저장소/공개 문서 및 diff 검사 PASS. 별도 개발 EXE의 1,125파일 receipt 검증과 실제 실행에서 새 기본 글꼴 Arial을 확인했다. 산출물은 독립 checkout의 project/dist/Excel_CAD_Label_Arial_Dev에 있다.
- 공개 latest는 v0.4.0이고 제품 commit은 156b4b9다. 이번 작업은 새 정식 버전의 공개 승인을 포함하지 않으며 기존 tag와 자산을 유지한다.
- 원래 OneDrive checkout은 예상 밖 staged/unstaged/untracked 변경과 중복 worktree로 보존한다. clean main adc5e9d에서 분기한 OneDrive 밖 독립 checkout에서 수행한다.

## 주요 결정

- 새 설정만 Arial을 기본으로 사용한다. 기존 마지막 설정과 프리셋의 명시적 Standard/굴림 선택은 유지하며 자동으로 덮어쓰지 않는다.
- DXF는 AC1024/UTF-8로 한글 문자열을 보존한다. 현재 사용자의 CAD에서 Arial 한글 표시 확인과 모든 CAD/PC에서의 글꼴 호환성은 구분한다.

## 검증 결과

- 변경 전 메모리상 DXF 직렬화/재읽기에서 Standard/굴림/맑은 고딕의 합성 한글이 모두 보존됐다. Standard는 txt.shx만 지정하고 bigfont는 비어 있었다. 원본 문자 손상으로 단정하지 않는다.
- 제품 128개 PASS: 기본 UI/DXF의 Arial, 한글/영문 문자열 보존, 명시적 Standard 출력, 기존 버전의 굴림과 현재 Standard 프리셋/마지막 설정 보존을 확인했다. 개발 빌드와 아이콘/법적 고지/전체 receipt 해시 및 격리 설정에서의 실제 Arial 표시도 PASS다.
- 이전 배포의 근거는 project/qc/release040-results.json에 보존했다.

## 미해결 사항

- PR #25의 최종 head 원격 검사를 확인하고 검토 후 병합/차기 정식 배포를 별도로 판단한다. 기존 공개 자산은 변경하지 않는다.
- Issue #20의 사용자/실제 OS 배율, #14의 실제 CAD/별도 PC/권리 조건과 원래 checkout 보존 상태는 유지한다.

## 다음 작업

1. PR #25의 최종 head CI를 확인하고 병합과 차기 정식 버전의 공개 범위를 결정한다.
2. 기존 설정이 Standard라면 고급 설정에서 Arial을 명시적으로 선택한다.
3. #20/#14의 남은 환경 검증과 원래 OneDrive checkout 보존 범위를 유지한다.
