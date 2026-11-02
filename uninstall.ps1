param([string]$HomeDirectory = $env:USERPROFILE)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding
& python (Join-Path $PSScriptRoot 'scripts/plugin_manager.py') uninstall --home $HomeDirectory
if ($LASTEXITCODE -ne 0) { throw 'Uninstall stopped to preserve modified configuration.' }
Write-Host 'Plugin source and registration removed. Restart Codex. Game workspaces were preserved.'
