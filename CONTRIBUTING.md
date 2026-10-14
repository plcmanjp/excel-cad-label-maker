# 개발 안내

작업지시의 단일 정본은 이 저장소의 [GitHub Issues](https://github.com/plcmanjp/excel-cad-label-maker/issues)입니다. 변경 전 해당 Issue 원문과 AGENTS.md 및 필수 규칙을 읽습니다. 진행 상태만 wiki/journal/CURRENT.md에 요약합니다.

## 현재 개발 기준선

Project/P001-excel-cad-label/original/excel_cad_label.py는 전달받은 원본입니다. 문법 손상 때문에 제품 실행 또는 빌드 대상이 아닙니다. 원본 파일을 보존하고 복구 구현은 별도 src/와 tests/에 추가합니다. 원본 EXE와 소스의 일치 여부는 확인되지 않았습니다.

복구 구현은 `Project/P001-excel-cad-label/src/`에 있습니다. 원본의 열 방향 읽기와 가변 높이 배치를 복구하고, Excel 파일 드래그 앤 드롭과 UTF-8 DXF 출력을 추가했습니다. 원본 EXE와 바이트 또는 기능이 동일한 재빌드라고 표현하지 않습니다.

## 개발환경

Windows x64와 Python **3.13.15**를 사용합니다. 저장소 루트에서 다음 명령을 실행하세요. `setup-dev.ps1`은 `.venv`에만 패키지를 설치합니다. 활성화 없이도 아래 명령을 사용할 수 있습니다.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup-dev.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run-dev.ps1
~~~

`requirements-dev.lock.txt`는 실제 검증 환경의 직접 및 간접 의존성을 고정합니다. pandas 3.0.6, openpyxl 3.1.5, xlrd 2.0.2, ezdxf 1.4.4, tkinterdnd2 0.6.4와 PyInstaller 6.22.3을 사용합니다. xlwt는 합성 `.xls` 검사 파일 생성용이며 앱의 읽기 엔진은 xlrd입니다. `.venv`는 개발과 검증에 사용할 수 있고 Git에서 제외됩니다.

## 제품 검사와 Windows 개발 빌드

~~~powershell
& .venv/Scripts/python.exe -B -m unittest discover -s Project/P001-excel-cad-label/tests -v
& .venv/Scripts/python.exe -B -m unittest discover -s scripts/tests -v
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build-dev.ps1
~~~

생성 앱은 `dist/Excel_CAD_Label_Dev/Excel_CAD_Label_Dev.exe`입니다. **EXE와 `_internal/`, `third_party/` 등 같은 폴더의 파일을 함께 유지**해야 합니다. Python이 없는 사용자 PC에서 실행하는 무설치 폴더 형태이며, 단일 EXE 형태는 아닙니다. `dist/`와 `build/`는 Git에서 제외됩니다.

재빌드 전 실행 중인 개발 앱을 닫으세요. 스크립트는 실행 중인 앱과 빌드 경로의 junction 및 symlink를 거부합니다. 생성된 출력 폴더의 OneDrive 읽기 전용 속성은 경로 검사를 통과한 뒤 처리합니다.

`build-receipt.json`은 Python과 의존성 버전, Git commit 및 변경 여부, 소스와 패키지 파일의 SHA-256을 기록합니다. 같은 소스와 의존성으로 빌드 절차를 반복할 수 있다는 뜻이며, EXE 바이트가 항상 동일하다는 뜻은 아닙니다. 다른 PC의 깨끗한 환경 검증은 GitHub Actions의 Windows `product` 작업 결과로 구분합니다.

복구 앱에는 `.xlsx` 또는 `.xls` 파일 한 개를 탐색기에서 끌어다 놓으세요. 파일 찾기도 사용할 수 있습니다. 여러 파일, 다른 확장자, 삭제된 파일과 Excel 임시 파일은 거부하며 기존 선택은 보존합니다. 파일 드롭은 입력 선택이며 도면 저장은 별도의 버튼과 저장 대화상자로 진행합니다.

DXF는 R2010(AC1024), mm 단위, UTF-8이며 `LABEL_BOX`와 `TEXT_DATA` 레이어를 사용합니다. 긴 글자 크기 계산은 추정치이고 실제 CAD 글꼴 렌더링과 CAD별 호환성은 별도 검증 대상입니다. 글꼴 파일은 포함하지 않습니다. DWG 직접 출력은 지원하지 않습니다.

## 외부 라이브러리 고지

`third_party/`는 고정된 개발환경과 포함 런타임의 저작권 및 라이선스 원문을 보존합니다. 누락된 wheel 고지는 SHA-256을 확인한 같은 버전의 공식 PyPI 소스에서 수집했습니다. 재수집 명령은 `& .venv/Scripts/python.exe -B scripts/collect-notices.py`이며 네트워크를 사용합니다. 원문 고지를 임의 수정하지 않습니다.

복구 앱의 신규 공개 릴리스에는 원권리자의 구체적인 수정, 상업 이용 및 추가 재배포 조건 확인과 해당 버전 공개 승인이 필요합니다. 0.1.0 릴리스와 원본 manifest는 개발 빌드가 교체하지 않습니다.

## 하네스 검증

저장소 루트에서 `.venv`의 Python으로 검증합니다. 독립 하네스 CI는 Python 3.14도 유지합니다.

~~~powershell
& .venv/Scripts/python.exe -B .agents/scripts/test_session_start.py
& .venv/Scripts/python.exe -B .agents/scripts/check_repository.py
& .venv/Scripts/python.exe -B .agents/scripts/test_package_release.py
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/setup/register-hooks.ps1
~~~

마지막 명령은 현재 PC의 절대 경로를 담은 로컬 .codex/hooks.json만 생성합니다. 해당 파일은 Git에서 제외하며 각 PC에서 등록합니다. Codex trust와 /hooks 승인은 런타임에서 별도로 확인합니다. Claude 전용 설정은 해당 도구의 담당 세션에서 구성합니다.

일반 commit과 push는 승인된 개발 작업의 완료 절차입니다. 공개 릴리스와 외부 배포는 버전과 대상에 대한 사용자 승인 범위를 지킵니다. 커밋 메시지는 한국어로 작성합니다. 비밀과 개인 경로, 고객 자료는 커밋하지 않습니다.
