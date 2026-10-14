# 외부 라이브러리 고지

저장소의 `release/third_party/notices/`는 검증된 개발환경과 Python/Tk 및 TkDnD 런타임에서 수집한 저작권과 라이선스 원문입니다. `release/third_party/provenance.json`은 원문의 출처와 SHA-256을 기록합니다. wheel에 고지가 없는 패키지는 같은 버전의 공식 PyPI 소스 배포본을 다운로드하고 게시된 SHA-256과 비교한 뒤 고지를 수집했습니다. 사용하지 않는 과거 의존성의 고지도 보존할 수 있으며 현재 설치 목록은 `project/requirements-dev.lock.txt`입니다.

Windows 앱에는 `third_party/notices/`, `third_party/provenance.json`과 이 안내를 README.txt로 포함합니다. 원본 `.md` 고지는 byte를 바꾸지 않고 빌드 출력에서 `.txt`로 제공하며 출력 provenance 경로도 맞춥니다. 개발 도구와 보존된 과거 의존성의 고지도 제공하므로 여기의 모든 패키지가 앱 런타임에서 사용된다는 뜻은 아닙니다.

재수집은 저장소 루트에서 `& .venv/Scripts/python.exe -B release/scripts/collect-notices.py`로 실행합니다. 설치환경의 버전이 잠금 목록과 일치해야 합니다. 외부 고지는 바이트 그대로 유지합니다.

원본 프로그램의 권리 조건은 [저장소 고지](https://github.com/plcmanjp/excel-cad-label-maker/blob/main/release/package/NOTICE.md) 및 앱 폴더의 NOTICE.txt를 따릅니다. 이 자료는 원본 0.1.0 EXE의 의존성 고지를 확정한 결과가 아니며 원본에 새 라이선스를 부여하지 않습니다.
