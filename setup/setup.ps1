<#
.SYNOPSIS
  Installs the tools this workspace uses, then opens Claude to finish setup. Safe to run again.
.EXAMPLE
  powershell -ExecutionPolicy Bypass -File setup\setup.ps1
  powershell -ExecutionPolicy Bypass -File setup\setup.ps1 -DryRun
#>
param(
    [switch]$DryRun,
    [switch]$Validate,
    [string]$Only,
    [switch]$Yes,
    [switch]$NoLaunch
)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # the 5.1 progress bar makes big downloads crawl
$root = Split-Path -Parent $PSScriptRoot
Get-ChildItem -Path (Join-Path $PSScriptRoot 'lib') -Filter '*.ps1' | ForEach-Object { . $_.FullName }

$tools = @(Read-ToolList -Path (Join-Path $PSScriptRoot 'tools.json'))
$errors = @(Test-ToolList -Tools $tools)
if ($errors.Count -gt 0) { $errors | ForEach-Object { Write-Host "tools.json: $_" -ForegroundColor Red }; exit 1 }
if ($Validate) { Write-Host "tools.json is valid: $($tools.Count) tools."; exit 0 }

Write-Host ''
Write-Host 'This sets up your workspace. It installs the tools Claude uses, then opens Claude.'
Write-Host 'It takes 15 to 30 minutes. It downloads about 500 MB. It signs in to nothing.'
Write-Host 'If a tool fails, it is written down and setup keeps going. Claude will help with it after.'
Write-Host ''

$stop = Test-Preflight
if ($stop) { Write-Host $stop -ForegroundColor Red; exit 4 }

Update-SessionPath
$selected = @(Select-Tools -Tools $tools -Only $Only)
$plan = @(Invoke-ToolRun -Tools $selected -Root $root -DryRun)
foreach ($r in $plan) {
    $label = @{ present = 'already installed'; planned = 'will install'; manual = 'you do this'; skipped = 'skipped' }[$r.Status]
    Write-Host ('  {0,-18} {1}' -f $label, $r.Name)
}
$reportPath = Join-Path $PSScriptRoot 'setup-report.md'
if ($DryRun) {
    Write-SetupReport -Results $plan -Path $reportPath -DryRun
    Write-Host "`nDry run. Nothing installed. Report: $reportPath"; exit 0
}
if (-not $Yes) {
    $answer = Read-Host "`nInstall the tools marked 'will install'? (Y/n)"
    if ($answer -and $answer -notmatch '^(y|yes)$') { Write-Host 'Cancelled. Nothing installed.'; exit 3 }
}
$results = @(Invoke-ToolRun -Tools $selected -Root $root)
Write-SetupReport -Results $results -Path $reportPath
$failed = @($results | Where-Object { $_.Status -eq 'failed' }).Count
Write-Host "`nDone. $failed failed. Report: $reportPath"

Update-SessionPath
if ($NoLaunch -or -not (Test-Command claude)) {
    Write-Host 'Open this folder in Claude Code and type: set this up'
    if ($failed -gt 0) { exit 2 } else { exit 0 }
}
Write-Host 'Opening Claude. Sign in if your browser asks, then answer its questions.'
Push-Location -LiteralPath $root
try { & claude 'set this up' } finally { Pop-Location }
exit 0
