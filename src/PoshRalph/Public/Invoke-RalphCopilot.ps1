function Invoke-RalphCopilot {
    <#
    .SYNOPSIS
    Invokes GitHub Copilot CLI with the specified prompt and configuration.
    
    .DESCRIPTION
    Core function that runs a single iteration of GitHub Copilot CLI with the provided
    prompt, PRD, skills, and tool permissions.
    
    .PARAMETER PromptFile
    Path to the prompt file (required).
    
    .PARAMETER PrdFile
    Path to the PRD JSON file (optional).
    
    .PARAMETER Skills
    Array of skill names to load from skills/<name>/SKILL.md (optional).
    
    .PARAMETER AllowProfile
    Tool permission profile: safe, dev, or locked (optional).
    
    .PARAMETER AllowTools
    Array of tool specs to allow (optional, repeatable).
    
    .PARAMETER DenyTools
    Array of tool specs to deny (optional, repeatable).
    
    .PARAMETER Model
    Model to use for Copilot (defaults to gpt-5.2 or $env:MODEL).
    
    .EXAMPLE
    Invoke-RalphCopilot -PromptFile "prompts/default.txt" -AllowProfile safe
    
    .EXAMPLE
    Invoke-RalphCopilot -PromptFile "prompts/default.txt" -PrdFile "plans/prd.json" -AllowProfile safe -Verbose
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ -PathType Leaf })]
        [string]$PromptFile,

        [Parameter(Mandatory = $false)]
        [ValidateScript({ Test-Path $_ -PathType Leaf })]
        [string]$PrdFile,

        [Parameter(Mandatory = $false)]
        [string[]]$Skills,

        [Parameter(Mandatory = $false)]
        [AllowEmptyString()]
        [ValidateSet('dev', 'safe', 'locked', '')]
        [string]$AllowProfile,

        [Parameter(Mandatory = $false)]
        [string[]]$AllowTools,

        [Parameter(Mandatory = $false)]
        [string[]]$DenyTools,

        [Parameter(Mandatory = $false)]
        [string]$Model = 'gpt-5.2'
    )

    Write-Verbose "Starting Ralph Copilot invocation"
    Write-Verbose "Prompt: $PromptFile"
    if ($PrdFile) { Write-Verbose "PRD: $PrdFile" }
    if ($Skills) { Write-Verbose "Skills: $($Skills -join ', ')" }

    # Validate progress file exists
    $progressFile = Join-Path $PWD "progress.txt"
    if (-not (Test-Path $progressFile -PathType Leaf)) {
        throw "Error: progress file not readable: $progressFile"
    }

    # Validate tool permissions
    if ([string]::IsNullOrWhiteSpace($AllowProfile) -and (-not $AllowTools -or $AllowTools.Count -eq 0)) {
        throw "Error: you must specify -AllowProfile or at least one -AllowTools"
    }

    # Use environment MODEL if set
    if ($env:MODEL) {
        $Model = $env:MODEL
        Write-Verbose "Using model from environment: $Model"
    }

    # Create context and prompt files
    $contextFile = $null
    $combinedPromptFile = $null
    
    try {
        Write-Verbose "Creating context file"
        $contextFile = New-ContextFile -Skills $Skills -PrdFile $PrdFile -ProgressFile $progressFile
        
        Write-Verbose "Creating combined prompt file"
        $combinedPromptFile = New-CombinedPromptFile -ContextFile $contextFile -PromptFile $PromptFile

        Write-Verbose "Building tool arguments"
        $toolArgs = Get-CopilotToolArgs -AllowProfile $AllowProfile -AllowTools $AllowTools -DenyTools $DenyTools

        # Build copilot command
        $copilotArgs = @(
            '--add-dir', $PWD
            '--model', $Model
            '--no-color'
            '--stream', 'off'
            '--silent'
            '-p', "@$combinedPromptFile Follow the attached prompt."
        ) + $toolArgs

        Write-Verbose "Invoking: copilot $($copilotArgs -join ' ')"

        # Invoke copilot and capture output
        $output = & copilot @copilotArgs 2>&1
        $exitCode = $LASTEXITCODE

        # Return results
        return @{
            Output = ($output | Out-String)
            ExitCode = $exitCode
        }
    }
    catch {
        Write-Error "Error invoking Copilot: $_"
        throw
    }
    finally {
        # Cleanup temp files
        if ($contextFile -and (Test-Path $contextFile)) {
            Remove-Item $contextFile -Force -ErrorAction SilentlyContinue
        }
        if ($combinedPromptFile -and (Test-Path $combinedPromptFile)) {
            Remove-Item $combinedPromptFile -Force -ErrorAction SilentlyContinue
        }
    }
}
