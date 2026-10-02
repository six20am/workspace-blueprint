$dir = Join-Path ([IO.Path]::GetTempPath()) ('toollist ' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $dir | Out-Null
$json = @'
[
 {"id":"git","name":"Git","area":"base","check":"Test-Command git","install":["x"],"check_mac":"command -v git","install_mac":["brew install git"]},
 {"id":"claude","name":"Claude Code","area":"claude","check":"Test-Command claude","login":"sign in"},
 {"id":"sup","name":"superpowers","area":"plugins","needs":["claude"],"check":"$true"}
]
'@
[IO.File]::WriteAllText("$dir\tools.json", $json)
$tools = @(Read-ToolList -Path "$dir\tools.json")
Assert-Equal $tools.Count 3 'three tools read'
Assert-Equal (@($tools[1].needs).Count) 0 'missing needs defaults to empty'
Assert-Equal (@($tools[1].install).Count) 0 'missing install defaults to empty'
Assert-Equal (@($tools[1].install_mac).Count) 0 'missing install_mac defaults to empty'
Assert-True ($null -eq $tools[0].login) 'missing login is null'
Assert-True ($null -eq $tools[1].check_mac) 'missing check_mac is null'
Assert-Equal (@(Test-ToolList -Tools $tools).Count) 0 'valid list has no errors'

$bad = @(
    [pscustomobject]@{ id = 'a'; name = 'A'; area = 'nowhere'; check = 'x'; needs = @('zzz'); install = @(); install_mac = @('brew install a'); check_mac = $null; login = $null },
    [pscustomobject]@{ id = 'a'; name = 'A2'; area = 'base'; check = ''; needs = @(); install = @(); install_mac = @(); check_mac = $null; login = $null },
    [pscustomobject]@{ id = 'b'; name = 'B'; area = 'base'; check = 'x'; needs = @('c'); install = @(); install_mac = @(); check_mac = $null; login = $null },
    [pscustomobject]@{ id = 'c'; name = 'C'; area = 'base'; check = 'x'; needs = @('b'); install = @(); install_mac = @(); check_mac = $null; login = $null }
)
$errs = @(Test-ToolList -Tools $bad)
Assert-True (($errs -join '|') -match "unknown area 'nowhere'") 'unknown area reported'
Assert-True (($errs -join '|') -match "needs unknown id 'zzz'") 'unknown need reported'
Assert-True (($errs -join '|') -match 'duplicate id: a') 'duplicate id reported'
Assert-True (($errs -join '|') -match "missing 'check'") 'empty check reported'
Assert-True (($errs -join '|') -match 'dependency cycle') 'cycle reported'
Assert-True (($errs -join '|') -match 'install_mac but no check_mac') 'mac install without mac check reported'
Remove-Item -Recurse -Force $dir
