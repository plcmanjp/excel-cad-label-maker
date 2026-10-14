# 작업 저널 (CURRENT)

## 목표

- [Issue #12](https://github.com/plcmanjp/excel-cad-label-maker/issues/12)에 따라 빌드 안내를 일반 텍스트로 제공하고 같은 Excel/DXF 동작을 유지하며 런타임 의존성과 용량 및 실행 비용을 줄인다.

## 현재 상태

- perf/issue-12-runtime-and-text에서 pandas를 제거하고 Excel 엔진 직접 읽기 및 Windows x64 전용 TkDnD 수집을 구현했다. TXT 출력과 고지 보존 및 충돌 거부를 검증했다. PR과 CI 및 clean main 패키징 확인이 남아 있다.
- 앱 구현은 project/src, 원본은 project/original, 제품과 빌드 보호 검사는 project/tests에서 관리한다. 문서는 wiki, 배포 자료는 release에 있으며 .venv와 .local은 루트에 유지한다.
- 공개 v0.2.0과 v0.1.0은 보존한다. 신규 검증 빌드는 공개 버전과 구분한다.

## 주요 결정

- [Issue #2](https://github.com/plcmanjp/excel-cad-label-maker/issues/2)는 실제 CAD, Python 없는 별도 PC와 원본 이용 조건 확인이 남아 있어 OPEN을 유지한다. 원본 소스와 제공된 EXE의 빌드 대응은 확인되지 않았다.
- 원본과 외부 고지의 byte를 보존한다. 빌드 출력의 Markdown 고지는 내용 변경 없이 .txt 이름으로 제공하고 출력 provenance를 맞춘다.
- numpy는 ezdxf의 필수 의존성이므로 유지한다. pandas 제거는 기존 읽기 결과와 날짜, bool, 오류 및 수식 캐시 대조를 통과해 채택했다.
- CURRENT 한글 전송 손상을 UTF-8 파일 편집으로 복구했다. 실제 CURRENT 구조를 기존 hook 파서로 확인하는 예방 검증을 추가한다.

## 검증 결과

- 기존 reader와 49개 합성 workbook의 라벨 묶음이 일치한다. 새 Python 프로세스 converter import 중앙값은 약 15.5% 감소했으며 frozen GUI 시작 시간으로 표현하지 않는다.
- 초기 후보 폴더는 87,078,780 bytes에서 65,536,853 bytes로 약 24.7% 감소했다. 실행 EXE의 실제 Explorer 드롭과 DXF 저장, 라벨 4개 및 개체 7쌍과 위치 및 스타일 대조와 audit 오류 0건을 확인했다. 날짜 경계 보정 후 최종 빌드는 별도 확인한다.
- 로컬 product39, release16 및 harness22를 실행해 76 PASS, native symlink 권한 부족 1 SKIP이다. 원본과 아이콘 및 고지와 공개 ZIP 68개 hash는 보존됐다. 날짜 경계 및 고지 충돌의 독립 검수 finding은 보정 후 delta 검수를 통과했다.

## 미해결 사항

- 이번 변경의 최종 개발 빌드, CI 및 clean main 정식 빌드와 ZIP 확인이 남아 있다.
- 실제 CAD, 별도 PC와 원본의 세부 이용 조건은 Issue #2의 미검증 범위다. DWG 직접 출력은 미지원이다.

## 다음 작업

1. 최종 개발 빌드와 CI를 확인하고 검증된 PR을 main에 반영한다.
2. clean main 정식 빌드와 신규 로컬 ZIP의 크기 및 hash와 TXT 고지 및 실제 동작을 확인한다.
3. 결과와 한계를 Issue #12 및 #2와 공개 QC 및 journal에 기록한다.
