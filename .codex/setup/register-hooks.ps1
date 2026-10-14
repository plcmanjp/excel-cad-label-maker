[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$hookPath = Join-Path $repoRoot '.agents/hooks/session_start_status.py'
if (-not (Test-Path -LiteralPath $hookPath -PathType Leaf)) { throw 'Hook source missing' }
$commandText = 'python -B "' + $hookPath + '"'
$registration = @{ hooks = @{ SessionStart = @(@{ matcher = 'startup|resume'; hooks = @(@{ type = 'command'; command = $commandText; commandWindows = $commandText; statusMessage = 'inject work journal (CURRENT.md)'; timeout = 30 }) }) } }
$jsonText = ($registration | ConvertTo-Json -Depth 8) + [Environment]::NewLine
[System.IO.File]::WriteAllText((Join-Path $repoRoot '.codex/hooks.json'), $jsonText, [System.Text.UTF8Encoding]::new($false))
Write-Output 'Local absolute SessionStart registration written. Runtime trust and hook approval remain unverified.'
