#!/usr/bin/env pwsh
#Requires -Version 7.0

<#
.SYNOPSIS
Ralph loop script - runs GitHub Copilot CLI in iterations.

.DESCRIPTION
Runs GitHub Copilot CLI in a loop for the specified number of iterations or until completion.
This is the PowerShell implementation of ralph.sh.

.PARAMETER PromptFile
Path to the prompt file (required).

.PARAMETER PrdFile
Path to the PRD JSON file (optional).

.PARAMETER Skill
Comma-separated list of skills to load from skills/<name>/SKILL.md (optional).

.PARAMETER AllowProfile
Tool permission profile: safe, dev, or locked (optional).

.PARAMETER AllowTools
Array of tool specs to allow (comma-separated). Example: -AllowTools write,'shell(git:*)'

.PARAMETER DenyTools
Array of tool specs to deny (comma-separated). Example: -DenyTools 'shell(rm)','shell(npm)'

.PARAMETER Iterations
Number of iterations to run (required, must be >= 1).

.PARAMETER Help
Show help message.

.EXAMPLE
.\ralph.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe -Iterations 10

.EXAMPLE
.\ralph.ps1 -PromptFile prompts/default.txt -AllowProfile safe -Iterations 5 -Verbose

.NOTES
Ralph version: 1.1.0
Requires PowerShell 7.0 or higher.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [Alias('Prompt')]
    [string]$PromptFile,

    [Parameter(Mandatory = $false)]
    [Alias('Prd')]
    [string]$PrdFile,

    [Parameter(Mandatory = $false)]
    [string]$Skill,

    [Parameter(Mandatory = $false)]
    [ValidateSet('dev', 'safe', 'locked')]
    [string]$AllowProfile,

    [Parameter(Mandatory = $false)]
    [string[]]$AllowTools,

    [Parameter(Mandatory = $false)]
    [string[]]$DenyTools,

    [Parameter(Mandatory = $false)]
    [ValidateScript({ $_ -ge 1 })]
    [int]$Iterations,

    [Parameter(Mandatory = $false)]
    [ValidateSet(
        
        'claude-sonnet-4.5',
        'claude-haiku-4.5',
        'claude-opus-4.5',
        'claude-sonnet-4',
        'gpt-5.2-codex',
        'gpt-5.1-codex-max',
        'gpt-5.1-codex',
        'gpt-5.2',
        'gpt-5.1',
        'gpt-5',
        'gpt-5.1-codex-mini',
        'gpt-5-mini',
        'gpt-4.1',
        'gemini-3-pro-preview'
    
    )]
    [string]$Model,

    [Parameter(Mandatory = $false)]
    [switch]$Help,

    [Parameter(Mandatory = $false)]
    [switch]$ListModels
)

$ErrorActionPreference = 'Stop'
$RALPH_VERSION = "1.1.0"

function Show-Usage {
    @"
Usage:
  .\ralph.ps1 -PromptFile <file> [-PrdFile <file>] [-Skill <a[,b,...]>] [-AllowProfile <safe|dev|locked>] [-AllowTools <toolSpec1>,<toolSpec2>,...] [-DenyTools <toolSpec1>,...] [-Model <model>] -Iterations <N>

Options:
  -PromptFile <file>           Load prompt text from file (required).
  -PrdFile <file>              Optionally attach a PRD JSON file.
  -Skill <a[,b,...]>           Prepend one or more skills from skills/<name>/SKILL.md (comma-separated).
  -AllowProfile <name>         Tool permission profile: safe | dev | locked.
  -AllowTools <spec1>,<spec2>  Allow specific tools (comma-separated array). Example: -AllowTools write,'shell(git:*)'
  -DenyTools <spec1>,<spec2>   Deny specific tools (comma-separated array). Example: -DenyTools 'shell(rm)','shell(npm)'
  -Model <model>               AI model to use (default: claude-sonnet-4.5). Use -ListModels to see all options.
  -NoStream                    Disable streaming output (quiet mode). By default, output streams in real-time.
  -Iterations <N>              Number of iterations to run (must be >= 1).
  -Help                        Show this help.
  -ListModels                  List all available models with their costs.

Notes:
  - You must pass -AllowProfile or at least one -AllowTools.
  - For array parameters, use comma-separated values: -AllowTools tool1,tool2,tool3
"@
}

function Show-Models {
    @"
Available Models (cost relative to Claude Sonnet 4.5):

  1. claude-sonnet-4.5         1.0x  (default)
  2. claude-haiku-4.5          0.33x (fast/cheap)
  3. claude-opus-4.5           3.0x  (premium)
  4. claude-sonnet-4           1.0x
  5. gpt-5.2-codex             1.0x
  6. gpt-5.1-codex-max         1.0x
  7. gpt-5.1-codex             1.0x
  8. gpt-5.2                   1.0x
  9. gpt-5.1                   1.0x
 10. gpt-5                     1.0x
 11. gpt-5.1-codex-mini        0.33x (fast/cheap)
 12. gpt-5-mini                0.0x  (free)
 13. gpt-4.1                   0.0x  (free)
 14. gemini-3-pro-preview      1.0x

Usage: .\ralph.ps1 -Model <model-name> ...
Example: .\ralph.ps1 -Model claude-haiku-4.5 -PromptFile prompts/default.txt -AllowProfile safe -Iterations 10
"@
}

function Get-ModelCost {
    param([string]$Model)
    
    $costs = @{
        'claude-sonnet-4.5' = '1.0x'
        'claude-haiku-4.5' = '0.33x'
        'claude-opus-4.5' = '3.0x'
        'claude-sonnet-4' = '1.0x'
        'gpt-5.2-codex' = '1.0x'
        'gpt-5.1-codex-max' = '1.0x'
        'gpt-5.1-codex' = '1.0x'
        'gpt-5.2' = '1.0x'
        'gpt-5.1' = '1.0x'
        'gpt-5' = '1.0x'
        'gpt-5.1-codex-mini' = '0.33x'
        'gpt-5-mini' = 'free'
        'gpt-4.1' = 'free'
        'gemini-3-pro-preview' = '1.0x'
    }
    
    if ($costs.ContainsKey($Model)) {
        return $costs[$Model]
    }
    return 'unknown'
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

# Show models if requested
if ($ListModels) {
    Show-Models
    exit 0
}

# Validate required parameters
if ([string]::IsNullOrWhiteSpace($PromptFile)) {
    Write-Error "Error: -PromptFile is required"
    Show-Usage
    exit 1
}

if ($Iterations -lt 1) {
    Write-Error "Error: -Iterations must be a positive integer"
    Show-Usage
    exit 1
}

if (-not (Test-Path $PromptFile -PathType Leaf)) {
    Write-Error "Error: prompt file not readable: $PromptFile"
    exit 1
}

if (-not [string]::IsNullOrWhiteSpace($PrdFile) -and -not (Test-Path $PrdFile -PathType Leaf)) {
    Write-Error "Error: PRD file not readable: $PrdFile"
    exit 1
}

# Parse skills
$skillsArray = $null
if (-not [string]::IsNullOrWhiteSpace($Skill)) {
    $skillsArray = $Skill -split ',' | ForEach-Object { $_.Trim() } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
}

# Import the PoshRalph module
$modulePath = Join-Path $PSScriptRoot "src" "PoshRalph" "PoshRalph.psd1"
if (-not (Test-Path $modulePath)) {
    Write-Error "Error: PoshRalph module not found at: $modulePath"
    exit 1
}

try {
    Import-Module $modulePath -Force
}
catch {
    Write-Error "Error: Failed to import PoshRalph module: $_"
    exit 1
}

# Build parameters for Invoke-RalphCopilot
$invokeParams = @{
    PromptFile = $PromptFile
    Verbose = $VerbosePreference -eq 'Continue'
}

if (-not [string]::IsNullOrWhiteSpace($PrdFile)) {
    $invokeParams['PrdFile'] = $PrdFile
}

if ($skillsArray) {
    $invokeParams['Skills'] = $skillsArray
}

if (-not [string]::IsNullOrWhiteSpace($AllowProfile)) {
    $invokeParams['AllowProfile'] = $AllowProfile
}

if ($AllowTools -and $AllowTools.Count -gt 0) {
    $invokeParams['AllowTools'] = $AllowTools
}

if ($DenyTools -and $DenyTools.Count -gt 0) {
    $invokeParams['DenyTools'] = $DenyTools
}

if (-not [string]::IsNullOrWhiteSpace($Model)) {
    $invokeParams['Model'] = $Model
}

if ($NoStream) {
    $invokeParams['NoStream'] = $true
}

# Determine effective model
$effectiveModel = if ($Model) { 
    $Model 
} elseif ($env:MODEL) { 
    $env:MODEL 
} else { 
    'claude-sonnet-4.5' 
}

$modelCost = Get-ModelCost -Model $effectiveModel

# Display run configuration
Write-Host "`nRalph Loop Configuration" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host "Model:      $effectiveModel" -ForegroundColor White
Write-Host "Cost:       $modelCost" -ForegroundColor $(if ($modelCost -eq 'free') { 'Green' } elseif ($modelCost -like '*0.33x*') { 'Yellow' } elseif ($modelCost -like '*3.0x*') { 'Red' } else { 'White' })
Write-Host "Iterations: $Iterations" -ForegroundColor White
Write-Host "=========================" -ForegroundColor Cyan

# Run loop
for ($i = 1; $i -le $Iterations; $i++) {
    Write-Host "`nIteration $i" -ForegroundColor Cyan
    Write-Host "------------------------------------" -ForegroundColor Cyan

    try {
        $result = Invoke-RalphCopilot @invokeParams
        
        # Only write output if in NoStream mode (otherwise already displayed)
        if ($NoStream -and $result.Output) {
            Write-Output $result.Output
        }

        if ($result.ExitCode -ne 0) {
            Write-Warning "Copilot exited with status $($result.ExitCode); continuing to next iteration."
            continue
        }

        # Check for completion signal (only relevant in NoStream mode)
        if ($NoStream -and $result.Output -like '*<promise>COMPLETE</promise>*') {
            Write-Host "PRD complete, exiting." -ForegroundColor Green
            
            # Optional: notify if tt command exists
            if (Get-Command tt -ErrorAction SilentlyContinue) {
                & tt notify "PRD complete after $i iterations"
            }
            
            exit 0
        }
    }
    catch {
        Write-Warning "Error in iteration ${i}: $_"
        Write-Warning "Continuing to next iteration."
        continue
    }
}

Write-Host "Finished $Iterations iterations without receiving the completion signal." -ForegroundColor Yellow
exit 0
