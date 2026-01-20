function Get-CopilotToolArgs {
    <#
    .SYNOPSIS
    Builds the tool permission arguments for Copilot CLI.
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [AllowEmptyString()]
        [ValidateSet('dev', 'safe', 'locked', '')]
        [string]$AllowProfile,

        [Parameter(Mandatory = $false)]
        [string[]]$AllowTools,

        [Parameter(Mandatory = $false)]
        [string[]]$DenyTools
    )

    $args = [System.Collections.Generic.List[string]]::new()

    # Always deny dangerous commands
    $args.Add('--deny-tool')
    $args.Add('shell(rm)')
    $args.Add('--deny-tool')
    $args.Add('shell(git push)')

    # Add profile-based permissions
    if (-not $AllowTools -or $AllowTools.Count -eq 0) {
        if (-not [string]::IsNullOrWhiteSpace($AllowProfile)) {
            switch ($AllowProfile) {
                'dev' {
                    $args.Add('--allow-all-tools')
                    $args.Add('--allow-tool')
                    $args.Add('write')
                    $args.Add('--allow-tool')
                    $args.Add('shell(pnpm:*)')
                    $args.Add('--allow-tool')
                    $args.Add('shell(git:*)')
                }
                'safe' {
                    $args.Add('--allow-tool')
                    $args.Add('write')
                    $args.Add('--allow-tool')
                    $args.Add('shell(pnpm:*)')
                    $args.Add('--allow-tool')
                    $args.Add('shell(git:*)')
                }
                'locked' {
                    $args.Add('--allow-tool')
                    $args.Add('write')
                }
                default {
                    throw "Error: unknown --allow-profile: $AllowProfile"
                }
            }
        }
    }

    # Add custom allow tools
    if ($AllowTools -and $AllowTools.Count -gt 0) {
        foreach ($tool in $AllowTools) {
            $args.Add('--allow-tool')
            $args.Add($tool)
        }
    }

    # Add deny tools
    if ($DenyTools -and $DenyTools.Count -gt 0) {
        foreach ($tool in $DenyTools) {
            $args.Add('--deny-tool')
            $args.Add($tool)
        }
    }

    return $args.ToArray()
}
