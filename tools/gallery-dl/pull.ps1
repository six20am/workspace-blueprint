<#
.SYNOPSIS
  gallery-dl wrapper. Pulls social or web images into one folder with a resume archive.

.DESCRIPTION
  Points gallery-dl's output and its download archive at the folder you name, so a second run
  skips what the first one already fetched.

  Behaviour (throttling, filename template, directory layout) comes from the global config at
  %APPDATA%\gallery-dl\config.json. This script only decides WHERE output lands.

  Credentials are never stored. Cookie auth is passed at runtime only.

.EXAMPLE
  .\pull.ps1 -Out social-harvest -Simulate https://www.instagram.com/<your-handle>/

.EXAMPLE
  .\pull.ps1 -Out social-harvest https://www.facebook.com/<your-page>

.EXAMPLE
  .\pull.ps1 -Out social-harvest -CookiesFile C:\tmp\cookies.txt https://www.instagram.com/<your-handle>/
#>
[CmdletBinding()]
param(
    # Output folder, relative to the workspace root or absolute
    [Parameter(Mandatory)]
    [string]$Out,

    # Metadata-only run: extract and report, download nothing
    [switch]$Simulate,

    # Load cookies from an installed browser (default when no other auth is given)
    [string]$Browser = 'chrome',

    # Load cookies from a Netscape-format cookies.txt instead of a browser
    [string]$CookiesFile,

    # Skip cookie auth entirely (fine for generic crawls, fails on Instagram/Facebook)
    [switch]$Anonymous,

    # Cap the number of items, e.g. 1-40
    [string]$Range,

    # One or more URLs
    [Parameter(Mandatory, Position = 0, ValueFromRemainingArguments)]
    [string[]]$Url
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command gallery-dl -ErrorAction SilentlyContinue)) {
    throw "gallery-dl is not on PATH. Install with: pip install -U gallery-dl"
}

# tools/gallery-dl/pull.ps1 -> tools -> workspace root
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent

if ([IO.Path]::IsPathRooted($Out)) { $OutDir = $Out } else { $OutDir = Join-Path $Root $Out }
$Archive = Join-Path $OutDir '.archive.sqlite3'

New-Item -ItemType Directory -Force $OutDir | Out-Null

$galleryArgs = @('--destination', $OutDir, '--download-archive', $Archive)

if ($Simulate)   { $galleryArgs += '--simulate' }
if ($Range)      { $galleryArgs += @('--range', $Range) }

if ($Anonymous) {
    Write-Host "auth    : none (anonymous)" -ForegroundColor Yellow
}
elseif ($CookiesFile) {
    if (-not (Test-Path $CookiesFile)) { throw "Cookies file not found: $CookiesFile" }
    $galleryArgs += @('--cookies', $CookiesFile)
    Write-Host "auth    : cookies.txt ($CookiesFile)"
}
else {
    $galleryArgs += @('--cookies-from-browser', $Browser)
    Write-Host "auth    : browser cookies ($Browser)"
}

Write-Host "output  : $OutDir"
Write-Host "archive : $Archive"
Write-Host ""

& gallery-dl @galleryArgs @Url
exit $LASTEXITCODE
