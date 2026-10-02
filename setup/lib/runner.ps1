# Runs tools against the machine. Real side effects only through the default executor.

function Get-WingetPath {
    $cmd = Get-Command winget -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $apps = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\winget.exe'
    if (Test-Path $apps) { return $apps }
    return $null
}

function Update-SessionPath {
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $links = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Links'
    $parts = @($machine, $user, $links) | Where-Object { $_ }
    # pip falls back to a user install under a machine-scope Python; its Scripts folder is on no PATH.
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $prev = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
        try {
            $scripts = (& python -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))" 2>$null | Select-Object -First 1)
            if ($scripts) {
                $scripts = ([string]$scripts).Trim()
                if ($scripts -and (Test-Path -LiteralPath $scripts) -and (@($parts -split ';') -notcontains $scripts)) { $parts = @($parts) + $scripts }
            }
        } catch { } finally { $ErrorActionPreference = $prev }
    }
    $env:Path = ((@($parts) -join ';') -split ';' | Where-Object { $_ } | Select-Object -Unique) -join ';'
}

function Test-Command([string]$Name) {
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Install-Winget([string]$Id) {
    $w = Get-WingetPath
    if (-not $w) { throw 'winget not found. Install "App Installer" from the Microsoft Store, then run setup again.' }
    $common = @('install', '--id', $Id, '--exact', '--silent', '--accept-package-agreements', '--accept-source-agreements', '--disable-interactivity')
    & $w @($common + @('--scope', 'user'))
    if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq -1978335189) { $global:LASTEXITCODE = 0; return }   # -1978335189: already installed
    & $w @common                                                           # some packages only install machine-wide
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -ne -1978335189) { throw "winget install $Id failed with exit code $LASTEXITCODE" }
    $global:LASTEXITCODE = 0
}

function Install-NpmDeps([string]$Dir) {
    & npm install --prefix $Dir --no-audit --no-fund
    if ($LASTEXITCODE -ne 0) { throw "npm install in $Dir failed with exit code $LASTEXITCODE" }
}

function Add-ClaudePlugin([string]$MarketplaceRepo, [string]$MarketplaceName, [string]$Plugin) {
    $ErrorActionPreference = 'Continue'   # 5.1 turns native stderr into a terminating error under Stop
    $markets = (& claude plugin marketplace list 2>&1) -join "`n"
    if ($markets -notmatch [regex]::Escape($MarketplaceName)) {
        & claude plugin marketplace add $MarketplaceRepo
        if ($LASTEXITCODE -ne 0) { throw "adding marketplace $MarketplaceRepo failed" }
    }
    & claude plugin install "$Plugin@$MarketplaceName"
    if ($LASTEXITCODE -ne 0) { throw "installing plugin $Plugin failed" }
}

$script:DefaultExecutor = {
    param($cmd, $root)
    $ErrorActionPreference = 'Continue'   # 5.1: native stderr must not throw; the exit code is the signal
    Push-Location -LiteralPath $root
    try {
        $global:LASTEXITCODE = 0
        Invoke-Expression $cmd
        if ($LASTEXITCODE -ne 0) { throw "exit code $LASTEXITCODE" }
    } finally { Pop-Location }
}

$script:DefaultChecker = {
    param($expr, $root)
    $ErrorActionPreference = 'Continue'
    Push-Location -LiteralPath $root
    try { return [bool](Invoke-Expression $expr) } catch { return $false } finally { Pop-Location }
}

function Invoke-ToolRun([object[]]$Tools, [string]$Root, [switch]$DryRun, [scriptblock]$Executor, [scriptblock]$Checker) {
    if (-not $Executor) { $Executor = $script:DefaultExecutor }
    if (-not $Checker) { $Checker = $script:DefaultChecker }
    $done = @{}
    $results = New-Object System.Collections.Generic.List[object]
    foreach ($t in $Tools) {
        $r = [pscustomobject]@{ Id = [string]$t.id; Name = [string]$t.name; Area = [string]$t.area; Status = ''; Detail = ''; Login = $t.login }
        $missing = @(@($t.needs) | Where-Object { $_ -and @('present', 'installed', 'planned') -notcontains $done[[string]$_] })
        if (& $Checker $t.check $Root) {
            $r.Status = 'present'
        } elseif ($missing.Count -gt 0) {
            $r.Status = 'skipped'; $r.Detail = 'needs ' + ($missing -join ', ')
        } elseif (@($t.install).Count -eq 0) {
            $r.Status = 'manual'
        } elseif ($DryRun) {
            $r.Status = 'planned'
        } else {
            try {
                Write-Host "Installing $($t.name)..."
                foreach ($cmd in @($t.install)) { & $Executor $cmd $Root | ForEach-Object { Write-Host "$_" } }
                Update-SessionPath
                if (& $Checker $t.check $Root) { $r.Status = 'installed' }
                else { $r.Status = 'failed'; $r.Detail = 'install ran but the check still fails' }
            } catch {
                $r.Status = 'failed'; $r.Detail = $_.Exception.Message
            }
        }
        $done[$r.Id] = $r.Status
        $results.Add($r)
    }
    return $results.ToArray()
}
