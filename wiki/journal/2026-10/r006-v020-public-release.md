# r006: main 병합과 복구 앱 v0.2.0 공개

| 항목 | 값 |
|---|---|
| 문서리비전 | r006-v020-public-release |
| 작성일시 | 2026-10-14 13:57 (KST) |
| 작성모델 | GPT-6 기반 Codex 메인 + code-reviewer |
| 담당에이전트 | Director |

## 요약

사용자의 현재 승인과 [Issue #6](https://github.com/plcmanjp/excel-cad-label-maker/issues/6)에 따라 PR #4 및 #7을 main에 병합하고 별도 복구 앱 [v0.2.0](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.2.0)을 최신 정식 GitHub Release로 공개했다. 기존 v0.1.0과 원본 VERSION, manifest, Python 및 EXE를 보존했다.

정식 버전과 제목 및 안내를 일치시키고 release-build receipt와 깨끗한 main 및 소스, 자산과 패키지 hash를 확인하는 ZIP 패키징을 추가했다. 원본 baseline 패키징은 변경하지 않았다. 태그와 빌드 commit은 `df1581f28088c1f5f4f6b9e0a3248572beb4fca5`이며 공개 Release ID는 412348290이다.

## 검증

- main의 [Windows CI](https://github.com/plcmanjp/excel-cad-label-maker/actions/runs/38512367722)에서 제품 33개, 빌드 및 패키징 8개, 하네스 22개 및 기준선 6개, 총 69개가 통과했다. 로컬 native symlink는 생성 권한 부족으로 SKIP였고 CI에서는 실제 링크를 생성해 거부 검사가 통과했다.
- 독립 공개 검수의 체크섬 leaf 보호를 보정하고 delta PASS를 받았다. 최종 artifact 독립 대조도 finding 없이 통과했다.
- 깨끗한 main에서 정식 Windows 앱을 빌드했다. receipt 1,903개, ZIP 및 압축 해제본 manifest 1,904개 파일 hash, ZIP 1,905개 고유 항목과 실제 PE 아이콘 10개를 대조했다.
- 최종 ZIP의 EXE를 실행했다. 공용 file-drop 엔진으로 실제 Explorer 파일 전달을 마친 뒤 Computer Use에서 파일 선택과 생성 버튼 활성화를 관찰했다. 입력용 파일 찾기는 사용하지 않았고 원본 및 보호 출력은 변경되지 않았다. 드래그 전송과 제품 수용 근거를 구분했다.
- 실제 정식 EXE로 DXF를 저장했다. 4개 라벨과 TEXT 및 LWPOLYLINE 각각 7개, mm 및 AC1024, 원본 합성 Excel의 한글과 영문 및 숫자 읽기 일치, audit 오류 0개를 확인했다.
- ZIP SHA-256은 `ae7a8515bf1418503fca8c59ce109c45952e83f59ef84e7764cafc37f5475b6a`, EXE는 `7b619636417f02f69e58bfe27d5dfbdcd51030022de726556950e0998b1f31fa`다. ZIP 크기는 39,860,962바이트다.
- 게시 전에 업로드된 두 자산의 상태, 크기와 GitHub digest 및 tag의 정확한 commit을 확인했다. 공개 뒤 ZIP과 checksum을 다시 내려받아 hash와 1,905개 항목을 대조했다. 릴리스 노트 원문 readback, latest API 0.2.0 및 기존 v0.1.0 자산 불변을 확인했다.
- 이전 개발 EXE 0.2.0.dev1을 실제 재실행하자 새 정식 0.2.0 팝업이 자동 표시됐다. 수동 조회에서도 표시됐다. 버전 입력 override나 테스트용 원격 릴리스를 사용하지 않았다.
- 상세 공개 요약은 `qc/release-v0.2.0.json`이고 raw 경로와 UI 증거는 `.local/`에만 보관한다.

## 커밋 (이번 세션)

- PR #4 main 병합: `e20e95257fe2ebf25496daf9d9efc4bf0b31c2bd`.
- 릴리스 준비: `9a87fa4c9094024949961cbb505d2d8ab4752d4b`.
- 링크 검사 순서 보정: `adb3232271df5dc5e8881a0fce45e9d6f9a55ced`.
- PR #7 main 병합 및 공개 tag: `df1581f28088c1f5f4f6b9e0a3248572beb4fca5`.
- 공개 결과 문서의 commit은 이 journal 경로의 git log로 확인한다. 문서 후속 commit은 공개 tag와 artifact를 교체하지 않는다.

## 미해결 이슈

Issue #2의 실제 CAD 글꼴과 도면 수용, 별도 Windows PC 실행 및 원본 빌드 대응과 세부 이용 조건은 미확인이다. 릴리스 노트와 NOTICE에 범위를 명시했다. DWG 직접 출력은 미지원이며 원본에 임의 오픈소스 라이선스를 부여하지 않았다.

## 다음 우선순위

1. 실제 사용하는 CAD에서 합성 DXF의 한글, 글꼴, 레이어 및 mm 규격을 확인한다.
2. Python 없는 별도 Windows PC에서 ZIP 압축 해제 후 변환을 확인한다.
3. 원본의 빌드 자료와 세부 이용 조건을 확보한다.

## 자가점검 회고

기능 및 아이콘 구현의 QC, 정식 main 빌드, 압축 해제 앱의 실제 입출력과 원격 게시 readback을 각각 기록했다. 로컬 도구 제한과 원격 native 검사 실행을 구분했고 보호 guard를 약화하지 않았다. 공개 전후 exact commit과 artifact hash를 고정하고 이전 릴리스를 보존했다.
