# Writes setup/setup-report.md. Claude reads this file on first open (see CLAUDE.md).
function Write-SetupReport([object[]]$Results, [string]$Path, [switch]$DryRun) {
    $lines = New-Object System.Collections.Generic.List[string]
    $title = 'Setup report'; if ($DryRun) { $title = 'Setup report (dry run, nothing installed)' }
    $lines.Add("# $title"); $lines.Add(''); $lines.Add("Run: $(Get-Date -Format 'yyyy-MM-dd HH:mm') on $env:COMPUTERNAME"); $lines.Add('')

    $attention = @($Results | Where-Object { $_.Status -eq 'failed' }) + @($Results | Where-Object { $_.Status -eq 'skipped' }) + @($Results | Where-Object { $_.Status -eq 'manual' })
    if ($attention.Count -gt 0) {
        $lines.Add('## Needs attention'); $lines.Add('')
        foreach ($r in $attention) {
            $why = $r.Detail; if (-not $why) { $why = $r.Login }
            $lines.Add("- **$($r.Name)** ($($r.Status)): $why")
        }
        $lines.Add('')
    }
    $logins = @($Results | Where-Object { $_.Login })
    if ($logins.Count -gt 0) {
        $lines.Add('## Sign in yourself'); $lines.Add('')
        foreach ($r in $logins) { $lines.Add("- **$($r.Name)**: $($r.Login)") }
        $lines.Add('')
    }
    $sections = @(@('Installed now', 'installed'), @('Already present', 'present'))
    if ($DryRun) { $sections += , @('Would install', 'planned') }
    foreach ($s in $sections) {
        $rows = @($Results | Where-Object { $_.Status -eq $s[1] })
        if ($rows.Count -eq 0) { continue }
        $lines.Add("## $($s[0])"); $lines.Add('')
        foreach ($r in $rows) { $lines.Add("- $($r.Name) ($($r.Area))") }
        $lines.Add('')
    }
    [IO.File]::WriteAllText($Path, ($lines -join "`r`n"), (New-Object System.Text.UTF8Encoding $false))
}
