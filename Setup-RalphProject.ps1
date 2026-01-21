param(
    [Parameter(Mandatory = $false)]
    [string]$TargetPath = '.',

    [switch]$Force
)

function Set-RalphFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $true)]
        [string]$Content,
        [switch]$ForceWrite
    )

    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }

    if ((-not $ForceWrite) -and (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Write-Host "Skip existing: $Path" -ForegroundColor Yellow
        return
    }

    $Content | Set-Content -LiteralPath $Path -Encoding UTF8
    Write-Host "Wrote: $Path" -ForegroundColor Green
}

$resolvedRoot = Resolve-Path -LiteralPath $TargetPath -ErrorAction SilentlyContinue
if (-not $resolvedRoot) {
    New-Item -ItemType Directory -Path $TargetPath -Force | Out-Null
    $resolvedRoot = Resolve-Path -LiteralPath $TargetPath
}

$root = $resolvedRoot.Path
Write-Host "Setting up Ralph in: $root" -ForegroundColor Cyan

$promptPath = Join-Path $root 'prompts/default.txt'
$planPath = Join-Path $root 'plans/prd.json'
$progressPath = Join-Path $root 'progress.txt'
$gettingStartedPath = Join-Path $root 'RALPH-GETTING-STARTED.md'

$defaultPrompt = @'
You are Ralph. Follow the PRD and plans/prd.json. Keep responses concise, actionable, and list next steps when unclear.
'@

$defaultPlan = @'
[
  {
    "category": "functional",
    "description": "User can send a message and see it appear",
    "steps": [
      "Open the chat app and navigate to a conversation",
      "Type a message",
      "Send it",
      "Verify it appears in the thread"
    ],
    "passes": false
  }
]
'@

$defaultProgress = @'
Not started
'@

$defaultGettingStarted = @'
# Ralph: Getting Started

## Files created
- prompts/default.txt
- plans/prd.json
- progress.txt
- skills/ (place SKILL.md files here if you use skills)

## Run Ralph
From the repo root:

```
pwsh -Command "Import-Module PoshRalph; Invoke-RalphCopilot -PromptFile 'prompts/default.txt' -PrdFile 'plans/prd.json' -AllowProfile safe"
```

Notes:
- Ensure GitHub Copilot CLI is installed and on PATH (`copilot --help`).
- Skills are loaded from ./skills/<name>/SKILL.md when you pass -Skills <name> to Invoke-RalphCopilot.
- Edit prompts and PRD to reflect your project; set `passes` to false until verified.
'@

Set-RalphFile -Path $promptPath -Content $defaultPrompt -ForceWrite:$Force
Set-RalphFile -Path $planPath -Content $defaultPlan -ForceWrite:$Force
Set-RalphFile -Path $progressPath -Content $defaultProgress -ForceWrite:$Force
Set-RalphFile -Path $gettingStartedPath -Content $defaultGettingStarted -ForceWrite:$Force

Write-Host "Setup complete. Run Invoke-RalphCopilot with your prompt and PRD." -ForegroundColor Cyan
