$results = @(
    [pscustomobject]@{ Id = 'git'; Name = 'Git'; Area = 'base'; Status = 'present'; Detail = ''; Login = $null },
    [pscustomobject]@{ Id = 'node'; Name = 'Node.js'; Area = 'base'; Status = 'installed'; Detail = ''; Login = $null },
    [pscustomobject]@{ Id = 'py'; Name = 'Python'; Area = 'base'; Status = 'failed'; Detail = 'exit code 1'; Login = $null },
    [pscustomobject]@{ Id = 'md'; Name = 'markitdown'; Area = 'docs'; Status = 'skipped'; Detail = 'needs py'; Login = $null },
    [pscustomobject]@{ Id = 'nb'; Name = 'NotebookLM'; Area = 'docs'; Status = 'present'; Detail = ''; Login = 'Run: notebooklm login' }
)
$path = Join-Path ([IO.Path]::GetTempPath()) ('setup report ' + [guid]::NewGuid() + '.md')
Write-SetupReport -Results $results -Path $path
$md = Get-Content $path -Raw
Assert-True ($md -match '(?s)## Needs attention.*Python.*exit code 1.*markitdown.*needs py') 'failures then skips, with reasons'
Assert-True ($md -match '(?s)## Sign in yourself.*NotebookLM.*notebooklm login') 'sign-in list includes present tools with a login'
Assert-True ($md -match '(?s)## Installed now.*Node\.js') 'installed section'
Assert-True ($md -match '(?s)## Already present.*Git') 'present section'
Assert-True ($md -notmatch 'Would install') 'no dry-run section on a real run'
Assert-True ($md -notmatch [char]0x2014) 'no em dashes'
Remove-Item $path

# Test single result object (not wrapped in array)
$singleResult = [pscustomobject]@{ Id = 'test'; Name = 'Test Tool'; Area = 'base'; Status = 'installed'; Detail = ''; Login = $null }
$path = Join-Path ([IO.Path]::GetTempPath()) ('setup report ' + [guid]::NewGuid() + '.md')
Write-SetupReport -Results $singleResult -Path $path
$md = Get-Content $path -Raw
Assert-True ($md -match '## Installed now') 'single-result: installed section appears'
Assert-True ($md -match 'Test Tool') 'single-result: tool name appears'
Remove-Item $path

# Test dry-run with planned status
$dryRunResults = @(
    [pscustomobject]@{ Id = 'test'; Name = 'Test Tool'; Area = 'base'; Status = 'planned'; Detail = ''; Login = $null }
)
$path = Join-Path ([IO.Path]::GetTempPath()) ('setup report ' + [guid]::NewGuid() + '.md')
Write-SetupReport -Results $dryRunResults -Path $path -DryRun
$md = Get-Content $path -Raw
Assert-True ($md -match 'Setup report \(dry run, nothing installed\)') 'dry-run: title indicates dry run'
Assert-True ($md -match '## Would install') 'dry-run: Would install section appears'
Assert-True ($md -match 'Test Tool') 'dry-run: tool name in Would install section'
Remove-Item $path

# Test $null input (caller forgot to wrap in @())
$path = Join-Path ([IO.Path]::GetTempPath()) ('setup report ' + [guid]::NewGuid() + '.md')
Write-SetupReport -Results $null -Path $path
$md = Get-Content $path -Raw
Assert-True ($md -match '# Setup report') '$null input: title appears'
Assert-True ($md -notmatch '## Needs attention') '$null input: no attention section'
Assert-True ($md -notmatch '## Installed now') '$null input: no installed section'
Remove-Item $path
