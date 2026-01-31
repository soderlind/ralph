# Ralph - Autonomous Coding Agent Loop

Ralph is a Python wrapper for GitHub Copilot CLI that autonomously implements PRD stories one at a time.

## Principles

Based on the Ralph Wiggum loop:
1. **ONE story at a time** - Ralph picks the highest priority unfinished story
2. **Tests must pass** - Story marked `passes: true` only when tests succeed
3. **Clean repo** - All changes must be committed, no dirty git state
4. **Progress tracking** - All iterations logged to `progress.txt`

## Usage

```bash
# Basic usage with safe profile (allows write, pnpm, git)
./ralph.py --allow-profile safe --max-iterations 10

# Single iteration (like old ralph-once.sh)
./ralph.py --once --allow-profile safe

# With custom PRD location
./ralph.py --prd plans/my-prd.json --allow-profile safe --max-iterations 20

# Allow starting with uncommitted changes (ralph will commit at each story completion)
./ralph.py --allow-profile safe --allow-dirty --max-iterations 5

# Add custom prompt instructions
./ralph.py --allow-profile safe --prompt-prefix prompts/custom.txt --max-iterations 10

# Dev mode (allows all tools)
./ralph.py --allow-profile dev --max-iterations 10

# Locked mode (write only, no shell commands)
./ralph.py --allow-profile locked --max-iterations 5

# Yolo mode (run without hesitation)
./ralph.py --allow-profile yolo --max-iterations 10

# Custom model
./ralph.py --allow-profile safe --model claude-sonnet-4.5 --max-iterations 10
```

## Key Parameters

- `--prd <path>` - Path to PRD JSON file (default: `plans/prd.json`)
- `--progress <path>` - Path to progress log (default: `progress.txt`)
- `--allow-profile <safe|dev|locked|yolo>` - Tool permission profile
- `--once` - Run only one iteration (same as `--max-iterations 1`)
- `--allow-dirty` - Allow starting with uncommitted changes
- `--prompt-prefix <path>` - Optional file with additional instructions prepended to each prompt
- `--max-iterations <N>` - Maximum iterations to run (default: 20)
- `--model <name>` - Copilot model to use (default: `gpt-5.2`)

## Profiles

- **safe**: Allows `write`, `shell(pnpm:*)`, `shell(git:*)` - suitable for most development
- **dev**: Allows all tools - use with caution
- **locked**: Only allows `write` - very restricted, no commands
- **yolo**: Runs with `--yolo` flag - skip confirmations, run without hesitation

## Iterative Workflow

**Clean Repo (Default):**
```bash
# Ralph requires clean repo to start
./ralph.py --allow-profile safe --max-iterations 5
```

**Iterative Mode (with --allow-dirty):**
```bash
# Run 3 iterations
./ralph.py --allow-profile safe --allow-dirty --max-iterations 3

# Review changes manually, edit if needed
git diff

# Run 3 more iterations (ralph will commit at each story completion)
./ralph.py --allow-profile safe --allow-dirty --max-iterations 3

# Manually commit any remaining changes
git add -A && git commit -m "Final manual adjustments"
```

## PRD Format

Your `prd.json` should be an array of stories:

```json
[
  {
    "id": "arch-001",
    "category": "architecture",
    "priority": 1,
    "description": "Setup Next.js boilerplate",
    "steps": [
      "Copy next-boilerplate to project root",
      "Delete unnecessary pages",
      "Update package.json"
    ],
    "tests": [
      "pnpm install",
      "pnpm typecheck"
    ],
    "passes": false,
    "dependsOn": []
  }
]
```

## Prompt Prefix (Optional)

Create `prompts/custom.txt` with additional instructions:

```
IMPORTANT: Use TypeScript strict mode.
Follow project coding conventions in .eslintrc.
Always add JSDoc comments to exported functions.
```

This will be prepended to every story prompt.

## Requirements

- Python 3.10+
- GitHub Copilot CLI installed (`copilot` in PATH)
- Git repository
- Clean working tree to start (or use `--allow-dirty`)

## How It Works

1. Ralph loads your PRD and picks the next story (sorted by priority)
2. Builds a prompt with the story details, steps, and recent progress
3. Calls Copilot CLI in programmatic mode (`copilot -p "prompt"`)
4. Waits for Copilot to complete the work
5. Runs the story's tests
6. If tests pass: marks `passes: true`, commits changes
7. If tests fail: logs failure, continues to next iteration
8. Repeats until all stories pass or max iterations reached

## Completion

When ALL stories have `passes: true` AND all final tests pass AND git is clean, Ralph outputs the completion token (default: `COMPLETE`) and exits with code 0.

## Files

- `prd.json` - Source of truth for stories
- `progress.txt` - Append-only log of all iterations
- `.ralph/state.json` - Metadata (runs, timestamps)

## Tips

- Start with 1-2 stories to test the loop
- Add meaningful tests to each story
- Keep stories small and focused
- Review `progress.txt` to understand what happened
- Ralph will NOT push to remote (safety: denies `shell(git push)`)
- Use `--allow-dirty` for iterative development and manual review between batches
