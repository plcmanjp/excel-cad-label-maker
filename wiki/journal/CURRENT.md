# 작업 저널 (CURRENT)

## 목표

- 최신 경량화 앱 [v0.2.1](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.2.1)을 공개하고 Issue #2와 #15를 완료했다. 실제 CAD 및 별도 PC와 원본 조건의 후속 확인은 Issue #14에서 관리한다.

## 현재 상태

- [PR #13](https://github.com/plcmanjp/excel-cad-label-maker/pull/13)은 main에 병합됐으며 Issue #12는 CLOSED다. pandas 제거와 직접 읽기 및 TXT 출력과 고지 충돌 거부를 구현하고 최종 빌드 및 압축 해제 앱 QC를 완료했다.
- 앱 구현은 project/src, 원본은 project/original, 제품과 빌드 보호 검사는 project/tests에서 관리한다. 문서는 wiki, 배포 자료는 release에 있으며 .venv와 .local은 루트에 유지한다.
- [PR #16](https://github.com/plcmanjp/excel-cad-label-maker/pull/16)은 main에 병합됐고 v0.2.1은 최신 정식 공개 버전이다. 원격 tag와 latest 및 공개 ZIP과 체크섬 재다운로드를 검증했다. 기존 v0.1.0과 v0.2.0은 보존했다.

## 주요 결정

- Issue #2는 복구 소스와 재현 가능한 빌드 완료로 CLOSED다. 실제 CAD, 별도 PC와 원본 대응 및 이용 조건은 [후속 Issue #14](https://github.com/plcmanjp/excel-cad-label-maker/issues/14)에서 OPEN 및 미검증을 유지한다.
- 원본과 외부 고지의 byte를 보존한다. 빌드 출력의 Markdown 고지는 내용 변경 없이 .txt 이름으로 제공하고 출력 provenance를 맞춘다.
- numpy는 ezdxf의 필수 의존성이므로 유지한다. pandas 제거는 기존 읽기 결과와 날짜, bool, 오류 및 수식 캐시 대조를 통과해 채택했다.
- CURRENT 한글 전송 손상을 UTF-8 파일 편집으로 복구했다. 실제 CURRENT 구조를 기존 hook 파서로 확인하는 예방 검증을 추가한다.

## 검증 결과

- CI77개와 독립 검수 및 최종 ZIP 실제 앱의 드롭과 DXF 저장이 PASS다. 공개0.2.0 앱의 시작에서 0.2.1 자동 알림을 확인했고 최신 앱의 수동 조회도 정상이다. 정확한 빌드 commit과 hash 및 공개 readback은 [릴리스 QC](../../release/qc/release-v0.2.1.json)에 있다.

## 미해결 사항

- 실제 CAD, 별도 PC와 원본의 세부 이용 조건은 Issue #14의 미검증 범위다. DWG 직접 출력은 미지원이다.

## 다음 작업

1. 실제 CAD에서 합성 DXF의 글꼴과 정렬 및 도면 수용을 확인한다.
2. Python 없는 별도 Windows x64 사용자 PC의 무설치 앱 실행을 확인한다.
3. 원본 빌드 정보와 세부 이용 조건의 근거를 확보해 Issue #14에 기록한다.
