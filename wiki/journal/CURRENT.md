# 작업 저널 (CURRENT)

## 목표

- [Issue #17](https://github.com/plcmanjp/excel-cad-label-maker/issues/17)에 따라 업데이트 알림을 앱 중앙에 표시하고 사용자 문서와 배포 안내를 제품 사용 중심으로 정리한다.

## 현재 상태

- [PR #13](https://github.com/plcmanjp/excel-cad-label-maker/pull/13)은 main에 병합됐으며 Issue #12는 CLOSED다. pandas 제거와 직접 읽기 및 TXT 출력과 고지 충돌 거부를 구현하고 최종 빌드 및 압축 해제 앱 QC를 완료했다.
- 앱 구현은 project/src, 원본은 project/original, 제품과 빌드 보호 검사는 project/tests에서 관리한다. 문서는 wiki, 배포 자료는 release에 있으며 .venv와 .local은 루트에 유지한다.
- [PR #16](https://github.com/plcmanjp/excel-cad-label-maker/pull/16)은 main에 병합됐고 v0.2.1은 최신 정식 공개 버전이다. 원격 tag와 latest 및 공개 ZIP과 체크섬 재다운로드를 검증했다. 기존 v0.1.0과 v0.2.0은 보존했다.
- fix/issue-17-centered-notice-and-docs에서 중앙 배치와 문서 정리를 구현했다. 사용자 문서의 내부 운영 문구를 검사하는 예방 검증을 추가했다. 0.2.2 버전의 검수와 최종 빌드 및 실제 알림 배치 확인이 남아 있다.

## 주요 결정

- Issue #2는 복구 소스와 재현 가능한 빌드 완료로 CLOSED다. 실제 CAD, 별도 PC와 원본 대응 및 이용 조건은 [후속 Issue #14](https://github.com/plcmanjp/excel-cad-label-maker/issues/14)에서 OPEN 및 미검증을 유지한다.
- 원본과 외부 고지의 byte를 보존한다. 빌드 출력의 Markdown 고지는 내용 변경 없이 .txt 이름으로 제공하고 출력 provenance를 맞춘다.
- numpy는 ezdxf의 필수 의존성이므로 유지한다. pandas 제거는 기존 읽기 결과와 날짜, bool, 오류 및 수식 캐시 대조를 통과해 채택했다.
- CURRENT 한글 전송 손상을 UTF-8 파일 편집으로 복구했다. 실제 CURRENT 구조를 기존 hook 파서로 확인하는 예방 검증을 추가한다.
- README와 사용 및 배포 안내 및 릴리스 노트는 앱 사용에 필요한 정보만 제공한다. 개발 안내는 기여자의 재현 가능한 절차로 정리하고 운영 문서와 이미지 생성 프롬프트는 .agents/docs에서 관리한다. 기존 journal과 QC 증거는 보존한다.

## 검증 결과

- CI77개와 독립 검수 및 최종 ZIP 실제 앱의 드롭과 DXF 저장이 PASS다. 공개0.2.0 앱의 시작에서 0.2.1 자동 알림을 확인했고 최신 앱의 수동 조회도 정상이다. 정확한 빌드 commit과 hash 및 공개 readback은 [릴리스 QC](../../release/qc/release-v0.2.1.json)에 있다.
- 새 중앙 배치의 실제 Tk 부모 이동 및 크기 변경 회귀와 제품40개 및 사용자 문서와 저장소 검사 PASS다. 기존 업데이트 지연 및 중복 방지 검사가 유지된다.
- frozen 업데이트 QC 앱에서 두 위치와 크기의 실제 알림 중심을 확인했다. 각 수평 오차0.5px, 수직 오차0px이며 나중에 동작 및 실제 GitHub API 조회가 PASS다. 독립 source 누적 검수가 PASS다.

## 미해결 사항

- 실제 CAD, 별도 PC와 원본의 세부 이용 조건은 Issue #14의 미검증 범위다. DWG 직접 출력은 미지원이다.
- 최종 ZIP의 실행과 드롭/저장 및 artifact 검수와 CI, 0.2.2 공개 및 기존 릴리스 설명의 정리가 남아 있다.

## 다음 작업

1. 중앙 배치와 문서 경계의 독립 검수 및 CI를 확인한다.
2. frozen 알림 및 최종 ZIP의 실제 동작을 확인해 0.2.2를 공개한다.
3. 기존 릴리스 설명을 사용자 중심으로 맞추고 자산 hash 및 공개 후 결과를 확인한다.
