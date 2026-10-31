# Loads and validates setup/tools.json. Never touches the machine.
$script:SetupAreas = @('base', 'claude', 'plugins', 'tools', 'mcp', 'logins', 'programs')

function Read-ToolList([string]$Path) {
    $raw = Get-Content -Path $Path -Raw -Encoding UTF8
    # 5.1 emits a JSON array as one object; foreach unrolls it on both 5.1 and 7.
    $parsed = ConvertFrom-Json -InputObject $raw
    $tools = @(foreach ($item in $parsed) { $item })
    for ($i = 0; $i -lt $tools.Count; $i++) {
        foreach ($arr in 'needs', 'install', 'install_mac', 'install_linux') {
            if ($null -eq $tools[$i].$arr) { $tools[$i] = $tools[$i] | Add-Member -NotePropertyName $arr -NotePropertyValue @() -Force -PassThru }
        }
        foreach ($opt in 'login', 'check_mac', 'check_linux', 'adapter') {
            if (-not ($tools[$i].PSObject.Properties.Name -contains $opt)) { $tools[$i] = $tools[$i] | Add-Member -NotePropertyName $opt -NotePropertyValue $null -PassThru }
        }
    }
    return $tools
}

function Test-ToolList([object[]]$Tools) {
    $errors = New-Object System.Collections.Generic.List[string]
    $ids = @{}
    foreach ($t in $Tools) {
        foreach ($field in 'id', 'name', 'area', 'check') {
            if (-not ($t.PSObject.Properties.Name -contains $field) -or [string]::IsNullOrWhiteSpace([string]$t.$field)) {
                $errors.Add("$($t.id): missing '$field'")
            }
        }
        if ($ids.ContainsKey([string]$t.id)) { $errors.Add("duplicate id: $($t.id)") } else { $ids[[string]$t.id] = $t }
        if ($t.area -and ($script:SetupAreas -notcontains $t.area)) { $errors.Add("$($t.id): unknown area '$($t.area)'") }
        if ((@($t.install_mac).Count -gt 0) -and [string]::IsNullOrWhiteSpace([string]$t.check_mac)) { $errors.Add("$($t.id): has install_mac but no check_mac") }
        if ((@($t.install_linux | Where-Object { $_ }).Count -gt 0) -and [string]::IsNullOrWhiteSpace([string]$t.check_linux)) { $errors.Add("$($t.id): has install_linux but no check_linux") }
        if ($t.adapter -and (@('claude-code', 'grok-bot') -notcontains [string]$t.adapter)) { $errors.Add("$($t.id): unknown adapter '$($t.adapter)'") }
    }
    foreach ($t in $Tools) {
        foreach ($n in @($t.needs)) {
            if ($n -and -not $ids.ContainsKey([string]$n)) { $errors.Add("$($t.id): needs unknown id '$n'") }
        }
    }
    # cycle check: depth-first with a visiting set
    $state = @{}
    $visit = $null
    $visit = {
        param($id)
        if ($state[$id] -eq 'done') { return $false }
        if ($state[$id] -eq 'visiting') { return $true }
        $state[$id] = 'visiting'
        foreach ($n in @($ids[$id].needs)) { if ($n -and $ids.ContainsKey([string]$n) -and (& $visit $n)) { return $true } }
        $state[$id] = 'done'
        return $false
    }
    foreach ($id in @($ids.Keys)) {
        if (& $visit $id) { $errors.Add("dependency cycle involving '$id'"); break }
    }
    return $errors.ToArray()
}
