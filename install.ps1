param(
    [ValidateSet('codex', 'uninstall')][string]$Action = 'codex',
    [string]$CodexHome
)
$ErrorActionPreference = 'Stop'
$Python = $null
$PythonArgs = @()
foreach ($Candidate in @('python', 'python3', 'py')) {
    $Command = Get-Command $Candidate -CommandType Application -ErrorAction SilentlyContinue
    if (-not $Command) { continue }
    $Prefix = @()
    if ($Candidate -eq 'py') { $Prefix = @('-3') }
    & $Command.Source @Prefix -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)' 2>$null
    if ($LASTEXITCODE -eq 0) { $Python = $Command.Source; $PythonArgs = $Prefix; break }
}
if (-not $Python) { throw 'concise requires Python 3.11+; no Codex configuration was changed.' }
$EngineArgs = @($Action)
if ($CodexHome) { $EngineArgs += @('--codex-home', $CodexHome) }
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { $null }
$Engine = if ($ScriptDir) { Join-Path $ScriptDir 'install.py' } else { $null }
$LocalSkill = if ($ScriptDir) { Join-Path $ScriptDir 'skills/concise/SKILL.md' } else { $null }
if ($Engine -and (Test-Path -LiteralPath $Engine) -and ($Action -eq 'uninstall' -or (Test-Path -LiteralPath $LocalSkill))) {
    & $Python @PythonArgs $Engine @EngineArgs
    if ($LASTEXITCODE -ne 0) { throw 'concise installation or recovery failed; see the message above.' }
} else {
    $TempDir = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $TempDir | Out-Null
    try {
        $Base = 'https://raw.githubusercontent.com/Cpp1022/concise/main'
        $Engine = Join-Path $TempDir 'install.py'
        Invoke-WebRequest -UseBasicParsing "$Base/install.py" -OutFile $Engine
        if ($Action -eq 'codex') {
            $Skill = Join-Path $TempDir 'SKILL.md'
            Invoke-WebRequest -UseBasicParsing "$Base/skills/concise/SKILL.md" -OutFile $Skill
            $EngineArgs += @('--skill-file', $Skill)
        }
        & $Python @PythonArgs $Engine @EngineArgs
        if ($LASTEXITCODE -ne 0) { throw 'concise installation or recovery failed; see the message above.' }
    } finally {
        if ([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($TempDir)) -ne [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\')) {
            throw 'Unexpected temporary cleanup path.'
        }
        Remove-Item -LiteralPath $TempDir -Recurse -Force
    }
}
