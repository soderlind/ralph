# posh-ralph — PowerShell version of the AI Ralph loop CLI

> Let AI implement your features while you sleep — **now on Windows with PowerShell**.

**posh-ralph** is a PowerShell implementation of the Ralph loop command-line tool. It runs **GitHub Copilot CLI** in a loop, implementing one feature at a time until your PRD is complete.

This repository targets **Windows (PowerShell 7+)** as the primary platform and aims to remain **cross-platform** when run with **PowerShell 7+** on Linux/macOS.

⚠️ **Note:** Linux/macOS are **not tested** in this repository at this time.

[Quick Start](#quick-start) · [How It Works](#how-it-works) · [Requirements](#requirements) · [Installation](#installation) · [Usage](#usage) · [Configuration](#configuration) · [Command Reference](#command-reference) · [Cross-Platform](#cross-platform-note)

---

## Quick Start

```powershell
# Clone and enter the repo
git clone https://github.com/Snellingen/posh-ralph
cd posh-ralph

# Add your work items to plans/prd.json

# Test with a single run
.\ralph-once.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe

# Run multiple iterations
.\ralph.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe -Iterations 10
```

Check `progress.txt` for a log of what was done.

---

## How It Works

Ralph implements the ["Ralph Wiggum" technique](https://www.humanlayer.dev/blog/brief-history-of-ralph):

1. **Read** — Copilot reads your PRD (if attached) and progress file
2. **Pick** — It chooses the highest-priority incomplete item
3. **Implement** — It writes code for that one feature
4. **Verify** — It runs your tests (`pnpm typecheck`, `pnpm test`)
5. **Update** — It marks the item complete and logs progress
6. **Commit** — It commits the changes
7. **Repeat** — Until all items pass or it signals completion

https://github.com/user-attachments/assets/28206ee1-8dad-4871-aef5-1a9f24625dba

### Learn More

- [Matt Pocock's thread](https://x.com/mattpocockuk/status/2007924876548637089)
- [Ship working code while you sleep (video)](https://www.youtube.com/watch?v=_IK18goX4X8)
- [11 Tips For AI Coding With Ralph Wiggum](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Requirements

- **Windows** with **PowerShell 7+** (recommended)
  - Download: [PowerShell 7+ for Windows](https://github.com/PowerShell/PowerShell/releases)
- **GitHub Copilot CLI** installed and authenticated
  - Install: `winget install GitHub.Copilot` or `npm i -g @github/copilot`
- Any required API keys/tokens (if needed by your configuration)

---

## Installation (Dev)

```powershell
# Clone the repository
git clone https://github.com/Snellingen/posh-ralph.git
cd posh-ralph

# Verify PowerShell version (must be 7.0+)
$PSVersionTable.PSVersion

# Run directly
.\ralph-once.ps1 -Help
```

---

## Usage

### Start the Ralph Loop

```powershell
# Run with a prompt and PRD for 10 iterations
.\ralph.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe -Iterations 10

# Run with verbose output
.\ralph.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe -Iterations 10 -Verbose

# Use a custom model
$env:MODEL = "claude-opus-4.5"
.\ralph.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe -Iterations 10
```

### Single Test Run

```powershell
# Test with a single iteration
.\ralph-once.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe

# Run with verbose output
.\ralph-once.ps1 -PromptFile prompts/default.txt -AllowProfile safe -Verbose
```

### Show Help

```powershell
# Show help for the loop script
.\ralph.ps1 -Help

# Show help for the single-run script
.\ralph-once.ps1 -Help
```

---

## Configuration

### Choose a Model

Set the `MODEL` environment variable (default: `gpt-5.2`):

```powershell
$env:MODEL = "claude-opus-4.5"
.\ralph.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe -Iterations 10
```

### Define Your Work Items

Create `plans/prd.json` with your requirements:

```json
[
  {
    "category": "functional",
    "description": "User can send a message and see it in the conversation",
    "steps": ["Open chat", "Type message", "Click Send", "Verify it appears"],
    "passes": false
  }
]
```

| Field         | Description                                |
|---------------|--------------------------------------------|
| `category`    | `"functional"`, `"ui"`, or custom          |
| `description` | One-line summary                           |
| `steps`       | How to verify it works                     |
| `passes`      | `false` → `true` when complete             |

See the [`plans/`](plans/) folder for more examples.

### Use Custom Prompts

Prompts are required. Use any prompt file:

```powershell
.\ralph.ps1 -PromptFile prompts/my-prompt.txt -AllowProfile safe -Iterations 10
```

> **Note:** Custom prompts require `-AllowProfile` or `-AllowTools`.

---

## Command Reference

### `ralph.ps1` — Looped Runner

Runs Copilot up to N iterations. Stops early on `<promise>COMPLETE</promise>`.

```powershell
.\ralph.ps1 [options] -Iterations <N>
```

**Options:**

| Option                   | Description                          | Default               |
|--------------------------|--------------------------------------|-----------------------|
| `-PromptFile <file>`     | Load prompt from file (required)     | —                     |
| `-PrdFile <file>`        | Optionally attach a PRD JSON file    | —                     |
| `-Skill <a[,b,...]>`     | Prepend skills from `skills/<name>/SKILL.md` | —              |
| `-AllowProfile <name>`   | Permission profile (see below)       | —                     |
| `-AllowTools <spec>`     | Allow specific tool (repeatable)     | —                     |
| `-DenyTools <spec>`      | Deny specific tool (repeatable)      | —                     |
| `-Iterations <N>`        | Number of iterations (required)      | —                     |
| `-Verbose`               | Show verbose output                  | —                     |
| `-Help`                  | Show help                            | —                     |

**Examples:**

```powershell
.\ralph.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe -Iterations 10
.\ralph.ps1 -PromptFile prompts/wp.txt -AllowProfile safe -Iterations 10 -Verbose

$env:MODEL = "claude-opus-4.5"
.\ralph.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe -Iterations 10
```

### `ralph-once.ps1` — Single Run

Runs Copilot once. Great for testing.

```powershell
.\ralph-once.ps1 [options]
```

**Options:**

Same as `ralph.ps1` except no `-Iterations` parameter.

**Examples:**

```powershell
.\ralph-once.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe
.\ralph-once.ps1 -PromptFile prompts/wp.txt -AllowProfile locked -Verbose

$env:MODEL = "claude-opus-4.5"
.\ralph-once.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe
```

### Permission Profiles

| Profile  | Allows                                 | Use Case                     |
|----------|----------------------------------------|------------------------------|
| `locked` | `write` only                           | File edits, no shell         |
| `safe`   | `write`, `shell(pnpm:*)`, `shell(git:*)` | Normal dev workflow        |
| `dev`    | All tools                              | Broad shell access           |

**Always denied:** `shell(rm)`, `shell(git push)`

**Custom tools:** If you pass `-AllowTools`, it replaces the profile defaults:

```powershell
.\ralph.ps1 -PromptFile prompts/wp.txt -AllowTools write -AllowTools 'shell(composer:*)' -Iterations 10
```

### Environment Variables

| Variable | Description        | Default   |
|----------|--------------------|-----------|
| `MODEL`  | Model to use       | `gpt-5.2` |

---

## Cross-Platform Note

If you have **PowerShell 7+** on Linux/macOS, you can run posh-ralph:

```bash
# Linux/macOS with PowerShell 7+
pwsh -File ./ralph.ps1 -PromptFile prompts/default.txt -PrdFile plans/prd.json -AllowProfile safe -Iterations 10
```

> ⚠️ This path is **not tested** in this repo yet. Please open issues with findings.

---

## Differences from the Original

- **PowerShell-based CLI/runtime** instead of shell scripts
- **Windows-first** testing and guidance
- **PowerShell 7+ requirement** (no Windows PowerShell 5.1 support)
- Command names/flags are kept as close as possible to the original
- Uses PowerShell parameter syntax (`-ParameterName value`) instead of shell syntax (`--parameter value`)

---

## Project Structure

```
.
├── src/PoshRalph/             # PowerShell module
│   ├── PoshRalph.psd1         # Module manifest
│   ├── PoshRalph.psm1         # Module loader
│   ├── Public/                # Exported functions
│   └── Private/               # Internal helpers
├── plans/prd.json             # Your work items
├── prompts/default.txt        # Example prompt
├── progress.txt               # Running log
├── ralph.ps1                  # Looped runner (PowerShell)
├── ralph-once.ps1             # Single-run script (PowerShell)
├── ralph.sh                   # Legacy bash looped runner
└── ralph-once.sh              # Legacy bash single-run script
```

---

## Install Copilot CLI

```powershell
# Check version
copilot --version

# Windows (winget)
winget install GitHub.Copilot

# Windows (npm)
npm i -g @github/copilot

# Upgrade (winget)
winget upgrade GitHub.Copilot

# Upgrade (npm)
npm update -g @github/copilot
```

For Linux/macOS:

```bash
# Homebrew
brew update && brew upgrade copilot

# npm
npm i -g @github/copilot
```

---

## Contributing

- Please open issues for gaps, bugs, or Linux/macOS experiences
- PRs welcome—prefer small, focused changes
- PowerShell code should follow standard conventions and use `CmdletBinding()` for functions

---

## Skills (`-Skill`)

[Skills](https://agentskills.io/home) let you prepend reusable instructions into the same attached context file.
Pass a comma-separated list:

- `-Skill wp-block-development` loads `skills/wp-block-development/SKILL.md`
- `-Skill aa,bb,cc` loads `skills/aa/SKILL.md`, `skills/bb/SKILL.md`, `skills/cc/SKILL.md`

Example:

```powershell
.\ralph.ps1 -PromptFile prompts/wordpress-plugin-agent.txt `
  -Skill wp-block-development,wp-cli `
  -PrdFile plans/prd.json `
  -AllowProfile safe `
  -Iterations 5
```

---

## Testing Prompts

The original bash test harness is available:

```bash
./test/run-prompts.sh
```

Logs: `test/log/`

> **Note:** A PowerShell version of the test harness may be added in the future.

---

## License

MIT — see [LICENSE](LICENSE).
