# Ralph Usage Guide

Complete reference for using Ralph daily - from business idea to implemented features.

---

## Overview

Ralph orchestrates your SDLC through 6 phases:

```
BRD → PRD → Tasks → Execute → Review → Cleanup
```

Each phase builds on the previous, transforming documents into executable work and maintaining audit trails.

---

## Understanding Ralph's Two Modes

Ralph operates in two modes to fit different workflows:

### 📋 Prompt Mode (Default - Recommended)

**What it does:** Generates formatted prompts for you to paste into Copilot CLI

```bash
./ralph.py tasks-kanban plans/tasks.json

# Shows:
# ╭──────────────────────────────────────────────╮
# │ 📋 Copy this prompt into Copilot CLI:       │
# ╰──────────────────────────────────────────────╯
# @ralph-tasks-kanban create tasks from...
```

**When to use:**
- ✅ First-time users (solves permission issues!)
- ✅ Learning how skills work
- ✅ Want to review before execution
- ✅ Debugging or customizing prompts

**How it works:**
1. Ralph generates the prompt
2. You copy and paste into `copilot`
3. Copilot grants permissions naturally
4. Skills execute with full MCP access

### ⚡ Execute Mode (For Automation)

**What it does:** Runs commands immediately (requires pre-granted permissions)

```bash
./ralph.py --execute tasks-kanban plans/tasks.json
# Runs immediately
```

**When to use:**
- ✅ After initial setup (permissions already granted)
- ✅ Automation scripts
- ✅ CI/CD pipelines
- ✅ Repeated tasks

**Add `--yolo` for non-interactive:**
```bash
./ralph.py --execute --yolo run
# Auto-approves all prompts
```

---

## The 6-Phase Workflow

### Phase 1: BRD → PRD

Transform business requirements into technical product requirements.

#### Input

Create a Business Requirements Document (BRD) in markdown:

**File:** `plans/my-product-brd.md`

```markdown
# My Product - Business Requirements

## Business Goals
- Help users track their daily tasks
- Simple, fast, no login required

## Target Users
- Busy professionals
- Students
- Anyone needing quick task tracking

## Key Features
1. Add tasks quickly
2. Mark tasks complete
3. View task history

## Success Metrics
- 100 users in first month
- 80% return rate
```

#### Command

```bash
./ralph.py brd plans/my-product-brd.md
```

#### Output

**File:** `plans/generated-prd.md`

Contains:
- Product Overview
- Jobs To Be Done (JTBD)
- Acceptance Criteria
- User Flows
- Page Flows
- Technical Constraints
- Success Metrics

#### What Happens

1. Ralph invokes `@ralph-brd-to-prd` skill
2. AI reads your BRD
3. Generates structured PRD with technical details
4. Saves to `plans/generated-prd.md`

**Note:** This phase doesn't need MCP - works in either mode.

---

### Phase 2: PRD → Tasks

Break down the PRD into atomic, executable tasks with dependencies.

#### Input

The PRD from Phase 1: `plans/generated-prd.md`

#### Command

```bash
./ralph.py prd plans/generated-prd.md
```

#### Output

**File:** `plans/tasks.json`

Example structure:
```json
[
  {
    "id": "TASK-001",
    "title": "Setup project structure",
    "description": "Initialize project with basic structure",
    "status": "todo",
    "priority": 1,
    "estimated_hours": 2,
    "dependencies": [],
    "acceptance_criteria": [
      "Project structure exists",
      "README.md created",
      "Git initialized"
    ]
  },
  {
    "id": "TASK-002",
    "title": "Create task model",
    "description": "Define task data model",
    "status": "todo",
    "priority": 2,
    "estimated_hours": 3,
    "dependencies": ["TASK-001"],
    "acceptance_criteria": [
      "Task model defined",
      "Unit tests pass"
    ]
  }
]
```

#### What Happens

1. Ralph invokes `@ralph-prd-to-tasks` skill
2. AI analyzes PRD sections
3. Breaks down into atomic tasks
4. Identifies dependencies
5. Assigns priorities
6. Generates `tasks.json`

**Note:** This phase doesn't need MCP - works in either mode.

---

### Phase 3: Tasks → Vibe-Kanban

Create tasks in Vibe-Kanban project management system.

#### Input

The tasks from Phase 2: `plans/tasks.json`

#### Command (Prompt Mode - Recommended)

```bash
# 1. Generate prompt
./ralph.py tasks-kanban plans/tasks.json

# 2. Copy the output

# 3. Paste into Copilot
copilot
> [paste @ralph-tasks-kanban prompt]
> y  # Approve permissions if asked
```

#### Command (Execute Mode)

```bash
./ralph.py --execute tasks-kanban plans/tasks.json
```

#### What Happens

1. Resolves project name to ID (`vibe_kanban-list_projects`)
2. Reads and validates `tasks.json`
3. Creates each task via `vibe_kanban-create_task` MCP
4. Links dependencies
5. Reports results

#### Output

- Tasks appear in Vibe-Kanban dashboard
- Start UI: `npm run vibe-kanban` (opens at http://localhost:3000)

#### Verification

```bash
# List tasks via Copilot
copilot -p "Use vibe_kanban-list_tasks to show tasks in 'your-project'"
```

---

### Phase 4: Run (Execute Ready Tasks)

Start workspace sessions for tasks with no blocking dependencies.

#### Command (Prompt Mode - Recommended)

```bash
# 1. Generate prompt
./ralph.py run

# 2. Copy and paste into Copilot
copilot
> [paste @ralph-run prompt]
```

#### Command (Execute Mode)

```bash
./ralph.py --execute run
```

#### Command (YOLO Mode - CI/CD)

```bash
./ralph.py --execute --yolo run
```

#### What Happens

1. Resolves project name to ID
2. Detects current git branch
3. Fetches all tasks from Vibe-Kanban (live status!)
4. Filters for:
   - `status='todo'`
   - No blocking dependencies
   - Valid Ralph task ID format (`TASK-XXX:`)
5. Starts workspace sessions via `vibe_kanban-start_workspace_session`
6. Reports started/failed sessions

**IMPORTANT:** Always reads from Vibe-Kanban (not tasks.json) - Vibe-Kanban is the source of truth for task status.

#### Progressive Execution

You can call `ralph run` multiple times as dependencies complete:

```bash
# First run - starts TASK-001, TASK-002 (no dependencies)
./ralph.py run

# ... tasks complete ...

# Second run - starts TASK-003 (depends on TASK-001, now done)
./ralph.py run

# Repeats until all tasks complete
```

#### Task Format Filtering

Ralph only processes tasks matching the pattern: `TASK-\d{3}:`

**Valid:**
- `TASK-001: Setup project`
- `TASK-099: Add tests`

**Ignored:**
- `Manual task` (no TASK- prefix)
- `TASK-A: Invalid` (not 3 digits)

This prevents Ralph from starting manual tasks in your Kanban board.

---

### Phase 5: Review (Document Completed Work)

Generate implementation summaries for completed tasks.

#### Command (Prompt Mode - Recommended)

```bash
# 1. Generate prompt
./ralph.py review

# 2. Copy and paste into Copilot
copilot
> [paste @ralph-task-review prompt]
```

#### Command (Execute Mode)

```bash
./ralph.py --execute review
```

#### What Happens

1. Resolves project name to ID
2. Fetches tasks with `status='done'`
3. Filters for valid Ralph task IDs
4. Invokes `@ralph-task-review` skill for each
5. Generates implementation summary (150-300 words)
6. **Appends** to `docs/implementation-log.md`
7. Optionally triggers cleanup (if `--no-cleanup` not set)

#### Output

**File:** `docs/implementation-log.md`

Example entry:
```markdown
## TASK-001: Setup project structure

**Date:** 2026-02-01
**Status:** Completed

### Implementation Summary

Initialized project with standard directory structure including src/, 
tests/, docs/, and config/ directories. Set up Git repository with 
.gitignore for common artifacts. Created README.md with project 
overview and basic installation instructions.

### Technical Decisions

- Used standard Node.js project structure
- Chose Jest for testing framework
- Configured ESLint for code quality

### Tests Added

- Project structure validation test
- README existence check

### Documentation Updates

- Created README.md
- Added LICENSE file

### Challenges Overcome

None - straightforward setup task.
```

#### Verification

```bash
# View implementation log
cat docs/implementation-log.md
```

---

### Phase 6: Cleanup (Archive Completed Work)

Archive reviewed tasks, delete git worktrees, update Kanban, and maintain changelog.

#### Command (Prompt Mode - Recommended)

```bash
# 1. Generate prompt
./ralph.py cleanup

# 2. Copy and paste into Copilot
copilot
> [paste @ralph-cleanup-agent prompt]
```

#### Command (Execute Mode)

```bash
./ralph.py --execute cleanup
```

#### What Happens

1. Resolves project name to ID
2. Reads `docs/implementation-log.md` for reviewed task IDs
3. Cross-references with tasks in `status='done'`
4. For each task:
   - Archives to `archive/tasks/{TASK-ID}/README.md`
   - Deletes git worktree (via `scripts/cleanup-worktrees.sh`)
   - Deletes from Vibe-Kanban (with double safety check)
5. Updates `CHANGELOG.md` with deletion audit
6. **Appends** to `docs/cleanup-log.md`
7. Reports summary

#### Safety Checks

- Only archives tasks that are BOTH reviewed AND done
- Double verification before deletion (implementation-log + status)
- Preserves data in archive before deletion
- Logs all operations for audit trail

#### Output Files

**File:** `archive/tasks/TASK-001/README.md`
```markdown
# TASK-001: Setup project structure

Archived task details and implementation summary
```

**File:** `docs/cleanup-log.md`
```markdown
## Cleanup - 2026-02-01

### Tasks Archived
- TASK-001: Setup project structure
- TASK-002: Create task model

### Git Worktrees Deleted
- vibe-kanban-TASK-001 (deleted)
- vibe-kanban-TASK-002 (deleted)

### Kanban Tasks Deleted
- TASK-001 (deleted from Vibe-Kanban)
- TASK-002 (deleted from Vibe-Kanban)

### Summary
Archived 2 tasks, deleted 2 worktrees, deleted 2 Kanban tasks
```

**File:** `CHANGELOG.md` (appended)
```markdown
## [2026-02-01] - Task Cleanup

### Archived
- TASK-001: Setup project structure (deleted from Vibe-Kanban)
- TASK-002: Create task model (deleted from Vibe-Kanban)
```

---

## Complete Workflow Examples

### Example 1: First-Time Workflow (Prompt Mode)

```bash
# ────────────────────────────────────────────────────────
# Phase 1: BRD → PRD (No MCP needed)
# ────────────────────────────────────────────────────────
./ralph.py brd plans/todo-app-brd.md
# Output: plans/generated-prd.md

# ────────────────────────────────────────────────────────
# Phase 2: PRD → Tasks (No MCP needed)
# ────────────────────────────────────────────────────────
./ralph.py prd plans/generated-prd.md
# Output: plans/tasks.json

# ────────────────────────────────────────────────────────
# Phase 3: Tasks → Kanban (Prompt mode!)
# ────────────────────────────────────────────────────────
./ralph.py tasks-kanban plans/tasks.json
# Copy the prompt, then:
copilot
> [paste prompt]
> y  # Approve permissions

# ────────────────────────────────────────────────────────
# Phase 4: Run ready tasks (Prompt mode!)
# ────────────────────────────────────────────────────────
./ralph.py run
# Copy the prompt, then:
copilot
> [paste prompt]

# ... work happens in Vibe-Kanban workspaces ...

# ────────────────────────────────────────────────────────
# Phase 5: Review completed (Prompt mode!)
# ────────────────────────────────────────────────────────
./ralph.py review
# Copy the prompt, then:
copilot
> [paste prompt]

# ────────────────────────────────────────────────────────
# Phase 6: Cleanup (Prompt mode!)
# ────────────────────────────────────────────────────────
./ralph.py cleanup
# Copy the prompt, then:
copilot
> [paste prompt]
```

### Example 2: Automation Workflow (Execute Mode)

```bash
# Requires permissions already granted!

./ralph.py brd plans/todo-app-brd.md
./ralph.py prd plans/generated-prd.md
./ralph.py --execute tasks-kanban plans/tasks.json
./ralph.py --execute run

# ... wait for tasks to complete ...

./ralph.py --execute review
./ralph.py --execute cleanup
```

### Example 3: CI/CD Pipeline (YOLO Mode)

```bash
#!/bin/bash
# ci-pipeline.sh

set -e

# Generate specs
./ralph.py brd plans/feature-brd.md
./ralph.py prd plans/generated-prd.md

# Execute with YOLO (auto-approve)
./ralph.py --execute --yolo tasks-kanban plans/tasks.json
./ralph.py --execute --yolo run

# Poll for completion (implement your own logic)
# ...

# Review and cleanup
./ralph.py --execute --yolo review
./ralph.py --execute --yolo cleanup
```

---

## Common Patterns

### Pattern 1: Incremental Development

```bash
# Start with MVP tasks
./ralph.py run  # Starts TASK-001, TASK-002, TASK-003

# Wait for completion, then:
./ralph.py run  # Starts TASK-004 (depends on TASK-001)

# Repeat as dependencies clear
```

### Pattern 2: Parallel Execution

```bash
# Ralph starts all ready tasks in parallel
./ralph.py run

# Multiple workspace sessions run simultaneously
# Each in its own git worktree
```

### Pattern 3: Review Without Cleanup

```bash
# Review but don't cleanup yet
./ralph.py --execute review --no-cleanup

# Later, when ready:
./ralph.py --execute cleanup
```

---

## Troubleshooting

### "Project not found"

**Problem:** Ralph can't find your Vibe-Kanban project

**Solution:**
```bash
# List available projects
copilot -p "Use vibe_kanban-list_projects to show all projects"

# Update config/ralph.json with exact project name
```

### "Permission denied" for MCP tools

**Problem:** MCP permissions not granted

**Solution:**
```bash
# Use prompt mode (grants permissions naturally)
./ralph.py tasks-kanban plans/tasks.json
# Then paste into copilot and approve
```

### "No tasks ready to run"

**Problem:** All tasks have blocking dependencies

**Solution:**
```bash
# Check task status in Vibe-Kanban
copilot -p "Use vibe_kanban-list_tasks to show tasks in 'your-project'"

# Mark dependency tasks as done manually if needed
```

### Skills not loading

**Problem:** Copilot can't find Ralph skills

**Solution:**
```bash
# Re-sync skills
./scripts/sync-skills.sh

# Verify
ls -la .copilot/skills/
```

---

## Configuration Reference

### config/ralph.json

```json
{
  "project_name": "ralph-sdlc-wrapper",
  "version": "0.1.0",
  "vibe_kanban": {
    "project_name": "your-project-name",  // ← SET THIS
    "executor": "COPILOT",                // COPILOT or CLAUDE_CODE
    "model": "claude-sonnet-4.5"          // Default model
  },
  "repo_config": {
    "base_branch": "main",               // Auto-detected by ralph.py
    "setup_script": "",                  // Optional setup commands
    "cleanup_script": "",                // Optional cleanup commands
    "dev_server_script": ""              // Optional dev server start
  },
  "paths": {
    "brd": "plans/brd.md",
    "prd": "plans/generated-prd.md",
    "tasks": "plans/tasks.json",
    "implementation_log": "docs/implementation-log.md",
    "cleanup_log": "docs/cleanup-log.md",
    "archive_dir": "archive/tasks"
  }
}
```

---

## Next Steps

- **[TEST-GUIDE.md](TEST-GUIDE.md)** - Validate your setup works correctly
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Understand how Ralph works internally
- **[docs/RFC.md](docs/RFC.md)** - Learn why Ralph was built this way
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Help improve Ralph

---

## Quick Reference

| Command | What It Does | Needs MCP? |
|---------|--------------|------------|
| `ralph brd <file>` | BRD → PRD | No |
| `ralph prd <file>` | PRD → Tasks | No |
| `ralph tasks-kanban <file>` | Tasks → Kanban | Yes |
| `ralph run` | Execute ready tasks | Yes |
| `ralph review` | Document completed work | Yes |
| `ralph cleanup` | Archive + cleanup | Yes |

**Add `--execute` for immediate execution (requires pre-granted permissions)**
**Add `--yolo` with `--execute` for non-interactive CI/CD mode**

---

**Happy developing with Ralph!** 🚀
