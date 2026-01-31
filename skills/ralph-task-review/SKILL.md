---
name: ralph-task-review
description: "Review completed tasks and generate comprehensive implementation summaries"
---

# ralph-task-review Skill

**Agentic skill for reviewing completed tasks and generating implementation summaries.**

## Purpose

Review tasks in 'done' status, generate implementation summaries, and append to implementation-log.md. Optionally trigger cleanup after successful review.

## When to Use

Invoked by `ralph.py review` command when user wants to document completed work and prepare tasks for archival.

## Inputs Required

- **project_name**: Human-readable project name (e.g., "ralph-copilot", "my-project")
- **model**: Optional model for review generation (default: claude-haiku-4.5)
- **no_cleanup**: Flag to skip automatic cleanup (default: false)

## Instructions for Agent

### Step 0: Resolve Project Name to ID

1. Use `vibe_kanban-list_projects` MCP tool to get all projects
2. Find project where name matches the provided project_name (case-insensitive)
3. Extract the project UUID (id field)
4. If not found: report error "Project '{project_name}' not found" and exit code 1
5. If found: use this project_id for all subsequent operations

### Step 1: List Completed Tasks

1. Use `vibe_kanban-list_tasks` MCP with:
   - `project_id`: from Step 0
   - `status`: 'done'
2. If no done tasks: report "No tasks to review" and exit code 0

### Step 2: Filter Tasks with Ralph IDs

1. For each done task, extract Ralph task ID pattern (e.g., TASK-001, PROJ-123)
2. Use regex pattern: `\b([A-Z]+-\d+)\b`
3. Keep only tasks with valid Ralph IDs
4. If no valid tasks: report warning and exit code 0

### Step 3: Generate Review for Each Task

For each task with Ralph ID:

1. Get full task details with `vibe_kanban-get_task`
2. Build review context:
   - Task ID (Ralph format)
   - Task title
   - Task description
   - Completion date
   - Any execution logs or artifacts
3. Generate implementation summary (150-300 words):
   - What was implemented
   - Key technical decisions
   - Tests added/modified
   - Documentation updates
   - Any blockers overcome
4. Format as markdown section

### Step 4: Append to Implementation Log

1. Read existing `docs/implementation-log.md` (create if missing)
2. Append new review entries with format:
   ```markdown
   ## [Task ID] Task Title
   
   **Completed**: YYYY-MM-DD
   
   ### Implementation Summary
   
   [Generated summary]
   
   ---
   ```
3. Write updated content back to file
4. Use file locking to prevent concurrent writes

### Step 5: Optionally Trigger Cleanup

1. If `--no-cleanup` flag NOT set:
   - Invoke `@ralph-cleanup-agent` skill
   - Pass reviewed task IDs
   - Let cleanup agent handle archival

### Step 6: Report Results

1. Report: "✅ Reviewed X tasks, appended to implementation-log.md"
2. List reviewed task IDs
3. If cleanup triggered: report "🧹 Cleanup initiated"
4. Return exit code 0

## MCP Tools Available

- `vibe_kanban-list_tasks` - list tasks by status
- `vibe_kanban-get_task` - get detailed task info
- `vibe_kanban-update_task` - update task metadata

## Error Handling

- **No project_id**: Exit code 1
- **No done tasks**: Exit code 0 (success, nothing to do)
- **File write fails**: Retry once, then exit code 1
- **Review generation fails**: Skip task, log error, continue
- **MCP unavailable**: Exit code 1

## Success Criteria

- All done tasks with Ralph IDs reviewed
- Implementation summaries generated and appended
- implementation-log.md updated successfully
- Cleanup triggered (unless disabled)
- Return meaningful summary

## Example Output Format

```markdown
## TASK-001 Setup Database Schema

**Completed**: 2026-01-31

### Implementation Summary

Implemented PostgreSQL database schema with 8 tables for user management,
authentication, and content storage. Key decisions included using UUID
primary keys for better distribution and JSONB for flexible metadata storage.

Added migrations using Alembic, comprehensive unit tests covering all models,
and updated API documentation. Overcame initial performance concerns by adding
appropriate indexes on frequently queried columns.

---
```
