$tools = @(Read-ToolList -Path (Join-Path $script:SetupRoot 'tools.json'))
$errs = @(Test-ToolList -Tools $tools)
Assert-Equal $errs.Count 0 ("tools.json validates: " + ($errs -join '; '))
Assert-True ($tools.Count -ge 20) 'the base has at least 20 entries'
foreach ($id in 'git', 'python', 'node', 'claude', 'plugin-superpowers', 'notebooklm', 'scrapling', 'markitdown', 'whisper-model') {
    Assert-True (@($tools | Where-Object { $_.id -eq $id }).Count -eq 1) "tools.json has $id"
}
$noMac = @($tools | Where-Object { (@($_.install).Count -gt 0) -and (@($_.install_mac).Count -eq 0) })
Assert-Equal (@($noMac | ForEach-Object { $_.id }) -join ',') '' 'every tool with a Windows install also has a Mac install'
foreach ($t in $tools) {
    foreach ($cmd in @($t.install) + @($t.install_mac) + @($t.install_linux)) {
        $personal = ('mt' + 'esi') + '|C:\\' + 'Users\\|/c/' + 'Users/'   # split so the scanner does not flag the scanner
        Assert-True ($cmd -notmatch $personal) "$($t.id): no personal path in install commands"
    }
}
foreach ($id in 'imagemagick', 'exiftool', 'sox', 'handbrake', 'mkvtoolnix', 'libreoffice', 'pandoc', 'tesseract', 'poppler', 'qpdf', 'jq', 'ocrmypdf', 'rtk', 'rtk-hook', 'defuddle', 'trafilatura', 'ccusage', 'repomix', 'codeburn') {
    Assert-True (@($tools | Where-Object { $_.id -eq $id }).Count -eq 1) "tools.json has $id once"
}
$noLinux = @($tools | Where-Object { (-not $_.adapter) -and (@($_.install).Count -gt 0) -and (@($_.install_linux).Count -eq 0) })
Assert-Equal (@($noLinux | ForEach-Object { $_.id }) -join ',') '' 'every shared tool with a Windows install also has a Linux install'
$noLinuxCheck = @($tools | Where-Object { (@($_.install_linux).Count -gt 0) -and [string]::IsNullOrWhiteSpace([string]$_.check_linux) })
Assert-Equal (@($noLinuxCheck | ForEach-Object { $_.id }) -join ',') '' 'every tool with a Linux install also has a Linux check'
$badAdapter = @($tools | Where-Object { $_.adapter -and (@('claude-code', 'grok-bot') -notcontains $_.adapter) })
Assert-Equal (@($badAdapter | ForEach-Object { $_.id }) -join ',') '' 'every adapter value is claude-code or grok-bot'
foreach ($id in 'claude', 'plugin-superpowers', 'mcp-scrapling', 'chrome-extension', 'rtk-hook', 'ccusage') {
    Assert-Equal (@($tools | Where-Object { $_.id -eq $id })[0].adapter) 'claude-code' "$id is Claude Code only"
}
Assert-Equal (@($tools | Where-Object { $_.area -eq 'programs' }).Count) 19 'the programs area has nineteen entries'
