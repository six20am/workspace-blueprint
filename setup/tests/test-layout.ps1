$dir = Join-Path ([IO.Path]::GetTempPath()) ('layout ' + [guid]::NewGuid())
New-Item -ItemType Directory -Path "$dir\setup" -Force | Out-Null
New-Item -ItemType Directory -Path "$dir\tools\update" -Force | Out-Null
[IO.File]::WriteAllText("$dir\tools\update\update.py", '# updater')
Assert-True (-not (Test-LayoutUnfinished -Root $dir)) 'no version.json: nothing to finish'
# the old updater stamped the remote commit and no layout
[IO.File]::WriteAllText("$dir\setup\version.json", '{"commit": "abc", "date": "2026-10-31", "updated": "2026-10-31"}')
Assert-True (Test-LayoutUnfinished -Root $dir) 'version.json without layout is unfinished'
$script:LayoutCalls = @()
$ran = Invoke-LayoutFinish -Root $dir -Run { param($u) $script:LayoutCalls += $u } 6>$null
Assert-True $ran 'the layout check is reached and runs the updater'
Assert-Equal $script:LayoutCalls.Count 1 'the updater runs once'
Assert-True ($script:LayoutCalls[0] -like '*tools\update\update.py') 'the new updater in tools is the one run'
[IO.File]::WriteAllText("$dir\setup\version.json", '{"commit": "abc", "layout": 2}')
$script:LayoutCalls = @()
Assert-True (-not (Invoke-LayoutFinish -Root $dir -Run { param($u) $script:LayoutCalls += $u } 6>$null)) 'layout 2 skips the move'
Assert-Equal $script:LayoutCalls.Count 0 'nothing runs on layout 2'
Remove-Item -LiteralPath "$dir\tools\update\update.py"
[IO.File]::WriteAllText("$dir\setup\version.json", '{"commit": "abc"}')
Assert-True (-not (Test-LayoutUnfinished -Root $dir)) 'no updater in tools: nothing to run'
$setupText = Get-Content -LiteralPath (Join-Path $script:SetupRoot 'setup.ps1') -Raw
Assert-True ($setupText.IndexOf('Invoke-LayoutFinish') -ge 0 -and $setupText.IndexOf('Invoke-LayoutFinish') -lt $setupText.IndexOf('Read-ToolList')) 'setup.ps1 finishes the layout before reading the tool list'
Remove-Item -Recurse -Force $dir
