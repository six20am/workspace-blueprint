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
Assert-Equal (@($tools[1].install_linux).Count) 0 'missing install_linux defaults to empty'
Assert-True ($null -eq $tools[1].check_linux) 'missing check_linux is null'
Assert-True ($null -eq $tools[1].adapter) 'missing adapter is null'
Assert-True ($script:SetupAreas -contains 'programs') 'programs is an area'
Assert-Equal (@(Test-ToolList -Tools $tools).Count) 0 'valid list has no errors'

$bad = @(
    [pscustomobject]@{ id = 'a'; name = 'A'; area = 'nowhere'; check = 'x'; needs = @('zzz'); install = @(); install_mac = @('brew install a'); check_mac = $null; login = $null },
    [pscustomobject]@{ id = 'a'; name = 'A2'; area = 'base'; check = ''; needs = @(); install = @(); install_mac = @(); check_mac = $null; login = $null },
    [pscustomobject]@{ id = 'b'; name = 'B'; area = 'base'; check = 'x'; needs = @('c'); install = @(); install_mac = @(); check_mac = $null; login = $null },
    [pscustomobject]@{ id = 'c'; name = 'C'; area = 'base'; check = 'x'; needs = @('b'); install = @(); install_mac = @(); check_mac = $null; login = $null },
    [pscustomobject]@{ id = 'd'; name = 'D'; area = 'base'; check = 'x'; needs = @(); install = @(); install_mac = @(); check_mac = $null; login = $null; install_linux = @('apt-get install -y d'); check_linux = $null; adapter = 'someone' }
)
$errs = @(Test-ToolList -Tools $bad)
Assert-True (($errs -join '|') -match "unknown area 'nowhere'") 'unknown area reported'
Assert-True (($errs -join '|') -match "needs unknown id 'zzz'") 'unknown need reported'
Assert-True (($errs -join '|') -match 'duplicate id: a') 'duplicate id reported'
Assert-True (($errs -join '|') -match "missing 'check'") 'empty check reported'
Assert-True (($errs -join '|') -match 'dependency cycle') 'cycle reported'
Assert-True (($errs -join '|') -match 'install_mac but no check_mac') 'mac install without mac check reported'
Assert-True (($errs -join '|') -match 'install_linux but no check_linux') 'linux install without linux check reported'
Assert-True (($errs -join '|') -match "unknown adapter 'someone'") 'unknown adapter reported'
# the owner's tools.local.json beside tools.json is appended after the template's entries
[IO.File]::WriteAllText("$dir\tools.local.json", '{"_comment":"mine","entries":[]}')
Assert-Equal (@(Read-ToolList -Path "$dir\tools.json").Count) 3 'an empty local list adds nothing'
[IO.File]::WriteAllText("$dir\tools.local.json", '{"_comment":"mine","entries":[{"id":"mine","name":"My tool","area":"tools","check":"$true"}]}')
$merged = @(Read-ToolList -Path "$dir\tools.json")
Assert-Equal $merged.Count 4 'a local entry is merged'
Assert-Equal $merged[3].id 'mine' 'the local entry comes after the template entries'
Assert-Equal (@($merged[3].needs).Count) 0 'a local entry gets the same defaults'
Assert-Equal (@(Test-ToolList -Tools $merged).Count) 0 'the merged list validates'
[IO.File]::WriteAllText("$dir\tools.local.json", '[{"id":"mine2","name":"Mine","area":"tools","check":"$true"}]')
Assert-Equal (@(Read-ToolList -Path "$dir\tools.json").Count) 4 'a plain list works too'
[IO.File]::WriteAllText("$dir\tools.local.json", '{"entries":[{"id":"git","name":"Git again","area":"base","check":"$true"}]}')
$dupMessage = ''
try { Read-ToolList -Path "$dir\tools.json" | Out-Null } catch { $dupMessage = $_.Exception.Message }
Assert-True ($dupMessage -match "tools.local.json: the id 'git' is already used") 'a duplicate local id is refused clearly'
Remove-Item -Recurse -Force $dir
