# r010 최신 경량화 빌드 0.2.1 공개

| 항목 | 값 |
|---|---|
| 문서리비전 | r010-v021-public-release |
| 작성일시 | 2026-10-14 16:32 (KST) |
| 작성모델 | GPT-6 Codex |
| 담당에이전트 | Director 및 읽기 전용 제품 Reviewer |

## 요약

사용자 최신 지시에 따라 [v0.2.1](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.2.1)을 latest 정식 버전으로 공개했다. 앱과 구성 및 사용자 안내 버전을 맞추고 [PR #16](https://github.com/plcmanjp/excel-cad-label-maker/pull/16)을 main에 병합했다. 기존 경량화 구현은 변경하지 않았다.

Issue #2를 복구 소스와 재현 가능한 빌드 완료로 닫고 공개 작업 Issue #15도 완료했다. 실제 CAD, 별도 PC 및 원본 대응과 이용 조건은 [Issue #14](https://github.com/plcmanjp/excel-cad-label-maker/issues/14)에 OPEN 및 미검증으로 이관했다. 기존 v0.1.0과 v0.2.0 및 원본과 크레딧과 NOTICE 범위는 보존했다.

## 검증

branch, PR과 clean main Windows CI77개 및 독립 소스와 artifact 검수가 PASS다. 공개 ZIP은 29,501,691 bytes이며 Markdown이 없고 외부 및 런타임 고지63개 byte와 provenance 및 manifest1128개와 receipt1127개 hash가 일치한다.

최종 ZIP을 별도 폴더에 압축 해제해 실제 EXE의 0.2.1과 ABC 아이콘, Explorer Excel 드롭과 DXF 저장을 확인했다. 라벨4개, TEXT와 LWPOLYLINE 각7개의 글자, 위치와 스타일이 이전 검증 결과와 같다. AC1024 및 mm와 UTF-8 및 audit 오류0건이다.

원격 tag와 latest, 본문 및 자산 업로드 상태를 확인하고 ZIP 및 체크섬을 재다운로드해 로컬과 byte 및 hash를 대조했다. 실제 공개0.2.0 EXE를 새 검수 폴더에서 실행해 시작 시 0.2.1 자동 알림과 나중에 동작을 확인했다. 별도 QC 버전 override는 사용하지 않았다. 최신0.2.1 앱의 수동 확인은 새 버전이 없다는 피드백과 공개0.2.1 상태를 표시했다.

상세 자산 ID와 source/tag commit 및 EXE/ZIP hash와 검증 범위는 [릴리스 QC](../../../release/qc/release-v0.2.1.json)에 있다. 원시 경로와 화면 증거는 .local/release-v021에만 보관한다. 공개0.1.0과0.2.0의 release/asset ID와 digest 및 보호68개 hash가 유지됐다.

## 커밋 (이번 세션)

- 공개 버전 준비 e50676d5aff9b74c5cba138b60fbb7b5287c25fc
- PR #16 병합 및 최종 빌드와 tag db1623962bee574d635ad6fccd93c0239c6b06fe
- 공개 후 README와 결과 및 journal 기록 커밋은 Git 이력을 따른다. tag는 실제 빌드 commit을 계속 가리킨다.

## 다음 우선순위

- Issue #14에서 실제 CAD와 Python 없는 별도 사용자 PC를 확인한다.
- 원본 빌드 대응 및 세부 이용 조건을 원권리자의 근거로 확인한다.

## 자가점검 회고

빌드 완료와 현장 및 권리 검증을 구분해 후속 이슈를 유지했다. 드롭 도구가 중복 Explorer를 감지한 관찰에서는 실제 입력을 하지 않았으며 독립된 검수 폴더의 유일 창을 다시 확인한 뒤 실제 드롭을 완료했다. 공개 전에 두 자산의 digest를 대조하고 공개 뒤 재다운로드 및 실제 구버전 시작 알림으로 결과를 확인했다.
