# Ralph.py Feature Comparison

## Questions Answered

### ✅ Q1: Can ralph.py receive custom paths for prd.json and prompts?

**Answer: YES (with improvements)**

```bash
# Custom PRD path
./ralph.py --prd plans/my-custom-prd.json --allow-profile safe

# Custom prompt prefix (NEW feature)
./ralph.py --prompt-prefix prompts/coding-style.txt --allow-profile safe

# Custom progress log
./ralph.py --progress my-progress.txt --allow-profile safe

# Custom state file
./ralph.py --state .ralph/my-state.json --allow-profile safe
```

**How it works:**
- PRD path is fully customizable via `--prd`
- No separate prompts.txt file - prompts are built dynamically from PRD stories
- NEW: `--prompt-prefix` for adding custom instructions to every story
- All file paths are configurable

### ✅ Q2: What is clean repo enforcement?

**Answer: Safety feature to prevent working on dirty repo (now optional)**

**Default Behavior (Strict):**
```bash
# Requires clean git state to start
./ralph.py --allow-profile safe --max-iterations 10
# Error if uncommitted changes exist
```

**New Behavior (Flexible):**
```bash
# Allow starting with uncommitted changes
./ralph.py --allow-profile safe --allow-dirty --max-iterations 10
# Ralph will commit at each story completion
```

**Why it exists:**
- Prevents accidental conflicts
- Ensures each story starts from known state
- Makes rollback easier (each story = 1 commit)

**When to use `--allow-dirty`:**
- Iterative development
- Manual review between batches
- Gradual commits preferred over big commits

### ✅ Q3: Can you run ralph iteratively with another plan and commit gradually?

**Answer: YES! (with --allow-dirty flag)**

## Iterative Workflow Examples

### Example 1: Multiple Plans, Same Repo
```bash
# Monday: Run architecture PRD
./ralph.py --prd plans/arch.json --allow-profile safe --allow-dirty --max-iterations 5

# Review changes
git diff

# Tuesday: Run features PRD (continues from current state)
./ralph.py --prd plans/features.json --allow-profile safe --allow-dirty --max-iterations 5

# Wednesday: Run polish PRD
./ralph.py --prd plans/polish.json --allow-profile safe --allow-dirty --max-iterations 5

# End of week: Final review and push
git log --oneline -10
git push origin feature/new-stuff
```

### Example 2: Batch + Review Cycle
```bash
# Run 3 iterations
./ralph.py --allow-profile safe --allow-dirty --max-iterations 3

# Review what changed
git diff
cat progress.txt | tail -50

# Make manual adjustments
vim app/components/NewFeature.tsx

# Run 3 more iterations (ralph continues from current state)
./ralph.py --allow-profile safe --allow-dirty --max-iterations 3

# Repeat until satisfied
```

### Example 3: Single Plan, Gradual Commits
```bash
# Run 1 story at a time, review each commit
./ralph.py --allow-profile safe --max-iterations 1

# Review the commit
git show HEAD

# Continue with next story
./ralph.py --allow-profile safe --max-iterations 1

# Review again
git show HEAD

# Etc.
```

## Feature Matrix

| Feature | ralph.sh (old) | ralph.py (new) |
|---------|---------------|----------------|
| Custom PRD path | ✅ | ✅ |
| Custom prompts file | ✅ | ❌ (uses dynamic prompts) |
| Prompt prefix | ❌ | ✅ NEW |
| Allow dirty repo | ❌ | ✅ NEW |
| Streaming output | ❌ | ✅ |
| Progress tracking | ✅ | ✅ |
| State persistence | ❌ | ✅ |
| Story-based iteration | ❌ | ✅ |
| Test enforcement | ✅ | ✅ |
| Auto-commit per story | ❌ | ✅ |
| Multiple PRDs | ❌ | ✅ |
| Permission profiles | ✅ | ✅ |
| Exit status 1 bug | 🐛 | ✅ Fixed |

## Migration Benefits

### 1. **Flexibility**
- Run multiple PRDs on same repo
- Iterate gradually with review
- Switch between plans easily

### 2. **Safety**
- Each story = 1 commit (easy rollback)
- Optional dirty repo mode for gradual work
- Still enforces clean state at completion

### 3. **Visibility**
- Streaming output (see Copilot work live)
- Better progress tracking
- State file shows history

### 4. **Reliability**
- No more exit status 1 errors
- Proper prompt passing to Copilot
- Better error handling

## Best Practices

### ✅ DO:
- Use `--allow-dirty` for iterative development
- Run small batches (3-5 iterations) with review
- Use different PRDs for different features
- Add custom prompt prefix for coding standards
- Review `progress.txt` regularly

### ❌ DON'T:
- Run 50 iterations unattended without `--allow-dirty`
- Mix unrelated features in same PRD
- Skip adding tests to stories
- Ignore test failures in progress log

## Summary

**YES to all your questions:**
1. ✅ Custom paths supported (PRD, progress, state, prompt-prefix)
2. ✅ Clean repo enforcement is optional (`--allow-dirty`)
3. ✅ Iterative work with multiple plans fully supported

**Key takeaway:** `--allow-dirty` unlocks the iterative workflow you want!
