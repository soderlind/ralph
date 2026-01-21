# Ralph quickstart

## Install the module
1. Copy the module to your PowerShell modules path (per-user example):
   ```powershell
   $src = "C:\\Users\\$env:USERNAME\\Git\\posh-ralph\\src\\PoshRalph"
   $dest = "$HOME\\Documents\\PowerShell\\Modules\\PoshRalph\\1.2.0"
   New-Item -ItemType Directory -Force -Path $dest | Out-Null
   Copy-Item "$src\\*" $dest -Recurse -Force
   Import-Module PoshRalph -Force
   ```
2. Confirm the command is available:
   ```powershell
   Get-Command -Module PoshRalph
   ```

## Initialize a project for Ralph
Run the setup script in the target repo (adds prompts, plans, progress):
```powershell
# from the repo root
pwsh -File ./Setup-RalphProject.ps1
# overwrite existing prompt/plan/progress if needed
pwsh -File ./Setup-RalphProject.ps1 -Force
```

This creates/updates:
- prompts/default.txt
- plans/prd.json
- progress.txt

## Run Ralph
From the project root:
```powershell
Invoke-RalphCopilot -PromptFile "prompts/default.txt" -PrdFile "plans/prd.json" -AllowProfile safe
```
Optional:
- Add `-Skills wp-project-triage` (or any folder under skills/ with SKILL.md).
- Set `$env:MODEL` to override the default model.

## Requirements
- PowerShell 7+
- GitHub Copilot CLI available on PATH (`copilot --help`)

## Notes
- The setup files are templates; edit prompts and PRDs to match your work.
- `progress.txt` must remain in the repo root; the command fails if it is missing.
