# 배포 자산

| 경로 | 역할 |
|---|---|
| app-release.json | 후속 앱의 버전, 소스와 배포 이름 구성 |
| baseline/ | 변경 없는 0.1.0 기준 배포의 VERSION과 원본 hash manifest |
| package/ | Windows 사용자 안내, 크레딧과 권리 고지 |
| notes/ | 공개 버전별 릴리스 노트 |
| scripts/, tests/ | 빌드 영수증, 패키징과 외부 고지 수집 및 거부 조건 검사 |
| third_party/ | 외부 라이브러리 고지 원문과 출처 및 hash |
| qc/ | 기준 EXE 실행 및 공개 릴리스 검수 기록 |
| artifacts/ | Git에서 제외되는 정식 빌드, ZIP과 체크섬 |

기존 릴리스 파일은 `artifacts/v0.1.0/`과 `artifacts/v0.2.0/`에 보존합니다. 정식 앱 빌드 출력은 `artifacts/Excel_CAD_Label/`, 기준 배포 재검사 출력은 `artifacts/baseline-build/`입니다. 이미 게시한 ZIP을 새 빌드로 덮어쓰지 않습니다.

빌드와 공개 절차는 [릴리스 안내](../wiki/guides/releasing.md), 고지의 출처는 [참고 자료](../wiki/reference/third-party.md)에서 확인합니다. 작업지시는 GitHub Issues에서 관리하며 공개는 해당 버전의 사용자 승인 범위를 따릅니다.
