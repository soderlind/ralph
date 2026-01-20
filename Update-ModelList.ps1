#!/usr/bin/env pwsh
#Requires -Version 7.0

<#
.SYNOPSIS
Updates the model list in ralph scripts from the copilot CLI.

.DESCRIPTION
Extracts the available models from 'copilot --help' and updates the ValidateSet
and Show-Models functions in ralph.ps1 and ralph-once.ps1.

.PARAMETER DryRun
Show what would be updated without making changes.

.EXAMPLE
.\Update-ModelList.ps1

.EXAMPLE
.\Update-ModelList.ps1 -DryRun
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

Write-Host "Fetching model list from copilot CLI..." -ForegroundColor Cyan

# Get copilot help and extract models
try {
    $helpOutput = copilot --help 2>&1 | Out-String
}
catch {
    Write-Error "Failed to run 'copilot --help'. Is copilot CLI installed?"
    exit 1
}

# Extract the model choice line
$modelPattern = '--model\s+<model>\s+Set the AI model to use \(choices:\s*([^)]+)\)'
if ($helpOutput -match $modelPattern) {
    $modelsRaw = $Matches[1]
    
    # Parse the quoted model names, handling ANSI codes
    $models = [regex]::Matches($modelsRaw, '"([^"]+)"') | ForEach-Object { $_.Groups[1].Value }
    
    if ($models.Count -eq 0) {
        Write-Error "No models found in copilot help output"
        exit 1
    }
    
    Write-Host "Found $($models.Count) models:" -ForegroundColor Green
    $models | ForEach-Object { Write-Host "  - $_" -ForegroundColor Gray }
}
else {
    Write-Error "Could not parse model list from copilot --help"
    exit 1
}

# Generate ValidateSet code
$validateSetLines = $models | ForEach-Object { "        '$_'," }
$validateSetLines[-1] = $validateSetLines[-1].TrimEnd(',')  # Remove trailing comma from last item

$validateSetCode = @"
    [Parameter(Mandatory = `$false)]
    [ValidateSet(
$($validateSetLines -join "`n")
    )]
    [string]`$Model,
"@

Write-Host "`nGenerated ValidateSet:" -ForegroundColor Cyan
Write-Host $validateSetCode -ForegroundColor Gray

if ($DryRun) {
    Write-Host "`n[DRY RUN] Would update ralph.ps1 and ralph-once.ps1" -ForegroundColor Yellow
    exit 0
}

# Update ralph.ps1
Write-Host "`nUpdating ralph.ps1..." -ForegroundColor Cyan
$ralphContent = Get-Content -Path "ralph.ps1" -Raw

# Find and replace ValidateSet in ralph.ps1
$pattern = '(?s)(\[Parameter\(Mandatory = \$false\)\]\s+\[ValidateSet\(\s+).*?(\s+\)\]\s+\[string\]\$Model,)'
$replacement = "`$1`n$($validateSetLines -join "`n")`n    `$2"
$ralphContent = $ralphContent -replace $pattern, $replacement

Set-Content -Path "ralph.ps1" -Value $ralphContent -NoNewline
Write-Host "  ✓ Updated ralph.ps1" -ForegroundColor Green

# Update ralph-once.ps1
Write-Host "Updating ralph-once.ps1..." -ForegroundColor Cyan
$ralphOnceContent = Get-Content -Path "ralph-once.ps1" -Raw

# Find and replace ValidateSet in ralph-once.ps1
$ralphOnceContent = $ralphOnceContent -replace $pattern, $replacement

Set-Content -Path "ralph-once.ps1" -Value $ralphOnceContent -NoNewline
Write-Host "  ✓ Updated ralph-once.ps1" -ForegroundColor Green

Write-Host "`n✓ Model list updated successfully!" -ForegroundColor Green
Write-Host "Run '.\ralph.ps1 -ListModels' to see the updated list" -ForegroundColor Yellow
Write-Host "`nNote: If model costs have changed, manually update the Get-ModelCost function in:" -ForegroundColor Yellow
Write-Host "  - ralph.ps1" -ForegroundColor Gray
Write-Host "  - ralph-once.ps1" -ForegroundColor Gray
