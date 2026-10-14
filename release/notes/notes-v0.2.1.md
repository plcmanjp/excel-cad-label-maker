# Excel CAD Label Maker 0.2.1

일반 텍스트 안내와 런타임 경량화를 적용한 Windows x64 무설치 앱입니다. 원개발자는 직장인, Fork 및 후속 개발자는 plcmanjp입니다. 별도 복구 소스로 빌드한 후속 앱이며 제공받은 원본 0.1.0 EXE와 같은 재빌드가 아닙니다. 공개 v0.1.0과 v0.2.0은 보존합니다.

## 변경 사항

- README, NOTICE와 CREDITS 및 외부 고지의 빌드 출력은 .txt로 제공합니다. 사용자 안내는 일반 텍스트로 변환하고 외부 고지 내용은 byte를 보존했습니다.
- pandas DataFrame 대신 기존 openpyxl과 xlrd 엔진을 직접 읽어 중간 처리와 포함 모듈을 줄였습니다. 첫 시트와 열 순서, 빈 셀 구분과 숫자, bool, 날짜 및 수식 캐시의 처리를 대조했습니다.
- 파일 드롭 모듈은 Windows x64와 Tk 8.6에 필요한 자료만 포함합니다. ezdxf의 필수 numpy 등은 유지합니다.
- 기존 Excel 드래그 앤 드롭, UTF-8 DXF 생성, ABC 흰 라벨 아이콘과 GitHub 업데이트 알림을 유지합니다.

## 다운로드와 실행

Excel-CAD-Label-Maker-0.2.1-windows-x64.zip 전체를 새 폴더에 압축 해제하고 Excel_CAD_Label.exe를 실행하세요. _internal과 third_party 및 다른 포함 파일을 함께 유지해야 합니다. 사용자 PC에서 Python을 별도로 설치하지 않아도 되도록 런타임을 포함합니다. ZIP은 함께 제공하는 SHA256SUMS.txt로 확인할 수 있습니다.

0.2.0 앱은 실행 시 이 릴리스를 새 버전으로 안내합니다. 알림에서 릴리스 페이지를 열어 새 ZIP을 내려받으세요. 자동 다운로드와 설치 또는 실행 파일 교체는 하지 않습니다. 0.1.0 원본 EXE에는 업데이트 알림이 없습니다.

## 검증과 확인 범위

Windows CI와 변환 및 빌드 보호 검사, 라이브러리 고지 및 hash와 독립 검수를 확인합니다. 최종 ZIP의 실제 앱에서 Excel 드롭과 DXF 저장 및 UTF-8, ABC 아이콘과 업데이트 조회를 확인한 결과는 릴리스 QC 기록에 연결합니다. converter import 측정을 실제 GUI 시작 시간이나 모든 Excel 파일의 성능 보장으로 표현하지 않습니다.

실제 사용하는 CAD에서의 글꼴과 도면 수용, Python 없는 별도 사용자 PC 실행, 원본 EXE 및 소스 대응과 원권리자의 세부 수정, 상업 이용 및 추가 재배포 조건은 [후속 Issue #14](https://github.com/plcmanjp/excel-cad-label-maker/issues/14)에 남아 있습니다. DWG 직접 출력은 지원하지 않습니다. 포함 NOTICE.txt의 권리 범위를 확인하세요. 원본에 임의 오픈소스 라이선스를 부여하지 않습니다.

복구 및 빌드 작업은 Issue #2, 경량화는 Issue #12 및 PR #13, 이번 공개와 결과는 [Issue #15](https://github.com/plcmanjp/excel-cad-label-maker/issues/15)에서 확인할 수 있습니다.
