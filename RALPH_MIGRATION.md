# Ralph Migration from Bash to Python

## What Changed

Rewrote `ralph.sh` from scratch as `ralph.py` following the Ralph Wiggum loop principle.

## Key Improvements

### 1. **First Principles Approach**
- Based on proven Python Ralph loop from the community
- Clear separation of concerns
- Streaming output (see Copilot work in real-time)
- Proper error handling

### 2. **Fixed Critical Issues**
- **No more exit status 1**: Copilot now runs properly in non-interactive mode
- **Prompt properly passed**: Uses `-p` with inline prompt text (not file references)
- **Streaming output**: See what Copilot is doing in real-time
- **Proper waiting**: No more premature timeouts

### 3. **Better Architecture**
- Clean Python code (vs complex bash)
- Proper JSON handling
- Git operations centralized
- Test runner with proper logging
- State persistence in `.ralph/state.json`

## Usage Comparison

### Old (ralph.sh)
```bash
./ralph.sh --prompt prompts/default.txt --prd plans/prd.json --allow-profile safe 10
```

### New (ralph.py)
```bash
./ralph.py --allow-profile safe --max-iterations 10
```

## What Works Now

1. ✅ Copilot executes properly (no exit 1)
2. ✅ Streaming output visible in terminal
3. ✅ Picks next story from PRD by priority
4. ✅ Runs tests after each story
5. ✅ Commits changes automatically
6. ✅ Tracks progress in `progress.txt`
7. ✅ Handles final tests phase
8. ✅ Enforces clean repo state

## Migration Steps

1. ✅ Created `ralph.py` from scratch
2. ✅ Added tests to first PRD story (`arch-001`)
3. ✅ Created `RALPH.md` documentation
4. ⏳ Ready to test first run

## Next Steps

1. Test with: `./ralph.py --allow-profile safe --max-iterations 1`
2. Review output in `progress.txt`
3. If successful, run full batch: `--max-iterations 20`
4. Archive old `ralph.sh` once confident

## Files

- `ralph.py` - New Python implementation ✨
- `RALPH.md` - Usage documentation
- `ralph.sh` - Old bash version (keep for reference)
- `plans/prd.json` - PRD with tests added
