# r021: 새 기본 글꼴을 Arial로 변경

| 항목 | 값 |
|---|---|
| 문서리비전 | r021-default-arial-font |
| 작성일시 | 2026-10-15 17:33 (KST) |
| 작성모델 | GPT-6 Codex |
| 담당에이전트 | Director |

## 요약

- 사용자는 AutoCAD 표준 글꼴에서 한글이 물음표로 표시되고 굴림/Arial에서는 정상임을 확인했다. 요청한 Arial을 새 기본값으로 적용했다.
- converter.py의 DEFAULT_FONT를 LabelSettings와 generate_dxf_string이 공유하도록 변경했다. 설정 저장소와 UI는 기존 LabelSettings 경로로 새 기본값을 사용한다.
- 기존 Standard/굴림 등의 명시적인 마지막 설정과 프리셋은 보존한다. 사용 안내와 패키지 README도 새 기본값과 기존 설정 변경 방법을 설명한다.
- 별도 개발 EXE를 생성하고 실제 실행에서 고급 설정의 Arial 기본 선택을 확인했다. 기존 공개 tag/자산과 OneDrive checkout은 변경하지 않았다.

## 커밋 (이번 세션)

- 5d3b144ff535d05d4e2a75ee0162dd43a8d21e3b: Arial 기본값, 기존 선택 보존 검사 및 사용자 안내.
- 이 journal과 최종 CURRENT는 기록 전용 후속 commit에 포함한다.

## 작업번호

- [Issue #24](https://github.com/plcmanjp/excel-cad-label-maker/issues/24): 기본 글꼴 변경의 작업지시.
- [PR #25](https://github.com/plcmanjp/excel-cad-label-maker/pull/25): OPEN. 최종 head의 원격 검사 결과는 PR checks로 확인한다.

## 검증

- 환경: OneDrive 밖 독립 checkout, Windows x64, Python 3.13.15/Tk 8.6, 잠금 의존성. 합성 입력과 임시 설정만 사용했다.
- 변경 유형: 기본 설정과 DXF 스타일 선택 및 사용자 안내. 설정 스키마/기존 파일은 변경하지 않았다.
- `python -B -m unittest discover -s project/tests -v`: 128개 PASS. 기본 UI와 문자열 API의 Arial, DXF TEXT의 ARIAL 참조와 arial.ttf, Unicode 재읽기, 명시적 Standard 출력과 이전 굴림/현재 Standard 설정 보존을 검증했다.
- `python -B .agents/scripts/check_repository.py`와 `git diff --check`: PASS. 원본 syntax 손상은 기존 비빌드 대상 제한이다.
- 로컬 개발 빌드는 기존 산출물을 보존하기 위해 PyInstaller의 새 이름 Excel_CAD_Label_Arial_Dev, 새 spec/work 경로를 사용했다. 공식 빌드와 같은 entrypoint/icon/data/hook/제외/hidden-import 옵션을 사용하고 package-materials, check-app-icon, build-receipt를 순서대로 실행했다. 빌드의 제품 source commit은 clean 5d3b144다.
- 첫 로컬 helper는 상대 icon 경로가 spec 폴더 기준으로 해석돼 실패했다. 공식 빌드와 같은 절대 icon 경로로 수정한 새 spec/work 경로의 빌드가 통과했다. 별도 README 자료 staging은 실행 파일 없는 폴더라 보호 검사에 거부됐으며 실제 개발 빌드 성공과 구분했다. README의 실제 plain_text 변환은 메모리에서 별도로 확인했다. 실패 산출물과 로그는 Git 제외 경로에 보존했다.
- 개발 EXE의 아이콘/법적 고지 및 receipt 전체 1,125파일 해시 PASS. EXE SHA-256 `3905352883f155939bdeeb4689eba79954a874d3a84a4abbd39cc8fa95faf63b`.
- Computer Use로 격리된 새 설정의 개발 EXE를 실행하고 고급 설정에서 Arial을 확인한 뒤 종료했다. 사용자 PC의 실제 Arial 한글 표시 확인은 사용자 보고이며 모든 CAD/PC의 결과로 일반화하지 않았다.
- 새 정식 버전과 tag/자산을 공개하지 않았다. 공개 latest는 0.4.0이다. 버전은 기본값 보정만으로 변경하지 않았다.

## 다음 우선순위

1. PR #25 최종 head의 원격 검사와 검토 후 병합/차기 공개 범위를 판단한다.
2. 기존 Standard 설정 사용자는 고급 설정에서 Arial을 선택한다. 명시적 기존 글꼴을 자동 덮어쓰지 않는다.
3. #20/#14의 사용자/OS/CAD/별도 PC/권리 검증과 원래 checkout의 예상 밖 변경 보존 상태를 유지한다.

## 자가점검 회고

- 문자열 보존과 CAD 표시를 구분하고 사용자가 확인한 Arial을 적용했다. 실제 TEXT의 스타일 참조를 검사해 스타일 테이블만 확인하는 검증 공백을 줄였다.
- 새 기본값과 기존 저장 설정을 구분했다. 과거 공개 자산과 로컬 변경을 덮어쓰지 않았다.
