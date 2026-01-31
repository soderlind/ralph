# Deprecated Scripts

## Removed Files

The following bash scripts have been **removed** and replaced by `ralph.py`:

- `ralph.sh` - Old loop implementation (buggy, complex bash)
- `ralph-once.sh` - Single iteration runner (no longer needed)

## Why Removed?

### ralph.sh Issues:
- ❌ Exit status 1 bug (copilot not executing properly)
- ❌ No streaming output
- ❌ Complex bash logic hard to maintain
- ❌ Static prompt from file (not flexible)
- ❌ No story-based iteration
- ❌ No state persistence

### ralph-once.sh Issues:
- ❌ Same bugs as ralph.sh
- ❌ No longer needed (ralph.py with `--max-iterations 1` does the same)

## Replacements

### Old: ralph.sh
```bash
./ralph.sh --prompt prompts/default.txt --prd plans/prd.json --allow-profile safe 10
```

### New: ralph.py
```bash
# Loop mode (same as old ralph.sh but better)
./ralph.py --allow-profile safe --max-iterations 10

# With custom prompt prefix
./ralph.py --prompt-prefix prompts/default.txt --allow-profile safe --max-iterations 10
```

### Old: ralph-once.sh
```bash
./ralph-once.sh --prompt prompts/task.txt --allow-profile safe
```

### New: ralph.py (single iteration)
```bash
# Using --once flag (cleaner)
./ralph.py --once --allow-profile safe

# Or use --max-iterations 1
./ralph.py --allow-profile safe --max-iterations 1

# With custom prompt prefix
./ralph.py --once --prompt-prefix prompts/task.txt --allow-profile safe
```

## Migration Complete

✅ All functionality preserved in ralph.py
✅ New features added (--allow-dirty, --prompt-prefix)
✅ Fixed all bugs from bash versions
✅ Follows proven Ralph Wiggum loop principle
✅ Comprehensive documentation available

## Need the Old Scripts?

They're still in git history:
```bash
# View old ralph.sh
git log --all --full-history -- ralph.sh

# Restore if needed (not recommended)
git checkout <commit-hash> -- ralph.sh
```

## Documentation

See:
- `RALPH.md` - Main usage guide
- `RALPH_FEATURES.md` - Feature comparison
- `RALPH_EXAMPLES.md` - Real-world examples
- `RALPH_MIGRATION.md` - Migration notes

## Quick Reference: ralph-once.sh → ralph.py

| Old Command | New Command |
|-------------|-------------|
| `./ralph-once.sh --allow-profile safe` | `./ralph.py --once --allow-profile safe` |
| `./ralph-once.sh --prompt prompts/task.txt --allow-profile safe` | `./ralph.py --once --prompt-prefix prompts/task.txt --allow-profile safe` |
| `./ralph-once.sh --prd plans/prd.json --allow-profile safe` | `./ralph.py --once --prd plans/prd.json --allow-profile safe` |
| `./ralph-once.sh --allow-profile dev` | `./ralph.py --once --allow-profile dev` |

## Quick Reference: ralph.sh → ralph.py

| Old Command | New Command |
|-------------|-------------|
| `./ralph.sh --prompt prompts/default.txt --prd plans/prd.json --allow-profile safe 10` | `./ralph.py --prompt-prefix prompts/default.txt --allow-profile safe --max-iterations 10` |
| `./ralph.sh --prd plans/prd.json --allow-profile safe 5` | `./ralph.py --allow-profile safe --max-iterations 5` |
| `./ralph.sh --prd plans/prd.json --allow-profile dev 20` | `./ralph.py --allow-profile dev --max-iterations 20` |

## Key Improvements Over Old Scripts

### ralph-once.sh Issues → ralph.py Solutions
- ❌ No state tracking → ✅ `.ralph/state.json` persists runs
- ❌ No progress log → ✅ Appends to `progress.txt`
- ❌ Exit 1 bug → ✅ Fixed prompt passing
- ❌ No dirty repo support → ✅ `--allow-dirty` flag
- ❌ Verbose flag naming → ✅ `--once` is clearer

### ralph.sh Issues → ralph.py Solutions
- ❌ No streaming output → ✅ See Copilot work live
- ❌ Complex bash logic → ✅ Clean Python code
- ❌ Static prompts from file → ✅ Dynamic prompts from PRD
- ❌ No story iteration → ✅ One story per commit
- ❌ No state between runs → ✅ State persistence

## Why --once is Better Than --max-iterations 1

```bash
# Old way (works but verbose)
./ralph.py --max-iterations 1 --allow-profile safe

# New way (clear intent)
./ralph.py --once --allow-profile safe

# Both do the same thing, but --once is:
# - Clearer intent (single run vs loop of 1)
# - Shorter to type
# - Direct replacement for ralph-once.sh
```
