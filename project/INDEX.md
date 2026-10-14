# 구현 자산

| 경로 | 역할 |
|---|---|
| original/ | 전달받은 원본 Python 소스 보존 |
| src/ | 복구 구현, Excel 드래그 앤 드롭 UI와 UTF-8 DXF 변환 및 아이콘 자산 |
| tests/ | 합성 Excel, DXF 구조, Tk 위젯과 업데이트 알림 및 빌드 보호 회귀 검사 |
| scripts/ | 개발환경 구성, 소스 실행, 앱 및 검수 빌드, 아이콘과 합성 샘플 생성 |
| requirements-dev.lock.txt | 개발 및 빌드 의존성 잠금 목록 |
| qc/ | 개발 빌드, 아이콘과 업데이트 알림 검수 기록 및 GUI 진입점 |
| build/, dist/ | Git에서 제외되는 빌드 캐시와 개발 앱 |

앱 구현은 src/와 tests/에서 관리합니다. 실행 파일과 ZIP은 GitHub Releases에서 배포합니다.

실행과 빌드 명령은 [개발 안내](../wiki/guides/development.md), 패키징 자료는 [배포 구성](../release/INDEX.md)에서 확인합니다.
