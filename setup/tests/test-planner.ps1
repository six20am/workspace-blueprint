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
