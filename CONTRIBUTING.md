# 개발 안내

작업지시의 단일 정본은 이 저장소의 [GitHub Issues](https://github.com/plcmanjp/excel-cad-label-maker/issues)입니다. 변경 전 해당 Issue 원문과 AGENTS.md 및 필수 규칙을 읽습니다. 진행 상태만 wiki/journal/CURRENT.md에 요약합니다.

## 현재 개발 기준선

Project/P001-excel-cad-label/original/excel_cad_label.py는 전달받은 원본입니다. 문법 손상 때문에 제품 실행 또는 빌드 대상이 아닙니다. 원본 파일을 보존하고 복구 구현은 별도 src/와 tests/에 추가합니다. 원본 EXE와 소스의 일치 여부는 확인되지 않았습니다.

Python 의존성 목록과 패키징 설정은 재현 가능한 빌드 작업에서 실제 환경을 확인한 뒤 고정합니다. 현재 저장소에는 작동한다고 추정한 requirements.txt나 빌드 명령을 제공하지 않습니다.

## 하네스 검증

저장소 루트에서 Python 3.14로 검증합니다.

~~~powershell
python -B .agents/scripts/test_session_start.py
python -B .agents/scripts/check_repository.py
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/setup/register-hooks.ps1
~~~

마지막 명령은 현재 PC의 절대 경로를 담은 로컬 .codex/hooks.json만 생성합니다. 해당 파일은 Git에서 제외하며 각 PC에서 등록합니다. Codex trust와 /hooks 승인은 런타임에서 별도로 확인합니다. Claude 전용 설정은 해당 도구의 담당 세션에서 구성합니다.

일반 commit과 push는 승인된 개발 작업의 완료 절차입니다. 공개 릴리스와 외부 배포는 버전과 대상에 대한 사용자 승인 범위를 지킵니다. 커밋 메시지는 한국어로 작성합니다. 비밀과 개인 경로, 고객 자료는 커밋하지 않습니다.
