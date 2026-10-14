# Git Sync

## 원격과 추적 범위

- 저장소: https://github.com/plcmanjp/excel-cad-label-maker (public)
- remote: origin / branch: main
- 포함: 제품 소스, 공개 문서, 하네스, 검증 스크립트와 GitHub Actions.
- 제외: EXE, ZIP, dist/, build/, .local/, 로컬 절대 경로 설정, 비밀과 고객 자료.

## 승인 분류

검토와 승인 불명에서는 git --no-optional-locks로 로컬 상태만 관찰합니다. fetch, pull, ref 갱신, 기록과 마무리 변경을 하지 않습니다. 승인된 실행 범위에서만 fetch 후 상태와 upstream을 확인하고 필요하면 pull --ff-only를 사용합니다. 예상 밖 변경이 있으면 보존하고 의존하는 편집 전 사용자에게 확인합니다.

## 완료 계약

큰 작업 단위를 검증한 뒤 경로를 지정해 stage하고 한국어 메시지로 commit 및 일반 push합니다. 다른 세션의 변경을 포함하지 않습니다. 관리형 부모 환경에서는 commit 직전에 부모 setup-git-env.ps1 -Mode Verify -RepositoryPath <repo>를 통과시킵니다. author와 committer는 검증된 plcmanjp 귀속을 사용하며 이메일을 문서나 일반 출력에 기록하지 않습니다.

UTF-8 파일을 git commit -F <파일>에 전달하고 git log -1 --format=%s로 확인합니다. force push, remote 변경과 공개 릴리스는 사용자 승인 대상입니다. 이미 승인된 해당 버전의 공개 작업은 같은 범위에서 재승인을 요구하지 않습니다.
