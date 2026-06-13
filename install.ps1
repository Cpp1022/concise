# 用途：Windows 安装唯一 concise 规则；新环境启用 Codex 全局默认注入时运行；避免手工漏写 hook/config。

$ErrorActionPreference = 'Stop'

$RepoRaw = 'https://raw.githubusercontent.com/Cpp1022/concise/main'
$UserHome = [Environment]::GetFolderPath('UserProfile')
$TempDir = Join-Path ([IO.Path]::GetTempPath()) ([IO.Path]::GetRandomFileName())
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

try {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $SkillFile = Join-Path $TempDir 'SKILL.md'
    $LocalSkill = Join-Path $ScriptDir 'SKILL.md'
    if (Test-Path $LocalSkill) {
        Copy-Item $LocalSkill $SkillFile -Force
    } else {
        Invoke-WebRequest -UseBasicParsing "$RepoRaw/SKILL.md" -OutFile $SkillFile
    }

    $CodexDir = Join-Path $UserHome '.codex'
    $HookDir = Join-Path $CodexDir 'hooks'
    $HookFile = Join-Path $HookDir 'concise-user-prompt-submit.ps1'
    $HooksJson = Join-Path $CodexDir 'hooks.json'
    $ConfigToml = Join-Path $CodexDir 'config.toml'

    New-Item -ItemType Directory -Path $HookDir -Force | Out-Null
    Copy-Item $SkillFile (Join-Path $CodexDir 'instructions.md') -Force

    @'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
@{
  hookSpecificOutput = @{
    hookEventName = 'UserPromptSubmit'
    additionalContext = 'concise: 先结论；1-2句；禁计划/禁tool旁白/禁Why-How清单。'
  }
} | ConvertTo-Json -Depth 4 -Compress
'@ | Set-Content -Path $HookFile -Encoding UTF8

    function ConvertTo-Hashtable($Value) {
        if ($null -eq $Value) { return $null }
        if ($Value -is [System.Collections.IDictionary]) {
            $Hash = @{}
            foreach ($Key in $Value.Keys) { $Hash[$Key] = ConvertTo-Hashtable $Value[$Key] }
            return $Hash
        }
        if ($Value -is [System.Collections.IEnumerable] -and $Value -isnot [string]) {
            return @($Value | ForEach-Object { ConvertTo-Hashtable $_ })
        }
        if ($Value.PSObject.Properties.Count -gt 0 -and $Value.GetType().Name -eq 'PSCustomObject') {
            $Hash = @{}
            foreach ($Prop in $Value.PSObject.Properties) { $Hash[$Prop.Name] = ConvertTo-Hashtable $Prop.Value }
            return $Hash
        }
        return $Value
    }

    if (Test-Path $HooksJson) {
        try { $Data = ConvertTo-Hashtable (Get-Content $HooksJson -Raw | ConvertFrom-Json) } catch { $Data = @{} }
    } else {
        $Data = @{}
    }
    if (-not $Data.ContainsKey('hooks') -or $Data['hooks'] -isnot [hashtable]) { $Data['hooks'] = @{} }
    if (-not $Data['hooks'].ContainsKey('UserPromptSubmit') -or $Data['hooks']['UserPromptSubmit'] -isnot [array]) { $Data['hooks']['UserPromptSubmit'] = @() }

    $HookCommand = 'powershell -NoProfile -ExecutionPolicy Bypass -Command "& (Join-Path $env:USERPROFILE ''.codex\hooks\concise-user-prompt-submit.ps1'')"'
    $Kept = @()
    foreach ($Group in $Data['hooks']['UserPromptSubmit']) {
        $HasConcise = $false
        foreach ($Hook in @($Group['hooks'])) {
            if (($Hook['command'] -as [string]) -like '*concise-user-prompt-submit*') { $HasConcise = $true }
        }
        if (-not $HasConcise) { $Kept += $Group }
    }
    $Data['hooks']['UserPromptSubmit'] = @(@{ hooks = @(@{ type = 'command'; command = $HookCommand }) }) + $Kept
    $Data | ConvertTo-Json -Depth 20 | Set-Content -Path $HooksJson -Encoding UTF8

    $Lines = @()
    if (Test-Path $ConfigToml) { $Lines = @(Get-Content $ConfigToml) }
    $Out = New-Object System.Collections.Generic.List[string]
    $InFeatures = $false
    $FeaturesSeen = $false
    $CodexSeen = $false
    foreach ($Line in $Lines) {
        $Stripped = $Line.Trim()
        if ($Stripped.StartsWith('[') -and $Stripped.EndsWith(']')) {
            if ($InFeatures -and -not $CodexSeen) { $Out.Add('codex_hooks = true') }
            $InFeatures = $Stripped -eq '[features]'
            if ($InFeatures) { $FeaturesSeen = $true; $CodexSeen = $false }
        }
        if ($InFeatures -and $Stripped.StartsWith('codex_hooks')) {
            $Out.Add('codex_hooks = true')
            $CodexSeen = $true
        } else {
            $Out.Add($Line)
        }
    }
    if ($InFeatures -and -not $CodexSeen) {
        $Out.Add('codex_hooks = true')
    } elseif (-not $FeaturesSeen) {
        if ($Out.Count -gt 0 -and $Out[$Out.Count - 1].Trim()) { $Out.Add('') }
        $Out.Add('[features]')
        $Out.Add('codex_hooks = true')
    }
    ($Out -join "`n").TrimEnd() + "`n" | Set-Content -Path $ConfigToml -Encoding UTF8

    Write-Host "installed: $(Join-Path $CodexDir 'instructions.md')"
    Write-Host "installed: $HookFile"
    Write-Host "updated: $HooksJson"
    Write-Host "updated: $ConfigToml"
} finally {
    Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
}
