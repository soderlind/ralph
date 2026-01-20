#!/usr/bin/env pwsh
#Requires -Version 7.0

<#
.SYNOPSIS
Ralph single-run script - runs GitHub Copilot CLI once.

.DESCRIPTION
Runs GitHub Copilot CLI a single time with the specified prompt, PRD, skills, and tool permissions.
This is the PowerShell implementation of ralph-once.sh.

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

.PARAMETER Help
Show help message.

.EXAMPLE
.\ralph-once.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe

.EXAMPLE
.\ralph-once.ps1 -PromptFile prompts/default.txt -AllowProfile safe -Verbose

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
    [switch]$Help
)

$ErrorActionPreference = 'Stop'
$RALPH_VERSION = "1.1.0"

function Show-Usage {
    @"
Usage:
  .\ralph-once.ps1 -PromptFile <file> [-PrdFile <file>] [-Skill <a[,b,...]>] [-AllowProfile <safe|dev|locked>] [-AllowTools <toolSpec1>,<toolSpec2>,...] [-DenyTools <toolSpec1>,...] [-Help]

Options:
  -PromptFile <file>           Load prompt text from file (required).
  -PrdFile <file>              Optionally attach a PRD JSON file.
  -Skill <a[,b,...]>           Prepend one or more skills from skills/<name>/SKILL.md (comma-separated).
  -AllowProfile <name>         Tool permission profile: safe | dev | locked.
  -AllowTools <spec1>,<spec2>  Allow specific tools (comma-separated array). Example: -AllowTools write,'shell(git:*)'
  -DenyTools <spec1>,<spec2>   Deny specific tools (comma-separated array). Example: -DenyTools 'shell(rm)','shell(npm)'
  -Help                        Show this help.

Notes:
  - You must pass -AllowProfile or at least one -AllowTools.
  - For array parameters, use comma-separated values: -AllowTools tool1,tool2,tool3
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

# Run Copilot
try {
    $result = Invoke-RalphCopilot @invokeParams
    Write-Output $result.Output
    exit $result.ExitCode
}
catch {
    Write-Error "Error: $_"
    exit 1
}
