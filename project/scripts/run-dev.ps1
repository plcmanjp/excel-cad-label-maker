$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
& "$repoRoot/.venv/Scripts/python.exe" -B "$repoRoot/project/src/excel_cad_label.py"
exit $LASTEXITCODE
