function New-CombinedPromptFile {
    <#
    .SYNOPSIS
    Creates a combined prompt file with context and prompt.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ContextFile,

        [Parameter(Mandatory = $true)]
        [string]$PromptFile
    )

    $tempFile = [System.IO.Path]::GetTempFileName()
    $sb = [System.Text.StringBuilder]::new()

    [void]$sb.AppendLine((Get-Content -Path $ContextFile -Raw))
    [void]$sb.AppendLine()
    [void]$sb.AppendLine("# Prompt")
    [void]$sb.AppendLine()
    [void]$sb.AppendLine((Get-Content -Path $PromptFile -Raw))
    [void]$sb.AppendLine()

    Set-Content -Path $tempFile -Value $sb.ToString() -Encoding UTF8 -NoNewline
    return $tempFile
}
