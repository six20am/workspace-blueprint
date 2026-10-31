function New-PlanTool([string]$Id, [string[]]$Needs = @()) {
    [pscustomobject]@{ id = $Id; name = $Id; area = 'base'; needs = $Needs; check = 'x'; install = @(); install_mac = @(); check_mac = $null; login = $null }
}
$tools = @((New-PlanTool 'claude'), (New-PlanTool 'plugin' @('claude')), (New-PlanTool 'node'), (New-PlanTool 'playwright' @('node')), (New-PlanTool 'mcp' @('node', 'claude')))
$ids = @(Select-Tools -Tools $tools | ForEach-Object { $_.id })
Assert-Equal ($ids -join ',') 'claude,plugin,node,playwright,mcp' 'file order kept, needs already satisfied'
$rev = @(Select-Tools -Tools @($tools[4], $tools[0], $tools[2]) | ForEach-Object { $_.id })
Assert-Equal ($rev -join ',') 'node,claude,mcp' 'a need listed later still runs first'
$one = @(Select-Tools -Tools $tools -Only 'playwright' | ForEach-Object { $_.id })
Assert-Equal ($one -join ',') 'node,playwright' '-Only pulls in its needs and nothing else'
$threw = $false
try { Select-Tools -Tools $tools -Only 'nope' | Out-Null } catch { $threw = $true }
Assert-True $threw 'unknown -Only id throws'
$grok = [pscustomobject]@{ id = 'bot'; name = 'bot'; area = 'base'; needs = @(); check = 'x'; install = @(); install_mac = @(); check_mac = $null; login = $null; adapter = 'grok-bot' }
$cc = [pscustomobject]@{ id = 'hook'; name = 'hook'; area = 'base'; needs = @('bot', 'node'); check = 'x'; install = @(); install_mac = @(); check_mac = $null; login = $null; adapter = 'claude-code' }
$mixed = @((New-PlanTool 'node'), $grok, $cc)
$forCc = @(Select-Tools -Tools $mixed -Adapter 'claude-code' | ForEach-Object { $_.id })
Assert-Equal ($forCc -join ',') 'node,hook' 'a grok-bot entry is dropped for claude-code, also as a need'
$forGrok = @(Select-Tools -Tools $mixed -Adapter 'grok-bot' | ForEach-Object { $_.id })
Assert-Equal ($forGrok -join ',') 'node,bot' 'a grok-bot entry is kept for grok-bot and a claude-code entry dropped'
$forAll = @(Select-Tools -Tools $mixed | ForEach-Object { $_.id })
Assert-Equal ($forAll -join ',') 'node,bot,hook' 'no -Adapter keeps every entry'
