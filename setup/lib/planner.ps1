# Orders the tools so each one's needs run before it. Never touches the machine.
function Select-Tools([object[]]$Tools, [string]$Only) {
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
        foreach ($n in @($t.needs)) { if ($n) { & $add $byId[[string]$n] } }
        $ordered.Add($t)
    }
    foreach ($t in $roots) { & $add $t }
    return $ordered.ToArray()
}
