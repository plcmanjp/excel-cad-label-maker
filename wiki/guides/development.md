# 개발 안내

작업지시의 단일 정본은 이 저장소의 [GitHub Issues](https://github.com/plcmanjp/excel-cad-label-maker/issues)입니다. 변경 전 해당 Issue 원문과 AGENTS.md 및 필수 규칙을 읽습니다. 진행 상태만 wiki/journal/CURRENT.md에 요약합니다.

## 현재 개발 기준선

project/original/excel_cad_label.py는 전달받은 원본입니다. 문법 손상 때문에 제품 실행 또는 빌드 대상이 아닙니다. 원본 파일을 보존하고 복구 구현은 별도 src/와 tests/에 추가합니다. 원본 EXE와 소스의 일치 여부는 확인되지 않았습니다.

복구 구현은 `project/src/`에 있습니다. 원본의 열 방향 읽기와 가변 높이 배치를 복구하고, Excel 파일 드래그 앤 드롭과 UTF-8 DXF 출력을 추가했습니다. 원본 EXE와 바이트 또는 기능이 동일한 재빌드라고 표현하지 않습니다.

## 개발환경

Windows x64와 Python **3.13.15**를 사용합니다. 저장소 루트에서 다음 명령을 실행하세요. `setup-dev.ps1`은 `.venv`에만 패키지를 설치합니다. 활성화 없이도 아래 명령을 사용할 수 있습니다.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/setup-dev.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/run-dev.ps1
~~~

`project/requirements-dev.lock.txt`는 실제 검증 환경의 직접 및 간접 의존성을 고정합니다. openpyxl 3.1.5, xlrd 2.0.2, ezdxf 1.4.4, tkinterdnd2 0.6.4와 PyInstaller 6.22.3을 사용합니다. Excel 엔진을 직접 읽으며 pandas와 그 전용 의존성은 설치 목록에서 제외합니다. xlwt는 합성 `.xls` 검사 파일 생성용입니다. `.venv`는 개발과 검증에 사용할 수 있고 Git에서 제외됩니다.

## 제품 검사와 Windows 개발 빌드

~~~powershell
& .venv/Scripts/python.exe -B -m unittest discover -s project/tests -v
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/build-dev.ps1
~~~

생성 앱은 `project/dist/Excel_CAD_Label_Dev/Excel_CAD_Label_Dev.exe`입니다. **EXE와 `_internal/`, `third_party/` 등 같은 폴더의 파일을 함께 유지**해야 합니다. Python이 없는 사용자 PC에서 실행하는 무설치 폴더 형태이며, 단일 EXE 형태는 아닙니다. `project/dist/`, `project/build/`와 `release/artifacts/`는 Git에서 제외됩니다.

재빌드 전 실행 중인 개발 앱을 닫으세요. 스크립트는 실행 중인 앱과 빌드 경로의 junction 및 symlink를 거부합니다. 생성된 출력 폴더의 OneDrive 읽기 전용 속성은 경로 검사를 통과한 뒤 처리합니다.

`project/tests/`는 제품과 빌드 보호 검사 39개를 함께 관리합니다. 빌드 스크립트가 이 검사를 실행하며 CI에서는 별도 배포 검사 16개와 하네스 검사 22개를 더해 총 77개를 확인합니다. 로컬 Windows의 symlink 권한이 없으면 해당 배포 검사 1개는 건너뛰고 CI 결과와 구분합니다.

사용자용 README, NOTICE와 CREDITS는 빌드에서 Markdown 표시를 제거한 `.txt`로 제공합니다. 외부 고지의 `.md`는 내용의 byte를 유지하며 출력 이름만 `.txt`로 바꾸고 출력 provenance를 갱신합니다. 배포 패키저는 Markdown 파일이 남아 있으면 거부합니다.

Windows x64와 Python 3.13의 Tk 8.6에 필요한 TkDnD만 `project/scripts/pyinstaller-hooks/`의 hook으로 수집합니다. numpy 등 ezdxf 필수 의존성은 유지합니다. 종류와 대안 및 측정 범위는 [의존성 검토](../reference/runtime-dependencies.md)에서 확인합니다.

`build-receipt.json`은 Python과 의존성 버전, Git commit 및 변경 여부, 소스와 패키지 파일의 SHA-256을 기록합니다. 같은 소스와 의존성으로 빌드 절차를 반복할 수 있다는 뜻이며, EXE 바이트가 항상 동일하다는 뜻은 아닙니다. 다른 PC의 깨끗한 환경 검증은 GitHub Actions의 Windows `product` 작업 결과로 구분합니다.

복구 앱에는 `.xlsx` 또는 `.xls` 파일 한 개를 탐색기에서 끌어다 놓으세요. 파일 찾기도 사용할 수 있습니다. 여러 파일, 다른 확장자, 삭제된 파일과 Excel 임시 파일은 거부하며 기존 선택은 보존합니다. 파일 드롭은 입력 선택이며 도면 저장은 별도의 버튼과 저장 대화상자로 진행합니다.

## 앱 아이콘

개발 앱은 흰 라벨지에 ABC가 적힌 아이콘을 사용합니다. 원본 PNG, 여러 크기의 Windows ICO와 생성 프롬프트는 [아이콘 안내](../reference/app-icon.md)에 있습니다. EXE 리소스와 Tk 창에 같은 ICO를 적용하며 개발 빌드에 포함합니다. 기존 0.1.0 배포물은 보존합니다.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/make-app-icon.ps1 -Force
~~~

이 명령은 저장된 PNG를 Windows ICO로 변환하고 자산 hash manifest를 갱신합니다. 새 이미지를 생성하거나 네트워크에 접속하지 않습니다. `build-receipt.json`은 소스 자산과 패키지에 포함된 ICO의 hash도 기록합니다.

빌드 스크립트는 `project/scripts/check-app-icon.py`로 ICO의 10개 PNG 프레임, EXE의 실제 아이콘 리소스와 포함된 Tk 자산이 같은지 검사합니다. 이 검사가 실패하면 빌드 완료로 처리하지 않습니다.

## 업데이트 알림

앱 버전은 `project/src/app_version.py`의 `APP_VERSION`으로 관리하며 현재 `0.2.0`입니다. 원본 배포의 `release/baseline/VERSION` 및 `release/baseline/manifest.json`은 0.1.0 기준선으로 보존합니다.

앱 시작 뒤 고정된 GitHub 최신 릴리스 API를 백그라운드에서 한 번 조회합니다. 설치 버전보다 새 정식 버전이 있을 때 `새 버전 알림`에 현재 및 최신 버전과 `릴리스 페이지 열기`, `나중에` 버튼을 표시합니다. 하단의 `업데이트 확인`으로 수동 조회할 수도 있습니다. 자동 다운로드나 실행 파일 교체는 하지 않습니다.

조회는 TLS 인증서 검증을 유지하고 인증 token 또는 PC 및 Excel 자료를 보내지 않습니다. 요청 timeout은 3초, 응답 본문 제한은 256KiB이며 redirect는 거부합니다. 시작 조회 실패, 동일 또는 구버전이면 오류 팝업 없이 앱을 사용할 수 있습니다. Excel 파일 및 저장 대화상자를 사용하는 동안 새 알림은 지연합니다.

알림을 수용하는 릴리스는 공개 정식 버전이며 tag가 `vX.Y.Z` 또는 `X.Y.Z`여야 합니다. 준비된 Windows ZIP 이름은 `Excel-CAD-Label-Maker-X.Y.Z-windows-x64.zip`이고 API의 업로드 상태, 크기와 저장소 URL이 일치해야 합니다. 초안, prerelease, 준비되지 않은 ZIP과 다른 저장소 URL은 알림 대상으로 수용하지 않습니다. 신규 공개 배포 시 ZIP을 준비한 뒤 정식 릴리스를 최신 버전으로 지정하세요.

이미 전달된 0.1.0 원본 EXE에 이 기능을 소급 추가할 수는 없습니다. 업데이트 알림을 포함한 후속 앱을 설치한 사용자부터 이후 릴리스 알림을 받을 수 있습니다. 새 공개 릴리스는 별도 승인 범위를 따릅니다.

## 실제 업데이트 GUI 검수

정상 EXE는 버전 override 실행 인자를 제공하지 않습니다. 별도 QC 진입점 `project/qc/update-notice-gui.py`가 제품 코드에 검수용 비교 버전을 주입하고 실제 GitHub API를 조회합니다. 이 코드와 검수 EXE를 공개 앱 배포물에 포함하지 않습니다.

~~~powershell
& .venv/Scripts/python.exe -B project/qc/update-notice-gui.py --scenario live-older --report .local/update-qc/live-older-source.json
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/build-update-qc.ps1
~~~

`live-older`는 비교 입력 0.0.1로 현재 최신 공개 릴리스를 조회해 알림을 검수하는 조건입니다. `live-current`는 정상 앱 버전을 사용합니다. 원격 릴리스나 제품 버전을 테스트용으로 변경하지 않습니다. 네트워크가 실패하면 검수 report에서도 실패를 그대로 기록합니다.

QC 빌드는 `.local/update-qc/builds/`에 새 폴더를 생성하고 `.local/update-qc/latest-build.json`에 해당 경로를 기록합니다. 그 폴더의 `Update_Notice_QC.exe`에 위와 같은 `--scenario`, `--report` 인자를 전달합니다. `build-receipt.json`의 제품 소스 SHA-256을 정상 EXE와 비교한 뒤 팝업, 나중에 및 실제 릴리스 페이지 열기를 확인합니다. 원시 경로와 UI 증거는 `.local/`에만 둡니다.

DXF는 R2010(AC1024), mm 단위, UTF-8이며 `LABEL_BOX`와 `TEXT_DATA` 레이어를 사용합니다. 긴 글자 크기 계산은 추정치이고 실제 CAD 글꼴 렌더링과 CAD별 호환성은 별도 검증 대상입니다. 글꼴 파일은 포함하지 않습니다. DWG 직접 출력은 지원하지 않습니다.

## 외부 라이브러리 고지

`release/third_party/`는 고정된 개발환경과 포함 런타임의 저작권 및 라이선스 원문을 보존합니다. 누락된 wheel 고지는 SHA-256을 확인한 같은 버전의 공식 PyPI 소스에서 수집했습니다. 재수집 명령은 `& .venv/Scripts/python.exe -B release/scripts/collect-notices.py`이며 네트워크를 사용합니다. 원문 고지를 임의 수정하지 않습니다.

원권리자의 구체적인 수정, 상업 이용 및 추가 재배포 조건은 별도 확인 항목입니다. 신규 공개 릴리스에는 확인 범위를 명시하고 해당 버전의 사용자 공개 승인을 확인합니다. 원본에 새 라이선스를 부여하지 않으며 0.1.0 릴리스와 원본 manifest는 후속 빌드가 교체하지 않습니다.

## 후속 정식 릴리스 빌드

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/build-dev.ps1 -Release
& .venv/Scripts/python.exe -B release/scripts/package-app-release.py --output release/artifacts/candidate-0.2.0
~~~

정식 빌드는 `release/artifacts/Excel_CAD_Label/Excel_CAD_Label.exe`와 Windows 사용자 안내 및 버전 파일을 생성하고 release-build receipt를 기록합니다. 패키징은 깨끗한 main, 현재 commit 및 소스와 자산, release receipt 및 모든 파일 hash를 확인합니다. 개발 receipt, 수정된 파일, 등록되지 않은 파일, 링크 경로와 기존 릴리스 파일 덮어쓰기는 거부합니다. ZIP과 SHA256SUMS.txt를 생성한 후 실제 압축 해제 앱의 QC 및 독립 검수를 마치고 승인된 버전을 공개합니다.

출력 폴더는 아직 ZIP과 체크섬이 없는 새 경로를 지정합니다. `release/artifacts/v0.1.0/`과 `v0.2.0/`은 이미 공개한 파일의 보존 경로입니다. 경로 재구성 검증용 빌드는 기존 공개 릴리스를 교체하지 않습니다.

## 하네스 검증

저장소 루트에서 `.venv`의 Python으로 검증합니다. 독립 하네스 CI는 Python 3.14도 유지합니다.

~~~powershell
& .venv/Scripts/python.exe -B .agents/scripts/test_session_start.py
& .venv/Scripts/python.exe -B .agents/scripts/check_repository.py
& .venv/Scripts/python.exe -B -m unittest discover -s release/tests -v
powershell -NoProfile -ExecutionPolicy Bypass -File .codex/setup/register-hooks.ps1
~~~

마지막 명령은 현재 PC의 절대 경로를 담은 로컬 .codex/hooks.json만 생성합니다. 해당 파일은 Git에서 제외하며 각 PC에서 등록합니다. Codex trust와 /hooks 승인은 런타임에서 별도로 확인합니다. Claude 전용 설정은 해당 도구의 담당 세션에서 구성합니다.

일반 commit과 push는 승인된 개발 작업의 완료 절차입니다. 공개 릴리스와 외부 배포는 버전과 대상에 대한 사용자 승인 범위를 지킵니다. 커밋 메시지는 한국어로 작성합니다. 비밀과 개인 경로, 고객 자료는 커밋하지 않습니다.
