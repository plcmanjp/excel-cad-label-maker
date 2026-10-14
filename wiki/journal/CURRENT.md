# 작업 저널 (CURRENT)

## 목표

- [Issue #15](https://github.com/plcmanjp/excel-cad-label-maker/issues/15)에 따라 검증된 최신 경량화 빌드를 0.2.1로 공개하고 Issue #2의 복구 및 빌드 작업을 완료 처리한다.

## 현재 상태

- [PR #13](https://github.com/plcmanjp/excel-cad-label-maker/pull/13)은 main에 병합됐으며 Issue #12는 CLOSED다. pandas 제거와 직접 읽기 및 TXT 출력과 고지 충돌 거부를 구현하고 최종 빌드 및 압축 해제 앱 QC를 완료했다.
- 앱 구현은 project/src, 원본은 project/original, 제품과 빌드 보호 검사는 project/tests에서 관리한다. 문서는 wiki, 배포 자료는 release에 있으며 .venv와 .local은 루트에 유지한다.
- release/v0.2.1에서 제품과 릴리스 및 사용자 안내 버전을 맞추고 공개 릴리스 노트를 준비한다. 사용자가 최신 빌드의 공개 배포를 승인했다. 기존 v0.1.0과 v0.2.0은 보존한다.

## 주요 결정

- Issue #2의 복구 및 빌드는 검증된 빌드 기준으로 완료 처리하고 실제 CAD, 별도 PC와 원본 대응 및 이용 조건은 [후속 Issue #14](https://github.com/plcmanjp/excel-cad-label-maker/issues/14)에서 계속 관리한다. 미검증 항목의 판정은 유지한다.
- 원본과 외부 고지의 byte를 보존한다. 빌드 출력의 Markdown 고지는 내용 변경 없이 .txt 이름으로 제공하고 출력 provenance를 맞춘다.
- numpy는 ezdxf의 필수 의존성이므로 유지한다. pandas 제거는 기존 읽기 결과와 날짜, bool, 오류 및 수식 캐시 대조를 통과해 채택했다.
- CURRENT 한글 전송 손상을 UTF-8 파일 편집으로 복구했다. 실제 CURRENT 구조를 기존 hook 파서로 확인하는 예방 검증을 추가한다.

## 검증 결과

- 개발, 업데이트 QC 및 clean main 정식 빌드와 로컬 ZIP 및 실제 앱 QC를 통과했다. CI77개가 모두 PASS이며 원본과 공개 자산을 보존했다. 결과와 hash 및 성능 측정의 범위는 [공개 QC 기록](../../project/qc/runtime-optimization-results.json)에 있다.

## 미해결 사항

- 0.2.1 버전 변경의 검수와 CI 및 clean main 빌드, 최종 ZIP 실제 QC와 공개 및 재다운로드 검증이 남아 있다.
- 실제 CAD, 별도 PC와 원본의 세부 이용 조건은 Issue #14의 미검증 범위다. DWG 직접 출력은 미지원이다.

## 다음 작업

1. 0.2.1의 PR과 CI 및 독립 검수 후 clean main 빌드와 최종 ZIP을 확인한다.
2. 정확한 commit과 자산 hash를 대조해 v0.2.1을 latest로 공개하고 재다운로드와 기존 앱의 알림을 확인한다.
3. #2와 #15를 완료 처리하고 실제 CAD 및 별도 PC와 원본 조건의 확인은 #14에 유지한다.
