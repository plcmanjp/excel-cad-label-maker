# 하네스 정책

이 저장소는 Excel CAD Label Maker의 공개 개발 및 릴리스를 함께 소유합니다. 900 스타터의 중립 규칙, 역할 정본, Codex 어댑터와 SessionStart 회귀 검사를 기반으로 구성합니다. 스타터의 이력, 부모 운영 문서와 타 제품 자료는 복제하지 않습니다.

## 정본 레지스트리

| 영역 | 경로 |
|---|---|
| 단일 진입점 | AGENTS.md |
| 운영 규칙 | .agents/rules/ |
| 작업지시 | GitHub Issues: plcmanjp/excel-cad-label-maker |
| 진행 상태 | wiki/journal/CURRENT.md |
| 역할 정본 | .agents/agents/ |
| Codex 런타임 어댑터 | .codex/agents/ |
| 공용 프로젝트 메모리 색인 | .agents/memory/MEMORY.md |
| SessionStart 실행 본문 | .agents/hooks/session_start_status.py |
| 합성 하네스 시험 임시 경로 | .agents/scripts/fixture_temp.py |
| 로컬 훅 등록 | .codex/setup/register-hooks.ps1 |
| 릴리스 운영 | wiki/guides/releasing.md |
| 사용자와 개발 문서 | wiki/guides/, wiki/reference/ |
| 에이전트 운영 자료 | .agents/docs/ |
| 앱 개발 자산 | project/INDEX.md |
| 배포 자산 | release/INDEX.md |
| 원개발자와 후속 개발자 | release/package/CREDITS.md |
| 권리와 재배포 범위 | release/package/NOTICE.md |

기존 규칙의 오타와 경로 정정은 승인된 범위에서 처리합니다. 구조와 행동을 바꾸는 하네스 변경은 제안과 승인을 거칩니다. 공개 배포, remote 변경과 force push는 사용자 승인 범위를 확인합니다. Claude 전용 설정은 해당 도구 담당자가 구성합니다.

## 하네스 시험 임시 자료

합성 fixture와 소모성 중간 출력은 현재 OS 사용자 Temp 아래 `excel-cad-harness/<저장소 식별자>/fixture-<고유 run ID>/`에 만듭니다. `.agents/scripts/fixture_temp.py`는 이 저장소만의 작은 검증 함수이며 부모 공용 엔진을 복제하거나 import하지 않습니다. Python의 OS Temp 선택 결과를 확인하고 workspace, OneDrive 환경 변수와 Windows 등록 계정 루트 안이면 생성을 거부합니다. 기존 경로의 링크와 reparse point도 거부하며 판독 오류를 무시하거나 workspace 내부로 fallback하지 않습니다. 전역 TEMP/TMP나 Windows 정리 설정은 변경하지 않습니다.

`FixtureDirectory`의 context 종료와 `cleanup()`은 정상 종료와 실패 모두에서 자료를 보존합니다. 부재 반례는 이전 payload를 고유 이름으로 바꾸어 보존합니다. 수명은 OS와 사용자의 정리 정책에 맡기며 자동 삭제 일정이나 정리 완료를 보장하지 않습니다. 이 검사는 생성 시점의 경계를 확인하며 다른 프로세스가 이후 경로를 바꾸는 상황의 보안 격리를 보장하지 않습니다.

고유 실패 증거와 재현 입력은 필요한 부분을 기존 내부 QC 기록 또는 작업지시가 정한 정식 보관 위치에 선별합니다. 승인된 원본, 미통합 작업과 고유 증거를 Temp에만 남기지 않습니다. 원본 개인정보와 Git 제외 정책을 유지하고 자동 Git 추가나 외부 업로드를 하지 않습니다. 실제 제품 데이터와 제품 저장 계약은 이 하네스 fixture 계약에 포함하지 않습니다.

저장소 루트에서 `python -B .agents/scripts/test_fixture_temp.py`로 실제 생성 경로, 경계 거부와 정상/실패 보존을 검사합니다. `python -B .agents/scripts/test_session_start.py`는 같은 보존형 fixture를 사용하는 SessionStart 회귀 검사입니다. 출력의 `PRESERVED_FIXTURE_RUN`과 `PRESERVED_FAILURE_RUN`은 실행별 확인용이며 소스에 개인 절대 경로를 기록하지 않습니다.
