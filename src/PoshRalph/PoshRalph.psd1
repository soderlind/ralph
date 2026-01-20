#
# Module manifest for module 'PoshRalph'
#

@{
    # Script module or binary module file associated with this manifest.
    RootModule = 'PoshRalph.psm1'

    # Version number of this module.
    ModuleVersion = '1.1.0'

    # Supported PSEditions
    CompatiblePSEditions = @('Core')

    # ID used to uniquely identify this module
    GUID = 'a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d'

    # Author of this module
    Author = 'Snellingen'

    # Company or vendor of this module
    CompanyName = 'Unknown'

    # Copyright statement for this module
    Copyright = '(c) Snellingen. All rights reserved.'

    # Description of the functionality provided by this module
    Description = 'PowerShell implementation of the Ralph loop CLI for running GitHub Copilot in iterations'

    # Minimum version of the PowerShell engine required by this module
    PowerShellVersion = '7.0'

    # Functions to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no functions to export.
    FunctionsToExport = @('Invoke-RalphCopilot')

    # Cmdlets to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no cmdlets to export.
    CmdletsToExport = @()

    # Variables to export from this module
    VariablesToExport = @()

    # Aliases to export from this module, for best performance, do not use wildcards and do not delete the entry, use an empty array if there are no aliases to export.
    AliasesToExport = @()

    # Private data to pass to the module specified in RootModule/ModuleToProcess. This may also contain a PSData hashtable with additional module metadata used by PowerShell.
    PrivateData = @{
        PSData = @{
            # Tags applied to this module. These help with module discovery in online galleries.
            Tags = @('Copilot', 'CLI', 'AI', 'Ralph', 'Automation')

            # A URL to the license for this module.
            LicenseUri = 'https://github.com/Snellingen/posh-ralph/blob/main/LICENSE'

            # A URL to the main website for this project.
            ProjectUri = 'https://github.com/Snellingen/posh-ralph'

            # ReleaseNotes of this module
            ReleaseNotes = 'PowerShell rewrite targeting Windows with PowerShell 7+ support'
        }
    }
}
