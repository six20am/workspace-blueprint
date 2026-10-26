# The things setup cannot work without. Probes are injectable so tests never touch the network.
function Test-Preflight([scriptblock]$Dns, [scriptblock]$Winget, [string]$Root) {
    if (-not $Dns) { $Dns = { try { [void][System.Net.Dns]::GetHostAddresses('github.com'); $true } catch { $false } } }
    if (-not $Winget) { $Winget = { [bool](Get-WingetPath) } }
    # Windows refuses paths over 260 characters; the kit's deepest file and npm installs add about 140.
    if ($Root -and $Root.Length -gt 120) { return 'This folder is inside too many other folders for Windows to handle. Move it to Documents, then run setup again.' }
    if (-not (& $Dns)) { return 'No internet connection. Connect to the internet, then run setup again.' }
    if (-not (& $Winget)) { return 'This computer is missing "App Installer". Open the Microsoft Store, search for App Installer, install it, then run setup again.' }
    return $null
}
