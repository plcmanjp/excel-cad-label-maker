# 작업 저널 (CURRENT)

## 목표

- 공개 v0.2.0의 검증 기록을 유지하고 [Issue #2](https://github.com/plcmanjp/excel-cad-label-maker/issues/2)의 실제 CAD, 별도 PC 및 원본 이용 조건을 확인한다.

## 현재 상태

- [v0.2.0](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.2.0)이 최신 정식 GitHub Release다. Excel 드래그 앤 드롭, UTF-8 DXF, GitHub 업데이트 알림과 ABC 흰 라벨 아이콘을 포함한다.
- PR #4와 #7을 main에 병합했다. 릴리스 소스 및 tag commit은 `df1581f28088c1f5f4f6b9e0a3248572beb4fca5`다. main에서 빌드한 ZIP과 checksum을 게시하고 원격 재다운로드 hash를 대조했다.
- 개발환경은 Python 3.13.15 `.venv`와 고정 의존성을 사용한다. 정식 빌드와 개발 및 별도 QC 빌드를 구분하며 원시 QC, EXE와 ZIP은 Git에서 제외한다.

## 주요 결정

- v0.1.0은 공급받은 원본 EXE의 변경 없는 기준 배포이며 원본 VERSION, manifest, Python과 EXE hash를 보존한다. 0.2.0은 별도 src 복구 구현의 빌드다.
- 사용자 승인으로 main 병합과 v0.2.0 공개를 완료했다. 원개발자 직장인과 후속 개발자 plcmanjp의 크레딧 및 외부 라이브러리 고지를 유지하며 원본에 임의 라이선스를 부여하지 않는다.
- 작업지시는 GitHub Issues가 소유한다. 공개 릴리스 결과는 Issue #6과 `qc/release-v0.2.0.json`에 있다.

## 검증 결과

- 릴리스 main의 Windows CI 69개 검사가 통과했다. 로컬에서 권한 부족으로 건너뛴 native symlink 검사도 CI에서 실제 통과했다. 공개 검수와 artifact 독립 대조가 PASS다.
- 최종 ZIP의 EXE를 실행해 실제 Explorer 파일 드롭, 파일 선택과 DXF 저장을 확인했다. 4개 라벨, TEXT와 LWPOLYLINE 각각 7개, mm 및 AC1024, 한글과 숫자 읽기 일치 및 audit 오류 0개다.
- 실제 공개 latest API가 0.2.0을 반환한다. 이전 0.2.0.dev1 앱의 수동 및 재시작 자동 업데이트 팝업에서 실제 새 릴리스를 확인했다. 게시 ZIP과 checksum 재다운로드 및 기존 v0.1.0 보존을 확인했다.

## 미해결 사항

- 실제 CAD의 글꼴 및 도면 수용과 Python 없는 별도 PC 실행은 미검증이며 DWG 직접 출력은 미지원이다.
- 원본 소스와 공급받은 EXE의 대응, 원본 EXE의 의존성 및 구체적인 수정, 상업 이용과 추가 재배포 조건은 별도 확인 항목이다. 후속 앱의 고지는 원본 EXE의 조사 결과가 아니다.

## 다음 작업

1. 합성 DXF를 실제 사용하는 CAD에서 열어 한글, 글꼴, mm 규격과 레이어를 확인한다.
2. Python 없는 별도 Windows PC에서 ZIP 전체 압축 해제와 EXE 및 DXF 생성을 확인한다.
3. 원본 빌드 자료와 구체적인 이용 조건을 확보하고 Issue #2의 남은 조건을 정리한다.
