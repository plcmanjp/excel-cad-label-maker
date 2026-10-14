param([switch]$CheckOnly, [switch]$Release)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$appName = if ($Release) { 'Excel_CAD_Label' } else { 'Excel_CAD_Label_Dev' }
$receiptType = if ($Release) { 'release-build' } else { 'development-build' }
Push-Location -LiteralPath $repoRoot
try {
    $buildRoots = @()
    foreach ($generatedRoot in @('project', 'project/dist', 'project/build', 'release', 'release/artifacts')) {
        $candidate = Join-Path $repoRoot $generatedRoot
        if (Test-Path -LiteralPath $candidate) {
            # Validate every root before traversal; normal OneDrive cloud reparse is allowed.
            if ((Get-Item -LiteralPath $candidate -Force).LinkType) { throw 'Linked build roots are not supported.' }
            $buildRoots += $candidate
        }
    }
    foreach ($candidate in $buildRoots) {
        if (@(Get-ChildItem -LiteralPath $candidate -Recurse -Force | Where-Object { $_.LinkType }).Count -ne 0) {
            throw 'Linked paths in build directories are not supported.'
        }
    }
    $distRoot = if ($Release) { 'release/artifacts' } else { 'project/dist' }
    $devOutput = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "$distRoot/$appName"))
    if (-not $devOutput.StartsWith($repoRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Build output must stay within the repository.'
    }
    $runningApps = @(Get-Process $appName -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -and $_.Path.StartsWith($devOutput + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
    })
    if ($runningApps.Count -gt 0) { throw 'Close this build app before rebuilding.' }
    if (Test-Path -LiteralPath $devOutput) {
        $generatedEntries = @(Get-Item -LiteralPath $devOutput -Force) + @(Get-ChildItem -LiteralPath $devOutput -Recurse -Force)
        if (@($generatedEntries | Where-Object { $_.LinkType }).Count -ne 0) {
            throw 'Linked paths in the build output are not supported.'
        }
    }
    if ($CheckOnly) { Write-Output 'PASS: build path and process guards'; return }
    # OneDrive may mark generated directories read-only. PyInstaller cannot remove them.
    foreach ($entry in $generatedEntries) {
        if ($entry.Attributes -band [System.IO.FileAttributes]::ReadOnly) {
            $entry.Attributes = $entry.Attributes -band (-bnot [System.IO.FileAttributes]::ReadOnly)
        }
    }
    & .venv/Scripts/python.exe -B -m unittest discover -s project/tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Product tests failed.' }
    $iconPath = Join-Path $repoRoot 'project/src/assets/app-icon.ico'
    & .venv/Scripts/python.exe -m PyInstaller --noconfirm --windowed --onedir --noupx `
        --icon $iconPath --add-data "$iconPath;assets" `
        --name $appName --collect-all tkinterdnd2 --hidden-import openpyxl `
        --hidden-import xlrd --specpath project/build --distpath $distRoot --workpath project/build/pyinstaller `
        project/src/excel_cad_label.py
    if ($LASTEXITCODE -ne 0) { throw 'Windows build failed.' }
    Copy-Item -LiteralPath release/third_party -Destination "$devOutput/third_party" -Recurse -Force
    Copy-Item -LiteralPath wiki/reference/third-party.md -Destination "$devOutput/third_party/README.md" -Force
    Copy-Item -LiteralPath release/package/NOTICE.md,release/package/CREDITS.md -Destination $devOutput -Force
    if ($Release) {
        $releaseConfig = Get-Content -LiteralPath release/app-release.json -Raw -Encoding UTF8 | ConvertFrom-Json
        Copy-Item -LiteralPath release/package/README-Windows.md -Destination "$devOutput/README.md" -Force
        [System.IO.File]::WriteAllText((Join-Path $devOutput 'VERSION'), ($releaseConfig.version + "`n"), [System.Text.UTF8Encoding]::new($false))
    }
    & .venv/Scripts/python.exe -B project/scripts/check-app-icon.py --output $devOutput --exe-name "$appName.exe"
    if ($LASTEXITCODE -ne 0) { throw 'Packaged app icon verification failed.' }
    & .venv/Scripts/python.exe -B release/scripts/build-receipt.py --output $devOutput --exe-name "$appName.exe" --build-type $receiptType
    if ($LASTEXITCODE -ne 0) { throw 'Build receipt failed.' }
} finally { Pop-Location }
