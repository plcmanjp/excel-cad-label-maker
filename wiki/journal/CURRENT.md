# 작업 저널 (CURRENT)

## 목표

- PR #23의 main 병합과 0.4.0 정식 배포, 완료 이슈와 병합 브랜치 정리를 마친다.

## 현재 상태

- [PR #23](https://github.com/plcmanjp/excel-cad-label-maker/pull/23)은 main의 156b4b9로 병합됐고 Issue #22는 CLOSED다. [0.4.0](https://github.com/plcmanjp/excel-cad-label-maker/releases/tag/v0.4.0)을 정식 latest로 공개하고 두 자산을 다시 내려받아 바이트 동일성을 확인했다.
- 원격과 OneDrive 밖 독립 빌드 checkout은 main만 남겼다. 병합 이력과 reflog 도달 가능성을 확인하고 검증된 Git bundle 및 refs 기록을 Git 제외 로컬 증거 폴더에 보존했다.
- 원래 OneDrive 작업 폴더는 Git index 읽기 오류가 있어 로컬 ref와 index, HEAD 및 worktree 자료를 보존했다. 이 폴더의 동기화와 전체 로컬 브랜치 정리는 완료로 판정하지 않는다.

## 주요 결정

- 1행=1라벨, 열=줄, 중간 빈 셀 보존과 기존 열 입력/설정 호환 계약을 0.4.0으로 배포했다. 안내 영역 오른쪽 여백 수정도 포함한다.
- 정식 배포물은 clean main 156b4b9에서 빌드했다. 이후 QC/진행 기록 커밋은 배포 tag를 이동하거나 기존 자산을 덮어쓰지 않는다.

## 검증 결과

- [배포 QC](../../../project/qc/release040-results.json): 제품 128개, 병합 main CI, ZIP 1,129멤버와 해시 및 독립 패키지 검수 PASS. 압축 해제 EXE에서 Excel 파일 선택, 3라벨/8칸의 중간 빈 줄, DXF 저장/재읽기와 원본 불변 및 안내 여백을 확인했다.
- 공개 자산 byte readback과 실제 이전 공개 0.3.0 EXE의 최신 0.4.0 알림 PASS. 기존 [Excel 기능 QC](../../../project/qc/issue22-results.json)와 [화면 배율 QC](../../../project/qc/issue22-ui-results.json)는 별도 근거다.

## 미해결 사항

- 정식 ZIP의 실제 Explorer 간 드래그는 도구가 다른 창으로 향하는 입력을 차단해 미검증이다. 파일 선택 경로는 통과했으며 드롭 PASS로 확대하지 않는다.
- Issue #20의 초보 사용자와 실제 OS 배율, Issue #14의 실제 CAD/별도 PC/원본 대응/이용 조건은 OPEN이다. 기존 청소 차단 상태도 유지한다.
- 원래 OneDrive 저장소의 index 접근 복구와 그 후 로컬 브랜치 정리가 필요하다. 임의 index 재생성이나 worktree 제거를 하지 않는다.

## 다음 작업

1. 실제 사용자 환경에서 Explorer 드롭과 Issue #20의 남은 사용자/OS 배율 검증을 수행한다.
2. Issue #14의 CAD와 별도 Windows PC 및 권리 조건을 실제 근거로 확인한다.
3. 원래 OneDrive index가 정상적으로 읽힌 뒤 보존 자료를 확인하고 로컬 Git 동기화와 브랜치 정리를 재개한다.
