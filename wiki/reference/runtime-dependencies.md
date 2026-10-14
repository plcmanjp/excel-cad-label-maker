# 런타임 의존성과 최적화 검토

## 현재 구성

| 모듈 | 역할 | 판단 |
|---|---|---|
| Python 표준 라이브러리, Tk/Tcl | GUI, 파일, XML/ZIP와 네트워크 및 업데이트 | 유지 |
| tkinterdnd2 및 TkDnD | Explorer 파일 드롭 | Windows x64, Tk 8.6용 자료만 수집 |
| openpyxl, et_xmlfile | xlsx 첫 시트 읽기, 값과 수식 캐시 | read_only 및 data_only로 직접 읽기 |
| xlrd | 구형 xls 읽기 | 직접 읽기, 날짜와 bool 및 오류 처리를 유지 |
| ezdxf | R2010 DXF, 텍스트와 폴리라인 및 스타일과 레이어 | 유지 |
| numpy, fonttools, pyparsing, typing_extensions | ezdxf 필수 의존성 | 유지 |
| PyInstaller, hooks, altgraph, packaging, pefile, pywin32-ctypes, setuptools | Windows 빌드와 아이콘 검사 | 개발 도구 |
| xlwt | 합성 xls 회귀 fixture | 검사 도구 |

pandas, python-dateutil, six와 tzdata는 잠금 목록에서 제거했다. 앱은 DataFrame이 필요한 분석이나 집계를 하지 않으며 같은 Excel 엔진을 직접 사용한다. 이전 개발환경에 남은 pandas는 비교 측정용으로만 사용하고 빌드에서 명시적으로 제외한다. receipt의 dependencies는 빌드 환경의 설치 목록이며 실제 포함 모듈 전체와 동일하다고 표현하지 않는다.

## 동작 유지와 측정

합성 xlsx와 xls 및 수식 캐시와 잘못된 worksheet dimension을 포함한 49개 workbook을 기존 구현과 대조해 라벨 묶음이 일치했다. 날짜, 시간, 오류, 첫 시트 및 bool과 0 및 1을 섞었을 때 기존 object reader의 열별 처리도 유지한다. XLS 날짜 반올림 경계는 1900 및 1904 epoch에 대한 별도 회귀 검사로 확인한다. read_only workbook은 finally에서 닫고 xlrd 리소스도 해제한다.

같은 Windows PC와 Python 3.13.15에서 최종 폴더 크기는 87,078,780 bytes에서 65,536,735 bytes로 약 24.7% 줄었다. 이 크기는 receipt와 고지를 포함한 실제 파일 합계다. 같은 로컬 기준선의 ZIP은 39,863,064 bytes에서 29,500,045 bytes로 약 26.0% 줄었다. 기존 공개 ZIP을 교체하지 않았으며 이번 ZIP은 검증용 로컬 결과물이다. 최종 검증 결과는 [공개 QC 기록](../../project/qc/runtime-optimization-results.json)에 있다.

20,000셀(2,000행, 10열)의 라벨 입력을 각 방식 5회 읽은 중앙값은 기존 0.1163초, 직접 읽기 0.1102초다. 이 작은 차이를 모든 파일에서의 성능 보장으로 확대하지 않는다. 새 Python 프로세스에서 converter import를 교차 7회 측정한 중앙값은 0.6929초에서 0.5856초로 약 15.5% 줄었다. OS 디스크 캐시는 비우지 않았으며 실제 frozen GUI 시작 시간의 측정 결과가 아니다.

원시 합성 fixture와 비교 코드 및 로그는 Git에서 제외되는 .local/runtime-qc에 있다. 실제 고객 자료를 사용하지 않는다.

## 검토한 대안

- openpyxl의 read_only 모드는 대용량 파일을 행별로 읽고 명시적으로 닫아야 한다. 잘못된 dimension은 reset_dimensions로 보정한다. 기존 pandas도 같은 엔진과 옵션을 사용하므로 중간 DataFrame과 수치 변환 비용을 줄이는 방식이 변경 범위가 작다. [openpyxl 문서](https://openpyxl.readthedocs.io/en/stable/optimized.html)
- numpy와 fonttools를 제거하면 ezdxf의 필수 의존성을 깨뜨린다. numpy.libs가 큰 비중을 차지해도 이번 검증만으로 임의 제외하지 않는다. [ezdxf 의존성](https://ezdxf.readthedocs.io/en/stable/setup.html)
- DXF를 직접 작성하거나 다른 DXF writer로 전환하면 더 작은 결과물이 가능할 수 있지만 현재 스타일, UTF-8, mm와 정렬 및 실제 CAD 수용을 다시 검증해야 한다. 이번에는 채택하지 않는다.
- Rust 기반 calamine 등 Excel 엔진 교체는 별도 네이티브 의존성과 값 변환 및 날짜 처리의 대조가 필요하다. 이미 포함된 엔진 직접 읽기의 효과부터 확인한다. [pandas Excel 엔진 문서](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- PyInstaller custom hook으로 필요한 플랫폼의 TkDnD DLL과 Tcl 자료만 수집한다. 외부 패키지 원본은 수정하지 않으며 실제 frozen EXE의 파일 드롭 검수로 확인한다. [PyInstaller hook 문서](https://www.pyinstaller.org/en/stable/hooks.html)

사용자용 안내는 Markdown을 제거한 UTF-8 일반 텍스트로 제공한다. 외부 법률 고지의 내용은 보존하고 출력 확장자만 바꾸며 출력 provenance와 checksum을 대조한다. 전체 출력 파일명은 Windows 대소문자 규칙으로 사전 대조하며 기존 파일, 고지 또는 provenance의 이름 충돌은 쓰기 전에 거부한다. 저장소 원본 고지는 그대로 유지한다.
