$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
& "$repoRoot/.venv/Scripts/python.exe" -B "$repoRoot/Project/P001-excel-cad-label/src/excel_cad_label.py"
exit $LASTEXITCODE
