function New-RunTool([string]$Id, [string[]]$Needs = @(), [string[]]$Install = @('ok'), [string]$Login = $null) {
    [pscustomobject]@{ id = $Id; name = $Id; area = 'video'; needs = $Needs; check = "check:$Id"; install = $Install; login = $Login }
}
$root = Join-Path ([IO.Path]::GetTempPath()) ('setup run ' + [guid]::NewGuid())   # a path with a space
New-Item -ItemType Directory -Path $root | Out-Null

# fake machine: which checks pass, which commands fail
$script:installed = @{ 'check:git' = $true }
$script:ran = New-Object System.Collections.Generic.List[string]
$checker = { param($expr, $r) [bool]$script:installed[$expr] }
$executor = {
    param($cmd, $r)
    $script:ran.Add("$cmd@$r")
    if ($cmd -eq 'boom') { throw 'exit code 1' }
    if ($cmd -like 'mark:*') { $script:installed['check:' + $cmd.Substring(5)] = $true }
}

$tools = @(
    (New-RunTool 'git'),
    (New-RunTool 'node' @() @('mark:node')),
    (New-RunTool 'python' @() @('boom')),
    (New-RunTool 'markitdown' @('python') @('mark:markitdown')),
    (New-RunTool 'claude' @() @() 'Install Claude Code first'),
    (New-RunTool 'half' @() @('ok'))
)
$res = @(Invoke-ToolRun -Tools $tools -Root $root -Executor $executor -Checker $checker 6>$null)
$status = @{}; foreach ($r in $res) { $status[$r.Id] = $r }

Assert-Equal $status['git'].Status 'present' 'passing check means present, nothing runs'
Assert-Equal $status['node'].Status 'installed' 'install then re-check passes'
Assert-Equal $status['python'].Status 'failed' 'throwing command fails'
Assert-True ($status['python'].Detail -match 'exit code 1') 'failure keeps the error text'
Assert-Equal $status['markitdown'].Status 'skipped' 'needs a failed tool, so skipped'
Assert-True ($status['markitdown'].Detail -match 'python') 'skip names the missing need'
Assert-Equal $status['claude'].Status 'manual' 'no install steps means manual'
Assert-Equal $status['claude'].Login 'Install Claude Code first' 'manual keeps its note'
Assert-Equal $status['half'].Status 'failed' 'install ran but check still fails'
Assert-True ($status['half'].Detail -match 'check still fails') 'post-check failure explained'
Assert-True ($script:ran -contains "mark:node@$root") 'commands run from the root, spaces intact'
Assert-True (-not ($script:ran -like 'git*')) 'present tools run nothing'

# dry run runs checks but no commands
$script:ran.Clear()
$dry = @(Invoke-ToolRun -Tools @((New-RunTool 'ffmpeg' @() @('mark:ffmpeg'))) -Root $root -DryRun -Executor $executor -Checker $checker)
Assert-Equal $dry[0].Status 'planned' 'dry run marks missing tools as planned'
Assert-Equal $script:ran.Count 0 'dry run executes nothing'

# winget lookup falls back to WindowsApps when not on PATH
$w = Get-WingetPath
if ($w) { Assert-True (Test-Path $w) 'winget path exists when found' } else { Assert-True $true 'winget absent is allowed (returns null)' }

# default executor and checker (safe: no installs)
function Test-FakeAlreadyInstalled { cmd /c exit 1; $global:LASTEXITCODE = 0 }
$threw = $false
try { & $script:DefaultExecutor 'Test-FakeAlreadyInstalled' $root } catch { $threw = $true }
Assert-True (-not $threw) 'default executor accepts a command that resets the exit code'

$script:seenDir = $null
& $script:DefaultExecutor '$script:seenDir = (Get-Location).Path' $root
Assert-Equal ([IO.Path]::GetFullPath($script:seenDir).TrimEnd('')) ([IO.Path]::GetFullPath($root).TrimEnd('')) 'default executor runs inside the spaced root'

$msg = ''
try { & $script:DefaultExecutor 'cmd /c exit 3' $root } catch { $msg = $_.Exception.Message }
Assert-True ($msg -match 'exit code 3') 'default executor throws on a nonzero exit code'

Assert-True ((& $script:DefaultChecker '$true' $root) -eq $true) 'default checker returns true for a true expression'
Assert-True ((& $script:DefaultChecker 'throw "nope"' $root) -eq $false) 'default checker returns false when the expression throws'


# Update-SessionPath leaves a usable PATH (no empty segments), python or not
Update-SessionPath
Assert-True (-not [string]::IsNullOrEmpty($env:Path)) 'PATH is non-empty after Update-SessionPath'
Assert-True (@($env:Path -split ';' | Where-Object { $_ -eq '' }).Count -eq 0) 'PATH has no empty segments'
$segs = @($env:Path -split ';')
Assert-Equal $segs.Count (@($segs | Select-Object -Unique).Count) 'PATH has no duplicate segments after Update-SessionPath'

# noisy executor output never pollutes the results
$noisy = { param($cmd, $r) Write-Output 'NOISE'; 'more noise' }
$nres = @(Invoke-ToolRun -Tools @((New-RunTool 'a' @() @('x')), (New-RunTool 'b' @() @('y'))) -Root $root -Executor $noisy -Checker { param($e, $r) $false } 6>$null)
Assert-Equal $nres.Count 2 'executor output adds nothing to the results'
Assert-True (@($nres | Where-Object { $_.PSObject.Properties.Name -contains 'Status' }).Count -eq 2) 'every result has a Status'

# 5.1: native stderr must not become a terminating error under Stop
$ErrorActionPreference = 'Stop'
Assert-True ((& $script:DefaultChecker '$(cmd /c "echo warn 1>&2 & echo ok") -match ''ok''' $root 2>$null) -eq $true) 'checker survives native stderr'
$threw = $false
try { & $script:DefaultExecutor 'cmd /c "echo warn 1>&2"' $root 2>$null } catch { $threw = $true }
Assert-True (-not $threw) 'executor survives native stderr with exit 0'
$msg4 = ''
try { & $script:DefaultExecutor 'cmd /c "echo warn 1>&2 & exit 4"' $root 2>$null } catch { $msg4 = $_.Exception.Message }
Assert-True ($msg4 -match 'exit code 4') 'executor still throws on exit 4 after stderr'

# a failed download must never be promoted to its final name
$dl = "$root\x.part"; $fin = "$root\x.bin"
$iwr = "Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 -Uri 'http://127.0.0.1:9/nothing' -OutFile `"$dl`""
$mv = "Move-Item -Force `"$dl`" `"$fin`""
$threw = $false
try { & $script:DefaultExecutor "$iwr -ErrorAction Stop; $mv -ErrorAction Stop" $root 2>$null } catch { $threw = $true }
Assert-True $threw 'a refused download with -ErrorAction Stop throws'
Assert-True (-not (Test-Path -LiteralPath $fin)) 'no final file after a refused download (Stop)'
$threw = $false
try { & $script:DefaultExecutor "$iwr; $mv" $root 2>$null } catch { $threw = $true }
Assert-True $threw 'a refused download without -ErrorAction Stop still throws'
Assert-True (-not (Test-Path -LiteralPath $fin)) 'no final file after a refused download (Continue)'
$threw = $false
try { & $script:DefaultExecutor '$null = Get-Command nosuch-command-xyz -ErrorAction SilentlyContinue; Remove-Item "$root\missing-file" -ErrorAction SilentlyContinue' $root 2>$null } catch { $threw = $true }
Assert-True (-not $threw) 'suppressed cmdlet errors (SilentlyContinue probes) do not fail the executor'
Remove-Item -Recurse -Force $root
