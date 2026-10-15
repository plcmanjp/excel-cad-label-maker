# 작업 저널 (CURRENT)

## 목표

- [Issue #26](https://github.com/plcmanjp/excel-cad-label-maker/issues/26): 소스 권리 양도에 대한 관리자 확인을 근거로 MIT를 적용하고 Arial 기본값과 함께 0.4.1을 정식 배포한다.

## 현재 상태

- 사용자는 원개발자에게 소스 권리를 양도받았다고 명시 확인했다. 이 확인을 근거로 LICENSE/NOTICE와 문서, LICENSE.txt의 원문 포함 및 누락/변조 거부 검사와 버전 0.4.1을 수정했다. 독립 읽기 전용 검수의 미해결 finding은 0개이며 최종 CI 및 정식 빌드가 남았다. 계약의 법적 효력을 독립 감정한 사실로 표현하지 않는다.
- [PR #25](https://github.com/plcmanjp/excel-cad-label-maker/pull/25)에 Arial/라이선스/0.4.1 배포를 통합한다. 기존 Arial 구현은 제품 128개와 개발 EXE 및 CI를 통과했다. 라이선스 배포 보호 18개 중 17 PASS와 로컬 symlink 권한 제한 1 SKIP, 하네스 22개와 저장소/공개 문서 검사는 PASS다.
- 공개 latest는 아직 v0.4.0이다. 원래 OneDrive checkout의 예상 밖 변경과 중복 worktree를 보존하며 독립 checkout에서 작업한다.

## 주요 결정

- 소스와 0.4.1부터 빌드한 앱은 MIT, 저작권자는 plcmanjp로 표시하고 원개발자 직장인의 크레딧을 유지한다. 보관 원본 EXE 0.1.0과 외부 구성요소는 별도 조건이다. original 및 외부 고지 bytes와 과거 자산은 유지한다.
- LICENSE.txt는 저장소 LICENSE와 byte 단위로 일치해야 한다. 정식 manifest에 MIT를 기록하며 누락/변조/충돌을 거부한다.
- 새 설정은 Arial이고 기존 마지막 설정/프리셋의 명시적 글꼴은 보존한다. 실제 사용자 CAD의 Arial 한글 확인을 다른 CAD/PC의 결과로 확대하지 않는다.

## 검증 결과

- 제품 128개 재검사와 배포 보호/고지 원문/충돌 및 독립 검수 통과. 로컬 symlink 제한은 CI와 구분한다. fresh clean main의 정식 EXE/ZIP 실제 실행과 원격 readback이 남았다.
- 기존 0.4.0 배포 근거는 project/qc/release040-results.json, Arial 개발 검증은 2026-10/r021 journal에 보존했다.

## 미해결 사항

- PR #25를 최종 CI/독립 검수 후 병합하고 fresh main 정식 빌드/ZIP의 LICENSE와 실제 DXF를 확인한 뒤 0.4.1을 공개한다.
- #14의 소스 권리 조건은 관리자 확인과 적용 범위를 갱신하되 CAD/별도 PC/원본 빌드 대응은 남긴다. #20과 원래 checkout 보존 상태도 유지한다.

## 다음 작업

1. 제품 검사와 독립 검수를 확인하고 PR #25의 범위/검증 근거를 갱신한다.
2. 최종 CI 후 main 병합과 fresh 0.4.1 빌드/ZIP 검수를 수행한다.
3. v0.4.1 latest를 공개하고 자산 재다운로드, 업데이트 알림 및 완료 이슈/브랜치 상태를 기록한다.
