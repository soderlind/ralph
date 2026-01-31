---
name: ralph-cleanup-agent
description: "Archive reviewed tasks, clean up workspace artifacts, and maintain project documentation"
---

# ralph-cleanup-agent Skill

**Agentic skill for archiving reviewed tasks and cleaning up workspace artifacts.**

## Purpose

Archive tasks that have been reviewed (present in implementation-log.md) and are in 'done' status. Move artifacts, update task metadata, and maintain CHANGELOG.

## When to Use

Invoked by `ralph.py cleanup` command or automatically after `ralph.py review` (unless --no-cleanup flag set).

## Inputs Required

- **project_name**: Human-readable project name (e.g., "ralph-copilot", "my-project")
- **archive_path**: Optional custom archive location (default: archive/)

## Instructions for Agent

### Step 0: Resolve Project Name to ID

1. Use `vibe_kanban-list_projects` MCP tool to get all projects
2. Find project where name matches the provided project_name (case-insensitive)
3. Extract the project UUID (id field)
4. If not found: report error "Project '{project_name}' not found" and exit code 1
5. If found: use this project_id for all subsequent operations

### Step 1: Read Implementation Log

1. Read `docs/implementation-log.md`
2. Extract all Ralph task IDs (pattern: `[A-Z]+-\d+`)
3. Store in `reviewed_task_ids` set
4. If log doesn't exist or empty: report "No reviewed tasks to cleanup" and exit code 0

### Step 2: List Done Tasks from Kanban

1. Use `vibe_kanban-list_tasks` MCP with:
   - `project_id`: from Step 0
   - `status`: 'done'
2. Cross-reference with `reviewed_task_ids`
3. Keep only tasks that are BOTH done AND reviewed
4. If no matching tasks: report "No tasks ready for cleanup" and exit code 0

### Step 3: Archive Each Reviewed Task

For each task to cleanup:

1. Get full task details with `vibe_kanban-get_task`
2. Create archive directory: `archive/tasks/{task_id}/`
3. Copy/move artifacts:
   - Task description → `archive/tasks/{task_id}/README.md`
   - Execution logs (if any)
   - Workspace artifacts (if any)
   - Screenshots/outputs
4. Use `vibe_kanban-update_task` to update status to 'cancelled' or add 'archived' label
5. Clean up temporary workspace files

### Step 4: Delete Git Worktrees

For all vibe-kanban worktrees and vk/* branches:

1. Run: `scripts/cleanup-worktrees.sh -f` to clean up all vibe-kanban created worktrees and branches
   - This script handles:
     - Finding all worktrees with "vibe-kanban" in path
     - Finding all vk/* branches
     - Removing worktrees with fallback to force removal if needed
     - Removing associated vk/* branches
2. Log output showing cleaned worktrees and branches
3. If script fails: log warning but continue (non-blocking)
4. The `-f` flag skips confirmation prompts (suitable for automation)

### Step 5: Delete Tasks from Vibe-Kanban

For each archived task:

1. Use `vibe_kanban-delete_task` MCP with:
   - `task_id`: from reviewed task list
   - Safety check: Verify task is in 'done' status AND appears in implementation-log.md before deletion
2. Log task deletion with ID and title
3. If deletion fails: log error but continue to next task
4. Return list of successfully deleted task IDs

### Step 6: Update CHANGELOG

1. Read existing `CHANGELOG.md` (create if missing)
2. Find or create "Archived" section
3. Append entry for each archived task:
   ```markdown
   - [YYYY-MM-DD] Archived TASK-XXX: Task Title (deleted from Vibe-Kanban)
   ```
4. Write updated CHANGELOG.md

### Step 7: Report Results

1. Report: "🧹 Archived X tasks"
2. List archived task IDs
3. Report number of deleted git worktrees
4. Report number of deleted kanban tasks
5. Report archive location for each task
6. Return exit code 0

## MCP Tools Available

- `vibe_kanban-list_tasks` - list tasks by status
- `vibe_kanban-get_task` - get detailed task info
- `vibe_kanban-delete_task` - delete task from Vibe-Kanban (used in Step 5)

## External Tools

- `scripts/cleanup-worktrees.sh` - Comprehensive worktree and branch cleanup
  - Usage: `scripts/cleanup-worktrees.sh -f` (force mode for automation)
  - Removes all vibe-kanban created worktrees
  - Removes all vk/* branches
  - Handles fallback force removal if needed
  - Provides summary of remaining worktrees/branches

## Error Handling

- **No project_id**: Exit code 1
- **No reviewed tasks**: Exit code 0 (success, nothing to do)
- **File operations fail**: Log error, continue to next task
- **CHANGELOG update fails**: Log warning, continue
- **MCP unavailable**: Exit code 1

## Success Criteria

- All reviewed+done tasks archived to archive/tasks/
- Git worktrees cleaned up and removed
- Tasks deleted from Vibe-Kanban
- Task metadata removed from vibe-kanban system
- CHANGELOG.md updated with archived tasks
- Temporary files cleaned up
- Return meaningful summary

## Archive Directory Structure

```
archive/
└── tasks/
    ├── TASK-001/
    │   ├── README.md (task description)
    │   ├── logs/
    │   └── artifacts/
    └── TASK-002/
        ├── README.md
        └── outputs/
```

## Safety Notes

- Only archives/deletes tasks that appear in implementation-log.md AND are in 'done' status
- Double safety check: implementation-log.md + vibe-kanban status before deletion
- Git worktree cleanup is non-destructive (worktrees can be recreated)
- Archive operations are idempotent (safe to re-run if needed)
- Always preserves original task data in archive/ before deletion from Vibe-Kanban
- Logs all deletions for audit trail
- If any step fails: logs error and continues with next task (partial cleanup is safe)
