$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Push-Location -LiteralPath $repoRoot
try {
    foreach ($ancestor in @('.local', '.local/update-qc', '.local/update-qc/builds')) {
        $path = Join-Path $repoRoot $ancestor
        if ((Test-Path -LiteralPath $path) -and (Get-Item -LiteralPath $path -Force).LinkType) {
            throw 'Linked QC output roots are not supported.'
        }
    }
    $runRoot = Join-Path $repoRoot ('.local/update-qc/builds/' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $runRoot | Out-Null
    $iconPath = Join-Path $repoRoot 'project/src/assets/app-icon.ico'
    & .venv/Scripts/python.exe -m PyInstaller --windowed --onedir --noupx `
        --icon $iconPath --add-data "$iconPath;assets" `
        --name Update_Notice_QC --paths project/src --collect-all tkinterdnd2 `
        --hidden-import openpyxl --hidden-import xlrd --specpath $runRoot `
        --distpath "$runRoot/dist" --workpath "$runRoot/work" project/qc/update-notice-gui.py
    if ($LASTEXITCODE -ne 0) { throw 'QC Windows build failed.' }
    $output = Join-Path $runRoot 'dist/Update_Notice_QC'
    Copy-Item -LiteralPath release/third_party -Destination "$output/third_party" -Recurse
    Copy-Item -LiteralPath wiki/reference/third-party.md -Destination "$output/third_party/README.md"
    Copy-Item -LiteralPath release/package/NOTICE.md,release/package/CREDITS.md -Destination $output
    & .venv/Scripts/python.exe -B project/scripts/check-app-icon.py --output $output --exe-name Update_Notice_QC.exe
    if ($LASTEXITCODE -ne 0) { throw 'Packaged QC icon verification failed.' }
    & .venv/Scripts/python.exe -B release/scripts/build-receipt.py --output $output --exe-name Update_Notice_QC.exe --build-type update-qc-build
    if ($LASTEXITCODE -ne 0) { throw 'QC build receipt failed.' }
    $pointer = @{ output = $output.Substring($repoRoot.Length + 1).Replace('\', '/'); executable = 'Update_Notice_QC.exe' }
    [System.IO.File]::WriteAllText((Join-Path $repoRoot '.local/update-qc/latest-build.json'), ($pointer | ConvertTo-Json), [System.Text.UTF8Encoding]::new($false))
    Write-Output 'PASS: separate update QC build; pointer .local/update-qc/latest-build.json'
} finally { Pop-Location }
