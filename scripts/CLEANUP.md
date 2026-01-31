# Git Cleanup: Vibe Kanban Worktree & Branch Removal

## Overview
This document describes tools and processes for cleaning up Vibe Kanban artifacts (worktrees and branches) from the Ralph repository.

## Phase 1: Bash Script (`scripts/cleanup-worktrees.sh`)

### Purpose
Automatically removes all Vibe Kanban-created git worktrees and their associated `vk/*` branches.

### Features
- ✅ Interactive confirmation before deletion (safety prompt)
- ✅ Force mode with `-f` flag for automation
- ✅ Detailed output showing what's being removed
- ✅ Validation checks (won't run outside git repo)
- ✅ Fallback to `--force` if standard removal fails
- ✅ Final verification summary

### Usage

**Interactive (with confirmation):**
```bash
./scripts/cleanup-worktrees.sh
```

**Force mode (no prompts, useful in automation):**
```bash
./scripts/cleanup-worktrees.sh -f
```

### What It Does
1. Lists all active Vibe Kanban worktrees and vk/* branches
2. Prompts for confirmation (unless `-f` is used)
3. Removes worktrees from git tracking
4. Deletes vk/* branches
5. Shows final verification (remaining branches/worktrees)

### Example Output
```
🧹 Ralph Git Cleanup Tool
==========================

📋 Items to be removed:

Worktrees:
  ❌ /private/var/folders/.../vibe-kanban/worktrees/3ce0-update-changelog/ralph-copilot
     Branch: e00e364

Branches:
  ❌ vk/3ce0-update-changelog
  ❌ vk/4c3a-verify-test-ralp

⚠️  Proceed with cleanup? (y/N) 
```

---

## Phase 2: Agent Skill (`prompts/git-ralph-cleanup-agent.txt`)

### Purpose
Copilot CLI agent skill for interactive, intelligent cleanup of Vibe Kanban artifacts.

### Features
- 📋 Validates branch state before deletion
- 🔍 Checks for unmerged commits
- ⚠️ Safety checks and confirmations
- 📝 Detailed logging and progress tracking
- 🎯 Integrates with Ralph workflow

### How Copilot Uses It

#### Load the skill in Copilot CLI:
```bash
# Method 1: Using profile flag (if Copilot CLI supports it)
copilot -p git-ralph-cleanup-agent "Clean up vk/* branches"

# Method 2: Include in context via @-mention (if supported)
@git-ralph-cleanup-agent Help me clean up old Vibe Kanban branches
```

#### The agent will:
1. List all Vibe Kanban worktrees and branches
2. Verify no unmerged commits exist
3. Show what will be deleted
4. Ask for confirmation
5. Execute cleanup
6. Verify success
7. Log results to progress.txt

### Agent Workflow

**Example interaction:**
```
You: Can you clean up the old Vibe Kanban worktrees and branches?

Agent: 
I found 4 vibe-kanban worktrees and 4 vk/* branches.

Checking for unmerged commits...
✅ vk/3ce0-update-changelog: All commits merged to chore/refine
✅ vk/4c3a-verify-test-ralp: All commits merged to chore/refine
✅ vk/bfd3-update-ralph-py: All commits merged to chore/refine
✅ vk/f5be-refine-readme: All commits merged to chore/refine

Ready to cleanup. Proceed? (y/n)

[After confirmation]

✨ Cleanup Report
- Worktrees removed: 4
- Branches deleted: 4
- Status: CLEAN
```

---

## When to Use Each

| Scenario | Tool | Reason |
|----------|------|--------|
| Manual one-time cleanup | Bash script | Quick, transparent, no setup |
| Automated cleanup (CI) | Bash script with `-f` | Simple flag for automation |
| Interactive review | Agent skill | Validates commits, confirms before deleting |
| Integrated workflow | Agent skill | Logs to progress.txt, fits Ralph pattern |

---

## Safety Considerations

### Before Running Cleanup
1. **Verify current branch**: `git branch`
2. **Check commits on main**: `git log --oneline main -5`
3. **No uncommitted changes**: `git status` should show clean working tree

### Branch Safety
- vk/* branches that are NOT merged will show in `git log <main>..<vk-branch>`
- Bash script uses `-D` flag which requires all commits to be merged (prevents accidental loss)
- Agent skill explicitly checks for unmerged commits before deletion

### Worktree Safety
- Worktrees with uncommitted changes are locked (can't be removed)
- Bash script uses `--force` fallback only if standard removal fails
- Agent skill will report locked worktrees and ask for guidance

---

## Troubleshooting

### Script can't remove a worktree
```bash
# The worktree is locked (has uncommitted changes)
# Option 1: Force removal (loses uncommitted work)
./scripts/cleanup-worktrees.sh -f

# Option 2: Manual cleanup
git worktree remove <path> --force
cd <path> && git status  # check what's uncommitted first
```

### Can't delete a branch
```bash
# Branch has unmerged commits
git log main..<branch>  # see what's not merged

# Option 1: Merge the branch first
git merge <branch>

# Option 2: Force delete (loses commits)
git branch -D <branch>
```

### Verify cleanup was successful
```bash
# No vibe-kanban worktrees should exist
git worktree list | grep vibe-kanban

# No vk/* branches should exist
git branch | grep vk/

# Main working branch should be unchanged
git branch -v
```

---

## Integration with Ralph

### Cleanup After Features Complete
Add to Ralph's post-feature-complete workflow:
```bash
# After all features pass and main merges complete
./scripts/cleanup-worktrees.sh -f
git log --oneline -5  # verify clean state
```

### Future Vibe Kanban Runs
Each new Vibe Kanban automation will create fresh vk/* branches and worktrees.
Run cleanup script after automation completes to maintain clean state.

---

## Files
- **Script:** `scripts/cleanup-worktrees.sh`
- **Skill:** `prompts/git-ralph-cleanup-agent.txt`
- **Docs:** `scripts/CLEANUP.md` (this file)
