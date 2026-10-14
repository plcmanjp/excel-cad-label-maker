param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $repoRoot
try {
    foreach ($generatedRoot in @('dist', 'build')) {
        $candidate = Join-Path $repoRoot $generatedRoot
        if (Test-Path -LiteralPath $candidate) {
            # Check ancestors before traversing, preserving normal OneDrive cloud reparse.
            if ((Get-Item -LiteralPath $candidate -Force).LinkType) { throw 'Linked build roots are not supported.' }
            if (@(Get-ChildItem -LiteralPath $candidate -Recurse -Force | Where-Object { $_.LinkType }).Count -ne 0) {
                throw 'Linked paths in build directories are not supported.'
            }
        }
    }
    $devOutput = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'dist/Excel_CAD_Label_Dev'))
    if (-not $devOutput.StartsWith($repoRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Build output must stay within the repository.'
    }
    $runningApps = @(Get-Process Excel_CAD_Label_Dev -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -and $_.Path.StartsWith($devOutput + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
    })
    if ($runningApps.Count -gt 0) { throw 'Close the development app before rebuilding.' }
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
    & .venv/Scripts/python.exe -B -m unittest discover -s Project/P001-excel-cad-label/tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Product tests failed.' }
    & .venv/Scripts/python.exe -m PyInstaller --noconfirm --windowed --onedir --noupx `
        --name Excel_CAD_Label_Dev --collect-all tkinterdnd2 --hidden-import openpyxl `
        --hidden-import xlrd --specpath build --distpath dist --workpath build/pyinstaller `
        Project/P001-excel-cad-label/src/excel_cad_label.py
    if ($LASTEXITCODE -ne 0) { throw 'Windows build failed.' }
    Copy-Item -LiteralPath third_party -Destination dist/Excel_CAD_Label_Dev/third_party -Recurse -Force
    Copy-Item -LiteralPath NOTICE.md,CREDITS.md -Destination dist/Excel_CAD_Label_Dev -Force
    & .venv/Scripts/python.exe -B scripts/build-receipt.py
    if ($LASTEXITCODE -ne 0) { throw 'Build receipt failed.' }
} finally { Pop-Location }
