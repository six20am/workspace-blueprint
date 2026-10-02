Assert-True ($null -eq (Test-Preflight -Dns { $true } -Winget { $true })) 'both probes pass means no message'
Assert-True ((Test-Preflight -Dns { $false } -Winget { $true }) -match 'internet') 'no dns means the internet message'
Assert-True ((Test-Preflight -Dns { $true } -Winget { $false }) -match 'App Installer') 'no winget means the App Installer message'
Assert-True ((Test-Preflight -Dns { $false } -Winget { $false }) -match 'internet') 'internet is checked first'
