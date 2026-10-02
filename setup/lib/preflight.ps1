# The two things setup cannot work without. Probes are injectable so tests never touch the network.
function Test-Preflight([scriptblock]$Dns, [scriptblock]$Winget) {
    if (-not $Dns) { $Dns = { try { [void][System.Net.Dns]::GetHostAddresses('github.com'); $true } catch { $false } } }
    if (-not $Winget) { $Winget = { [bool](Get-WingetPath) } }
    if (-not (& $Dns)) { return 'No internet connection. Connect to the internet, then run setup again.' }
    if (-not (& $Winget)) { return 'This computer is missing "App Installer". Open the Microsoft Store, search for App Installer, install it, then run setup again.' }
    return $null
}
