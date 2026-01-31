# Ralph SDLC - Complete Dry Run Test Guide

This guide provides complete commands to test the entire SDLC workflow from BRD to cleanup.

---

## Understanding --yolo Flag

**What is `--yolo`?**
- `--yolo` is a Copilot CLI flag that **auto-approves all MCP tool permissions**
- When you use `./ralph.py --yolo run`, it passes `--yolo` to the `copilot` command
- Perfect for CI/CD pipelines where no human is available to approve permissions

**Example:**
```bash
# Interactive mode (will ask for permission if needed)
./ralph.py run

# Non-interactive mode (auto-approves everything)
./ralph.py --yolo run

# What happens internally:
# copilot --model claude-haiku-4.5 --yolo -p "@ralph-run ..."
```

**When to use --yolo:**
- ✅ CI/CD pipelines
- ✅ Automated scripts
- ✅ When you trust all MCP tools
- ❌ First-time setup (grant permissions manually first)

---

## Phase 0: Prerequisites Check

```bash
# Verify Python
python3 --version

# Verify Copilot CLI
copilot --version

# Verify Git
git --version

# Check if ralph.py works
cd /Users/anshori/Works/ans4175/ralph-copilot
./ralph.py --help
```

**Note:** MCP permissions will be granted naturally when you paste prompts into Copilot (see Phase 4).

---

## Understanding Ralph's Two Modes

**IMPORTANT:** Ralph now has 2 modes to solve the MCP permission problem!

### Mode 1: Prompt Generator (Default - Use This First!)
```bash
./ralph.py tasks-kanban plans/tasks.json
# ↓ Shows formatted prompt to copy-paste into Copilot
# ✅ Solves permission issues!
```

### Mode 2: Execute Mode (After Permissions Granted)
```bash
./ralph.py --execute tasks-kanban plans/tasks.json
# ↓ Runs immediately
# ⚠️ Requires permissions already granted
```

**Rule of thumb:** Use prompt mode until you're sure permissions work, then use execute mode for automation.

---

## Phase 1: Create BRD (Business Requirements Document)

```bash
# Create plans directory if not exists
mkdir -p plans

# Create sample BRD
cat > plans/test-brd.md << 'EOF'
# Test Feature - Business Requirements

## Business Goals
- Validate Ralph's SDLC workflow end-to-end
- Ensure all skills work with project_name resolution
- Test both interactive and --yolo modes

## Market Context
- Target: Developers using Ralph for SDLC automation
- Need: Reliable, repeatable workflow testing
- Value: Confidence in Ralph's capabilities

## High-Level Requirements
1. Create simple test feature
2. Execute tasks automatically
3. Generate implementation reviews
4. Archive completed work

## Success Metrics
- All phases complete without errors
- Tasks visible in Vibe-Kanban
- Implementation log generated
- Cleanup archives tasks properly

## Constraints
- Must work with existing Ralph infrastructure
- No external dependencies required
- Should complete in under 10 minutes
EOF

cat plans/test-brd.md
```

---

## Phase 2: Generate PRD from BRD

```bash
# Generate PRD using ralph-brd-to-prd skill
./ralph.py brd-prd plans/test-brd.md

# Expected output:
# ✅ PRD generated at: plans/generated-prd.md

# View generated PRD
cat plans/generated-prd.md
```

---

## Phase 3: Generate Tasks from PRD

```bash
# Generate tasks JSON using ralph-prd-to-tasks skill
./ralph.py prd-tasks plans/generated-prd.md

# Expected output:
# ✅ Tasks generated at: plans/tasks.json

# View generated tasks
cat plans/tasks.json

# Expected format:
# [
#   {
#     "id": "TASK-001",
#     "title": "...",
#     "description": "...",
#     "dependencies": []
#   },
#   ...
# ]
```

---

## Phase 4: Create Tasks in Vibe-Kanban (NEW WORKFLOW!)

**This is where prompt mode shines!** Ralph generates the prompt, you paste it into Copilot.

```bash
# Generate prompt (default mode)
./ralph.py tasks-kanban plans/test-tasks.json

# Expected output:
# ╭──────────────────────────────────────────────────────────────────────╮
# │ 📋 Copy this prompt into Copilot CLI:                                │
# ╰──────────────────────────────────────────────────────────────────────╯
#
# @ralph-tasks-kanban create tasks from plans/tasks.json in project "ralph-copilot"
#
# ╭──────────────────────────────────────────────────────────────────────╮
# │ 💡 How to use:                                                       │
# │   1. Run: copilot                                                   │
# │   2. Paste the prompt above                                         │
# │   3. Approve permissions if asked                                   │
# ╰──────────────────────────────────────────────────────────────────────╯

# Now follow the instructions:
# 1. Copy the @ralph-tasks-kanban prompt
# 2. Run: copilot
# 3. Paste the prompt
# 4. When asked for permission: type 'y'
copilot
> @ralph-tasks-kanban create tasks from plans/tasks.json in project "ralph-copilot"
[Permission request appears]
> y  # Approve vibe_kanban-list_projects
[Tasks created successfully!]

# OR use execute mode (if permissions already granted)
./ralph.py --execute tasks-kanban plans/tasks.json
```

**Verify tasks were created:**
```bash
# Visit web UI:
```

---

## Phase 5: Run Ready Tasks

**Again, use prompt mode for first-time!**

```bash
# Generate prompt
./ralph.py run

# Copy the output and paste into:
copilot
> [paste @ralph-run prompt]

# OR execute directly (after permissions granted)
./ralph.py --execute run
```

---

## Phase 5b: Run Ready Tasks (YOLO Mode - Non-Interactive)

```bash
# Generate YOLO prompt
./ralph.py --yolo run

# OR execute with YOLO (fully automated)
./ralph.py --execute --yolo run
# 🚀 Starting ready tasks from project: ralph-copilot
# 🤖 Using @ralph-run skill
# [Agent will detect git context, find ready tasks, and start workspace sessions]
# ✅ Run complete
# 💡 View workspace sessions at: vibe-kanban-ui

# Check workspace sessions in web UI
```

---

## Phase 6: Review Completed Tasks

**Note:** This phase requires tasks to be in 'done' status. For testing, manually mark some tasks as done in Vibe-Kanban web UI first.

```bash
# Mark tasks as done (via web UI or copilot)
open vibe-ui

# Review completed tasks (without auto-cleanup)
./ralph.py review --no-cleanup

# Expected output:
# 📋 Reviewing completed tasks from project: ralph-copilot
# 🤖 Using @ralph-task-review skill
# [Agent lists done tasks, generates reviews, appends to docs/implementation-log.md]
# ✅ Review complete
# 💡 Skipping cleanup (--no-cleanup flag)

# View implementation log
cat docs/implementation-log.md

# Expected format:
# ## TASK-001: Task Title
# **Status:** Done | **Reviewed:** 2026-01-31
# 
# ### Implementation Summary
# [150-300 word summary of what was implemented]
# 
# ### Technical Decisions
# - Decision 1...
# 
# ---
```

---

## Phase 6b: Review with Auto-Cleanup (YOLO Mode)

```bash
# Review and cleanup in one command (non-interactive)
./ralph.py --yolo review

# Expected output:
# 🚀 YOLO MODE Reviewing completed tasks from project: ralph-copilot
# [Review phase...]
# ✅ Review complete
# 
# 🧹 Auto-running cleanup...
# [Cleanup phase...]
# ✅ Cleanup complete!
```

---

## Phase 7: Cleanup (Archive Reviewed Tasks)

```bash
# Archive tasks that are both done AND reviewed
./ralph.py cleanup

# Expected output:
# 🧹 Cleaning up reviewed tasks from project: ralph-copilot
# 🤖 Using @ralph-cleanup-agent skill
# [Agent reads implementation-log.md, cross-references with done tasks]
# [Archives tasks to plans/done/]
# [Updates task dependencies]
# [Runs git worktree cleanup]
# [Appends to docs/cleanup-log.md]
# ✅ Cleanup complete!

# View cleanup log
cat docs/cleanup-log.md

# View archived tasks
ls -la plans/done/

# Expected files:
# plans/done/TASK-001.json
# plans/done/TASK-002.json
```

---

## Phase 8: Verify Complete Workflow

```bash
# Check all generated artifacts
echo "=== Generated Files ==="
ls -lh plans/generated-prd.md
ls -lh plans/tasks.json
ls -lh docs/implementation-log.md
ls -lh docs/cleanup-log.md
ls -lh plans/done/

# Verify task count in Vibe-Kanban
copilot -p "Use vibe_kanban-list_tasks with project_id 'a4e53020-bd4b-47b2-ba47-bf196d785b04' to count tasks by status"

# Expected: Some tasks in 'todo', some in 'done', some archived
```

---

## Full Workflow (One-Shot Script)

Here's a complete script to run everything in sequence:

```bash
#!/bin/bash
set -e  # Exit on error

cd /Users/anshori/Works/ans4175/ralph-copilot

echo "=== Phase 1: Create BRD ==="
cat > plans/test-brd.md << 'EOF'
# Test Feature - Business Requirements

## Business Goals
- Validate Ralph SDLC workflow
- Test project_name resolution
- Verify all skills work correctly

## High-Level Requirements
1. Simple test implementation
2. Automated task execution
3. Complete review and cleanup

## Success Metrics
- All phases complete successfully
- Tasks visible in Vibe-Kanban
- Documentation generated
EOF
echo "✓ BRD created"

echo ""
echo "=== Phase 2: Generate PRD ==="
./ralph.py brd-prd plans/test-brd.md
echo "✓ PRD generated"

echo ""
echo "=== Phase 3: Generate Tasks ==="
./ralph.py prd-tasks plans/generated-prd.md
echo "✓ Tasks generated"

echo ""
echo "=== Phase 4: Create Tasks in Kanban ==="
./ralph.py tasks-kanban plans/tasks.json
echo "✓ Tasks created in Vibe-Kanban"

echo ""
echo "=== Phase 5: Run Ready Tasks (YOLO) ==="
./ralph.py --yolo run
echo "✓ Tasks started"

echo ""
echo "⏸️  MANUAL STEP REQUIRED:"
echo "   1. Go to vibe-kanban-ui"
echo "   2. Mark some tasks as 'done'"
echo "   3. Press Enter to continue..."
read

echo ""
echo "=== Phase 6: Review Completed Tasks ==="
./ralph.py --yolo review
echo "✓ Review and cleanup complete"

echo ""
echo "=== Workflow Complete! ==="
echo "Check:"
echo "  - PRD: plans/generated-prd.md"
echo "  - Tasks: plans/tasks.json"
echo "  - Implementation log: docs/implementation-log.md"
echo "  - Cleanup log: docs/cleanup-log.md"
echo "  - Archived tasks: plans/done/"
```

Save as `test-workflow.sh` and run:

```bash
chmod +x test-workflow.sh
./test-workflow.sh
```

---

## Troubleshooting Commands

```bash
# Check config
cat config/ralph.json | grep project_name

# List all Vibe-Kanban projects
copilot -p "Use vibe_kanban-list_projects"

# List tasks in project
copilot -p "Use vibe_kanban-list_tasks with project_id 'a4e53020-bd4b-47b2-ba47-bf196d785b04' and limit 50"

# Check if skills are synced
ls -la .copilot/skills/
ls -la .claude/skills/

# Verify SKILL.md files exist
find skills -name "SKILL.md"

# Re-sync skills if needed
./scripts/sync-skills.sh

# Check ralph.py line count (should be ~737 lines)
wc -l ralph.py

# View recent git commits
git log --oneline -10
```

---

## Clean Up Test Artifacts

```bash
# Remove test files
rm -f plans/test-brd.md
rm -f test-tasks.json

# Keep generated files for reference
# (or remove with: rm plans/generated-prd.md plans/tasks.json)
```

---

## Summary of Commands (Quick Reference)

```bash
# 1. BRD → PRD
./ralph.py brd-prd plans/brd.md

# 2. PRD → Tasks
./ralph.py prd-tasks plans/generated-prd.md

# 3. Tasks → Kanban
./ralph.py tasks-kanban plans/tasks.json

# 4. Run ready tasks
./ralph.py run              # Interactive
./ralph.py --yolo run       # Non-interactive

# 5. Review completed
./ralph.py review           # With auto-cleanup
./ralph.py review --no-cleanup  # Skip cleanup

# 6. Cleanup only
./ralph.py cleanup

# 7. Full YOLO workflow
./ralph.py --yolo run && ./ralph.py --yolo review
```
