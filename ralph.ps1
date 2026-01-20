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
Array of tool specs to allow (optional, repeatable).

.PARAMETER DenyTools
Array of tool specs to deny (optional, repeatable).

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
    [switch]$Help
)

$ErrorActionPreference = 'Stop'
$RALPH_VERSION = "1.1.0"

function Show-Usage {
    @"
Usage:
  .\ralph.ps1 -PromptFile <file> [-PrdFile <file>] [-Skill <a[,b,...]>] [-AllowProfile <safe|dev|locked>] [-AllowTools <toolSpec> ...] [-DenyTools <toolSpec> ...] -Iterations <N>

Options:
  -PromptFile <file>           Load prompt text from file (required).
  -PrdFile <file>              Optionally attach a PRD JSON file.
  -Skill <a[,b,...]>           Prepend one or more skills from skills/<name>/SKILL.md (comma-separated).
  -AllowProfile <name>         Tool permission profile: safe | dev | locked.
  -AllowTools <toolSpec>       Allow a specific tool (repeatable). Example: -AllowTools write
                               Use quotes if the spec includes spaces: -AllowTools 'shell(git push)'
  -DenyTools <toolSpec>        Deny a specific tool (repeatable). Example: -DenyTools 'shell(rm)'
  -Iterations <N>              Number of iterations to run (must be >= 1).
  -Help                        Show this help.

Notes:
  - You must pass -AllowProfile or at least one -AllowTools.
"@
}

# Show help if requested
if ($Help) {
    Show-Usage
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

# Run loop
for ($i = 1; $i -le $Iterations; $i++) {
    Write-Host "`nIteration $i" -ForegroundColor Cyan
    Write-Host "------------------------------------" -ForegroundColor Cyan

    try {
        $result = Invoke-RalphCopilot @invokeParams
        Write-Output $result.Output

        if ($result.ExitCode -ne 0) {
            Write-Warning "Copilot exited with status $($result.ExitCode); continuing to next iteration."
            continue
        }

        # Check for completion signal
        if ($result.Output -like '*<promise>COMPLETE</promise>*') {
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
