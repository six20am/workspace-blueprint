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
    foreach ($cmd in @($t.install) + @($t.install_mac)) {
        Assert-True ($cmd -notmatch 'mtesi|C:\\Users\\|/c/Users/') "$($t.id): no personal path in install commands"
    }
}
