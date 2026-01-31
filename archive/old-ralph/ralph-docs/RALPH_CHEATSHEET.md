# Ralph.py Cheat Sheet

## Quick Commands

```bash
# Single run (replaces ralph-once.sh)
./ralph.py --once --allow-profile safe

# Loop mode (replaces ralph.sh)
./ralph.py --allow-profile safe --max-iterations 10

# Iterative workflow (RECOMMENDED)
./ralph.py --allow-profile safe --allow-dirty --max-iterations 5

# Run without hesitation (yolo mode)
./ralph.py --allow-profile yolo --max-iterations 10
```

## All Flags Reference

| Flag | Description | Example |
|------|-------------|---------|
| `--prd <path>` | Path to PRD JSON | `--prd plans/backend.json` |
| `--progress <path>` | Path to progress log | `--progress my-progress.txt` |
| `--state <path>` | Path to state file | `--state .ralph/my-state.json` |
| `--once` | Run one iteration | `--once` |
| `--max-iterations <N>` | Max iterations | `--max-iterations 20` |
| `--allow-profile <name>` | Permission profile | `--allow-profile safe` |
| `--allow-dirty` | Allow dirty repo | `--allow-dirty` |
| `--prompt-prefix <path>` | Custom prompt file | `--prompt-prefix prompts/style.txt` |
| `--model <name>` | Copilot model | `--model claude-sonnet-4.5` |
| `--allow-tool <spec>` | Allow specific tool | `--allow-tool 'shell(docker:*)'` |
| `--deny-tool <spec>` | Deny specific tool | `--deny-tool 'shell(rm)'` |
| `--copilot-bin <path>` | Copilot binary path | `--copilot-bin /usr/local/bin/copilot` |
| `--sleep <seconds>` | Delay between iterations | `--sleep 1.0` |
| `--completion-token <str>` | Completion signal | `--completion-token DONE` |

## Permission Profiles

| Profile | Allows | Use Case |
|---------|--------|----------|
| `safe` | write, pnpm, git | Most development work |
| `dev` | all tools | Full access (use carefully) |
| `locked` | write only | Maximum safety, no commands |
| `yolo` | `--yolo` mode | Run without hesitation (skip confirmations) |

## Common Workflows

### 1. Quick Fix (Once Mode)
```bash
./ralph.py --once --allow-profile safe
```

### 2. Feature Development (Loop)
```bash
./ralph.py --allow-profile safe --max-iterations 10
```

### 3. Iterative Review Cycle
```bash
# Run 3 stories
./ralph.py --allow-profile safe --allow-dirty --max-iterations 3

# Review
git diff
cat progress.txt | tail -50

# Continue
./ralph.py --allow-profile safe --allow-dirty --max-iterations 3
```

### 4. Multiple PRDs
```bash
# Monday: Architecture
./ralph.py --prd plans/arch.json --allow-profile safe --allow-dirty --max-iterations 5

# Tuesday: Features
./ralph.py --prd plans/features.json --allow-profile safe --allow-dirty --max-iterations 5
```

### 5. Custom Coding Style
```bash
# Create style guide
cat > prompts/style.txt << 'EOF'
- Use TypeScript strict mode
- Add JSDoc to exports
- Follow ESLint rules
EOF

# Run with style
./ralph.py --prompt-prefix prompts/style.txt --allow-profile safe --max-iterations 10
```

## Debugging

### Check Progress
```bash
# View recent work
tail -100 progress.txt

# Search for errors
grep -i "error\|fail" progress.txt

# View state
cat .ralph/state.json
```

### Resume After Failure
```bash
# Fix issue manually, then mark story as passing in PRD
vim plans/prd.json  # set "passes": true

# Continue
./ralph.py --allow-profile safe --allow-dirty --max-iterations 10
```

## File Outputs

| File | Purpose |
|------|---------|
| `progress.txt` | Append-only log of all iterations |
| `.ralph/state.json` | Run count, timestamps |
| `plans/prd.json` | Updated with `passes: true` flags |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (all stories complete) |
| 1 | Max iterations reached |
| 2 | Invalid arguments or dirty repo (without `--allow-dirty`) |
| 3 | Story disappeared from PRD |
| 5 | Repo not clean after commit |

## Environment Variables

```bash
# Set default model
export MODEL="claude-sonnet-4.5"
./ralph.py --allow-profile safe --max-iterations 10

# Custom copilot binary
export COPILOT_BIN="/custom/path/copilot"
./ralph.py --copilot-bin "$COPILOT_BIN" --allow-profile safe
```

## Tips

✅ **DO:**
- Use `--once` for quick single tasks
- Use `--allow-dirty` for iterative development
- Run small batches (3-5 iterations) with review
- Add tests to all PRD stories
- Use `--prompt-prefix` for coding standards

❌ **DON'T:**
- Run 50 iterations unattended
- Mix unrelated features in one PRD
- Skip tests (ralph won't mark story as passing)
- Ignore progress.txt logs

## Quick Start

```bash
# First time? Start here:
./ralph.py --once --allow-profile safe

# Check what happened:
cat progress.txt
git log -1

# Ready for more? Go iterative:
./ralph.py --allow-profile safe --allow-dirty --max-iterations 5
```

## Help

```bash
# Full help
./ralph.py --help

# Documentation
cat RALPH.md
cat RALPH_EXAMPLES.md
cat RALPH_FEATURES.md
```
