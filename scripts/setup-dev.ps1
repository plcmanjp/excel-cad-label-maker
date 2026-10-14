param([string]$PythonLauncher = 'py')
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $repoRoot
try {
    if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
        & $PythonLauncher -3.13 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Python 3.13 venv creation failed.' }
    }
    & .venv/Scripts/python.exe -c "import sys; assert sys.version_info[:3] == (3, 13, 15), 'Python 3.13.15 required'"
    if ($LASTEXITCODE -ne 0) { throw 'Unexpected Python version.' }
    & .venv/Scripts/python.exe -m pip install -r requirements-dev.lock.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
    & .venv/Scripts/python.exe -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'Dependency check failed.' }
} finally { Pop-Location }
