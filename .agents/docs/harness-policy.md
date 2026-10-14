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
| 로컬 훅 등록 | .codex/setup/register-hooks.ps1 |
| 릴리스 운영 | wiki/guides/releasing.md |
| 사용자와 개발 문서 | wiki/guides/, wiki/reference/ |
| 에이전트 운영 자료 | .agents/docs/ |
| 앱 개발 자산 | project/INDEX.md |
| 배포 자산 | release/INDEX.md |
| 원개발자와 후속 개발자 | release/package/CREDITS.md |
| 권리와 재배포 범위 | release/package/NOTICE.md |

기존 규칙의 오타와 경로 정정은 승인된 범위에서 처리합니다. 구조와 행동을 바꾸는 하네스 변경은 제안과 승인을 거칩니다. 공개 배포, remote 변경과 force push는 사용자 승인 범위를 확인합니다. Claude 전용 설정은 해당 도구 담당자가 구성합니다.
