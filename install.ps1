param(
    [ValidateSet("codex", "claude", "all", "workbuddy", "")][string]$Target = "",
    [string]$UserRoot = [Environment]::GetFolderPath("UserProfile")
)
$ErrorActionPreference = "Stop"
if (-not $Target) {
    $Choice = Read-Host "Install for: 1 Codex / 2 Claude Code / 3 Both / 4 WorkBuddy"
    $Target = switch ($Choice) {
        "1" { "codex" }
        "2" { "claude" }
        "3" { "all" }
        "4" { "workbuddy" }
        default { throw "Choose 1, 2, 3 or 4." }
    }
}
if ($Target -eq "workbuddy") {
    Write-Host "WorkBuddy: download scan-pdf-to-word.zip and import it in Skills > Add > Upload."
    Write-Host "https://github.com/laughing-glitch/scan-pdf-to-word-skill/releases/latest"
    exit 0
}
$Source = Join-Path $PSScriptRoot "skills/scan-pdf-to-word"
if (-not (Test-Path (Join-Path $Source "SKILL.md"))) { throw "Extract the complete starter package first." }
$Destinations = @()
if ($Target -in @("codex", "all")) { $Destinations += Join-Path $UserRoot ".agents/skills/scan-pdf-to-word" }
if ($Target -in @("claude", "all")) { $Destinations += Join-Path $UserRoot ".claude/skills/scan-pdf-to-word" }
foreach ($Destination in $Destinations) {
    if (Test-Path $Destination) { throw "Already exists; no files overwritten: $Destination" }
}
foreach ($Destination in $Destinations) {
    New-Item -ItemType Directory -Force -Path (Split-Path $Destination -Parent) | Out-Null
    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse
    Write-Host "Installed: $Destination"
}
Write-Host "Open a new conversation and ask the AI to initialize scan-pdf-to-word and convert your PDF."
