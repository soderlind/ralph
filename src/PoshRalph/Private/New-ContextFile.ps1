function New-ContextFile {
    <#
    .SYNOPSIS
    Creates a context file for Copilot CLI with skills, PRD, and progress.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string[]]$Skills,

        [Parameter(Mandatory = $false)]
        [string]$PrdFile,

        [Parameter(Mandatory = $true)]
        [string]$ProgressFile
    )

    # Create temp file in current directory instead of system temp
    $tempFile = Join-Path $PWD ".ralph-context-$(Get-Random).tmp"
    $sb = [System.Text.StringBuilder]::new()

    [void]$sb.AppendLine("# Context")
    [void]$sb.AppendLine()

    # Add skills
    if ($Skills -and $Skills.Count -gt 0) {
        [void]$sb.AppendLine("## Skills")
        foreach ($skill in $Skills) {
            $skillTrimmed = $skill.Trim()
            if ([string]::IsNullOrWhiteSpace($skillTrimmed)) {
                continue
            }
            $skillFile = Join-Path $PWD "skills" $skillTrimmed "SKILL.md"
            if (-not (Test-Path $skillFile -PathType Leaf)) {
                throw "Error: skill not found/readable: $skillFile"
            }
            [void]$sb.AppendLine()
            [void]$sb.AppendLine("### $skillTrimmed")
            [void]$sb.AppendLine()
            [void]$sb.AppendLine((Get-Content -Path $skillFile -Raw))
        }
        [void]$sb.AppendLine()
    }

    # Add PRD
    if (-not [string]::IsNullOrWhiteSpace($PrdFile)) {
        [void]$sb.AppendLine("## PRD ($PrdFile)")
        [void]$sb.AppendLine((Get-Content -Path $PrdFile -Raw))
        [void]$sb.AppendLine()
    }

    # Add progress
    [void]$sb.AppendLine("## progress.txt")
    [void]$sb.AppendLine((Get-Content -Path $ProgressFile -Raw))
    [void]$sb.AppendLine()

    Set-Content -Path $tempFile -Value $sb.ToString() -Encoding UTF8 -NoNewline
    return $tempFile
}
