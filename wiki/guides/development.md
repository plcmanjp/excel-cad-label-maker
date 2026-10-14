# 개발 안내

## 환경 구성

Windows x64, Python 3.13.15와 Tk 8.6을 사용합니다. 저장소 루트에서 다음 명령을 실행하세요.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/setup-dev.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/run-dev.ps1
~~~

setup-dev.ps1은 .venv를 만들고 project/requirements-dev.lock.txt의 고정 의존성을 설치합니다. openpyxl과 xlrd로 Excel을 읽고 ezdxf로 DXF를 생성하며 tkinterdnd2로 Explorer 파일 드롭을 처리합니다. xlwt는 합성 .xls 테스트 입력을 만드는 도구입니다.

## 소스 구성

| 경로 | 내용 |
|---|---|
| project/src | 앱 소스와 아이콘 |
| project/tests | 변환, UI와 업데이트 및 빌드 보호 테스트 |
| project/scripts | 환경 구성과 실행 및 빌드 스크립트 |
| project/original | 보존된 원본 소스 |
| release/package | 배포 사용자 안내와 이용 조건 |
| release/third_party | 라이브러리 고지와 출처 |

현재 빌드 대상은 project/src/excel_cad_label.py입니다. project/original은 수정하지 않습니다. 기여할 변경이나 문제는 [Issues](https://github.com/plcmanjp/excel-cad-label-maker/issues)에 작성해 주세요.

input_model.py는 셀 출처와 진단을 보존하고 converter.py의 공통 배치를 미리보기와 DXF가 사용합니다. label_ui.py와 preview.py는 Tk 화면, jobs.py는 취소와 작업 세대 및 최종 파일 교체, settings_store.py는 버전 있는 설정을 관리합니다. text_bitmap.py는 Windows GDI를 이용해 글자의 가로 배율을 미리보기에 적용합니다.

working_data.py는 원본 분석에 수정/추가를 적용하는 메모리 모델이며 label_editor.py는 공통 편집 모달입니다. 원본 Excel에 쓰지 않으며 편집 revision과 렌더링 revision을 대조해 오래된 결과의 저장을 차단합니다.

설정 격리는 실행 프로세스의 EXCEL_CAD_LABEL_SETTINGS_DIR 환경 변수로 지정할 수 있습니다. 테스트와 측정은 임시 경로를 지정하며 실제 사용자 설정을 수정하지 않습니다.

## 테스트와 빌드

~~~powershell
& .venv/Scripts/python.exe -B -m unittest discover -s project/tests -v
& .venv/Scripts/python.exe -B -m unittest discover -s release/tests -v
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/build-dev.ps1
~~~

개발 앱은 project/dist/Excel_CAD_Label_Dev에 생성됩니다. EXE와 _internal 및 third_party를 함께 배포해야 합니다. 빌드 전에 같은 출력 폴더에서 실행 중인 앱을 닫으세요.

정식 빌드는 build-dev.ps1에 -Release를 추가합니다. 결과는 release/artifacts/Excel_CAD_Label에 생성됩니다. 캐시와 산출물 및 .venv는 Git에서 제외됩니다. 링크된 출력 경로는 빌드와 패키징에서 거부합니다.

빌드는 필요한 Windows x64용 TkDnD만 포함하며 라이브러리 고지 원문을 보존한 TXT 안내를 생성합니다. 의존성과 성능 측정은 [라이브러리 구성](../reference/runtime-dependencies.md), 공개 패키징은 [릴리스 절차](releasing.md)를 참고하세요.

## 업데이트 알림과 UI 확인

정상 앱의 버전은 project/src/app_version.py에서 관리합니다. 업데이트 조회는 백그라운드에서 수행하며 앱의 Tk 이벤트 루프에서 알림을 표시합니다. Excel 파일과 저장 대화상자가 열려 있으면 알림을 지연합니다. HTTP redirect 및 다른 저장소의 릴리스 URL은 수용하지 않습니다.

알림 배치를 확인하려면 별도의 테스트 진입점을 사용하세요. 정상 배포 앱에는 버전 override를 넣지 않습니다.

~~~powershell
& .venv/Scripts/python.exe -B project/qc/update-notice-gui.py --scenario live-older --geometry 740x760+650+100 --report .local/update-check.json
powershell -NoProfile -ExecutionPolicy Bypass -File project/scripts/build-update-qc.ps1
~~~

## 기여 시 참고

- 사용자 문서에는 사용 방법, 변경 사항과 필요한 제한을 설명합니다. 개발 과정의 대화와 도구 운영 내역을 넣지 않습니다.
- 원개발자의 크레딧과 라이브러리 고지 원문을 유지합니다.
- 테스트 입력은 합성 자료를 사용하고 고객 파일이나 개인 경로는 커밋하지 않습니다.
- DXF는 AC1024, mm와 UTF-8을 사용합니다. 실제 CAD의 글꼴과 렌더링은 사용하는 CAD에서 확인해야 합니다.
