# 작업 저널 (CURRENT)

## 목표

- [Issue #19](https://github.com/plcmanjp/excel-cad-label-maker/issues/19): 완료한 배포 세션의 워크스페이스 청소와 세션 마무리.

## 현재 상태

- [PR #18](https://github.com/plcmanjp/excel-cad-label-maker/pull/18)은 main에 병합됐고 v0.2.2는 최신 정식 공개 버전이다. Issue #17과 #2는 CLOSED다.
- 일회성 QC와 중복 빌드 및 Python bytecode 캐시를 휴지통으로 옮겼다. 병합 브랜치를 정리해 로컬과 원격에 main만 남고 등록 워크트리는 하나다.
- 앱과 원본, 정식 릴리스 및 저장된 검증 기록과 개발환경은 보존한다. .local에는 원본 실행 파일인 baseline과 재사용 가능한 uia-qc-env만 남긴다.

## 주요 결정

- README와 사용자 안내 및 릴리스 노트에는 제품 사용에 필요한 정보를 제공한다. 개발 안내는 기여자의 재현 가능한 절차로 작성한다. 사용자 문서 검사를 통해 내부 운영 문구와 기록 링크의 재유입을 차단한다.
- 원본과 외부 법적 고지 및 기존 공개 자산과 과거 journal 및 QC 기록은 보존한다. 기존 세 릴리스의 본문만 사용자 노트에 맞춰 정리했다.
- 업데이트 알림의 중앙 배치는 0.2.2에서 적용된다. 기존 실행 파일을 변경하거나 업데이트를 자동 설치하지 않는다.

## 검증 결과

- main CI 78개와 독립 검수 및 최종 ZIP의 실제 Excel 드롭과 DXF 저장 및 재읽기가 PASS다. frozen 알림의 두 앱 위치와 크기에서 중앙 배치와 나중에 동작을 확인했다.
- 공개 tag와 latest 및 본문과 자산, ZIP과 체크섬 재다운로드를 검증했다. 상세 결과와 hash는 [0.2.2 릴리스 QC](../../release/qc/release-v0.2.2.json)에 있다.
- 청소 대상의 휴지통 항목과 보존 hash를 대조했고 저장소 검사와 개발환경 및 의존성 import가 PASS다. 현재 임시 빌드와 bytecode 캐시는 없고 워크트리 메타데이터 잔여도 없다.

## 미해결 사항

- [Issue #14](https://github.com/plcmanjp/excel-cad-label-maker/issues/14)의 실제 CAD와 별도 PC 및 원본 대응과 이용 조건은 OPEN 및 미검증이다. DWG 직접 출력은 미지원이다.

## 다음 작업

1. Issue #14 작업 시 실제 CAD 환경과 별도 PC의 검증 조건을 확인한다.
2. 새 기능 변경은 해당 Issue와 현재 main을 기준으로 진행한다.
3. 새 사용자 문서를 추가하면 공개 문서 검사 목록에 포함한다.
