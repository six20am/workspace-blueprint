# An install the old updater touched has setup/version.json without "layout": the old updater copied
# tools/ and the installers but never the skills. The new updater (already in tools/) finishes the move.
function Test-LayoutUnfinished([string]$Root) {
    $version = Join-Path $Root 'setup\version.json'
    $updater = Join-Path $Root 'tools\update\update.py'
    if (-not (Test-Path -LiteralPath $version) -or -not (Test-Path -LiteralPath $updater)) { return $false }
    $text = Get-Content -LiteralPath $version -Raw -Encoding UTF8
    return ($text -notmatch '"layout"')
}

# Runs the new updater once with --no-install. $Run is injectable so tests never start Python.
function Invoke-LayoutFinish([string]$Root, [scriptblock]$Run) {
    if (-not (Test-LayoutUnfinished -Root $Root)) { return $false }
    Write-Host 'Finishing the move to the new layout...'
    if (-not $Run) {
        $Run = {
            param($Updater)
            $py = if (Get-Command python -ErrorAction SilentlyContinue) { 'python' } elseif (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { $null }
            if (-not $py) { Write-Host 'Python is not installed yet, so the move to the new layout waits for the next run.' -ForegroundColor Yellow; return }
            & $py $Updater --no-install | Out-Host
        }
    }
    try { & $Run (Join-Path $Root 'tools\update\update.py') }
    catch { Write-Host "The move to the new layout did not finish: $($_.Exception.Message). Setup keeps going." -ForegroundColor Yellow }
    return $true
}
