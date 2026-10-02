# Runs every test-*.ps1 in this folder. Exit code 0 when all pass.
$ErrorActionPreference = 'Stop'
$script:SetupRoot = Split-Path -Parent $PSScriptRoot
$script:Failures = 0
$script:Passes = 0

function Assert-Equal($Actual, $Expected, [string]$Message) {
    if ("$Actual" -ceq "$Expected") { $script:Passes++ }
    else { $script:Failures++; Write-Host "FAIL: $Message`n  expected: $Expected`n  actual:   $Actual" -ForegroundColor Red }
}
function Assert-True($Value, [string]$Message) {
    if ($Value) { $script:Passes++ } else { $script:Failures++; Write-Host "FAIL: $Message" -ForegroundColor Red }
}

Get-ChildItem -Path (Join-Path $script:SetupRoot 'lib') -Filter '*.ps1' | ForEach-Object { . $_.FullName }
Get-ChildItem -Path $PSScriptRoot -Filter 'test-*.ps1' | Sort-Object Name | ForEach-Object {
    Write-Host "== $($_.Name)"
    . $_.FullName
}
Write-Host "$script:Passes passed, $script:Failures failed (PowerShell $($PSVersionTable.PSVersion))"
if ($script:Failures -gt 0) { exit 1 } else { exit 0 }
