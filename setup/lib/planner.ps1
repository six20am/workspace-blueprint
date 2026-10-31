# Orders the tools so each one's needs run before it. Never touches the machine.
# With -Adapter, an entry made for a different adapter is dropped, also when another entry needs it.
function Select-Tools([object[]]$Tools, [string]$Only, [string]$Adapter) {
    if ($Adapter) { $Tools = @($Tools | Where-Object { -not $_.adapter -or [string]$_.adapter -eq $Adapter }) }
    $byId = @{}
    foreach ($t in $Tools) { $byId[[string]$t.id] = $t }
    if ($Only) {
        $roots = @($byId[$Only])
        if ($null -eq $roots[0]) { throw "no tool with id '$Only'" }
    } else {
        $roots = @($Tools)
    }
    $ordered = New-Object System.Collections.Generic.List[object]
    $seen = @{}
    $add = $null
    $add = {
        param($t)
        if ($seen.ContainsKey([string]$t.id)) { return }
        $seen[[string]$t.id] = $true
        foreach ($n in @($t.needs)) { if ($n -and $byId.ContainsKey([string]$n)) { & $add $byId[[string]$n] } }
        $ordered.Add($t)
    }
    foreach ($t in $roots) { & $add $t }
    return $ordered.ToArray()
}
