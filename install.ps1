param([string]$HomeDirectory = $env:USERPROFILE, [switch]$NoOpen)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding
$studioScript = Join-Path $PSScriptRoot 'scripts/plugin_manager.py'
if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'plugin.json')) -and
    -not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'plugins/codex-game-studios/plugin.json'))) {
    & python (Join-Path $PSScriptRoot 'scripts/build_plugin.py')
    if ($LASTEXITCODE -ne 0) { throw 'Plugin build failed.' }
}
$studioOutput = & python $studioScript install --home $HomeDirectory
if ($LASTEXITCODE -ne 0) { throw ($studioOutput -join "`n") }
$studioResult = ($studioOutput -join "`n") | ConvertFrom-Json
$studioResult | Format-List
if (-not $NoOpen -and $studioResult.open) { Start-Process $studioResult.open -WindowStyle Hidden }
Write-Host 'Restart Codex, review the plugin and trust its hooks. Run $studio-setup in your game workspace.'
