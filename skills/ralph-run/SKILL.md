---
name: ralph-run
description: "Start workspace sessions for ready tasks with no pending dependencies"
---

# ralph-run Skill

**Agentic skill for executing ready tasks via workspace sessions.**

## Purpose

Start workspace sessions for tasks that have no pending dependencies. Manage git repositories, executor selection, and workspace initialization.

## When to Use

Invoked by `ralph.py run` command when user wants to execute tasks that are ready (status='todo' and zero blocking dependencies).

## Inputs Required

- **project_name**: Human-readable project name (e.g., "ralph-copilot", "my-project")
- **executor**: Optional executor type (default: CLAUDE_CODE)
- **variant**: Optional executor variant
- **repo_config**: Repository configuration (branches, scripts)

## Instructions for Agent

### Step 0: Resolve Project Name to ID & Get Repository Info

1. Use `vibe_kanban-list_projects` MCP tool to get all projects
2. Find project where name matches the provided project_name (case-insensitive)
3. Extract the project UUID (id field)
4. If not found: report error "Project '{project_name}' not found" and exit code 1
5. If found: use this project_id for all subsequent operations
6. **IMPORTANT:** Immediately call `vibe_kanban-list_repos` with the project_id
   - Extract the first (or only) repository ID
   - Store this repo_id for use in Step 3 (start_workspace_session requires repo_id)
   - If no repositories found: report error and exit code 1

### Step 1: Detect Git Repository Context

1. Run `git remote get-url origin` to get repository URL
2. Extract repository name from URL (handles both https:// and git@ formats)
3. Get current branch with `git branch --show-current`
4. Read repo config from ralph config (base_branch, setup scripts)
5. If git detection fails: use fallback config or exit with error

### Step 2: List Ready Tasks

1. Use `vibe_kanban-list_tasks` MCP with:
   - `project_id`: from Step 0
   - `status`: 'todo'
2. **Filter tasks by title format**: Only include tasks with titles matching `TASK-\d{3}:` pattern
   - ✅ Valid: "TASK-001: Create file", "TASK-123: Update config"
   - ❌ Invalid: "Fix bug", "Update documentation", "My custom task"
   - This prevents Ralph from starting manually-created tasks in Vibe-Kanban
3. Filter tasks to find those with zero dependencies or all dependencies completed
4. If no ready tasks: report "No ready tasks to execute" and exit code 0

### Step 3: Start Workspace for Each Ready Task

For each ready task:

1. Get full task details with `vibe_kanban-get_task`
2. Prepare repository configuration:
   - **repo_id**: from Step 0 (already resolved)
   - Base branch (auto-detected or from config)
   - Setup script (if configured)
   - Dev server script (if configured)
3. Use `vibe_kanban-start_workspace_session` MCP with:
   - `task_id`: task UUID
   - `executor`: from input or default
   - `variant`: from input (optional)
   - `repos`: array of repo configs with **repo_id included** (required by API)
4. Log workspace session ID returned
5. Update task status to 'inprogress' with `vibe_kanban-update_task`

### Step 4: Report Results

1. Count successful workspace sessions started
2. Report summary: "✅ Started X workspace sessions"
3. List task IDs/titles that were started
4. If failures: report which tasks failed to start
5. Return exit code 0 if any started, 1 if all failed

## Task Format Requirements

**IMPORTANT:** Ralph only processes tasks that follow the standard naming convention:

**Pattern:** `TASK-XXX: Description`
- `TASK-` prefix (case-sensitive)
- 3-digit number (001-999)
- Colon separator
- Space
- Task description

**Examples:**
- ✅ `TASK-001: Create TEST.md file`
- ✅ `TASK-042: Update configuration`
- ✅ `TASK-999: Final cleanup`
- ❌ `Fix bug in parser` (no TASK- prefix)
- ❌ `Task-001: Do something` (wrong case)
- ❌ `TASK-1: Quick fix` (not 3 digits)

**Why this filtering?**
- Prevents Ralph from starting manually-created tasks in Vibe-Kanban
- Ensures only Ralph-managed tasks are automated
- Allows users to create custom tasks that won't be auto-executed
- Maintains clear separation between Ralph tasks and other work items

## MCP Tools Available

- `vibe_kanban-list_projects` - list all projects (used in Step 0)
- `vibe_kanban-list_repos` - get repository info (used in Step 0 to resolve repo_id)
- `vibe_kanban-list_tasks` - list tasks by status (used in Step 2)
- `vibe_kanban-get_task` - get task details (used in Step 3)
- `vibe_kanban-start_workspace_session` - start execution (used in Step 3, requires repo_id from Step 0)
- `vibe_kanban-update_task` - update task status (used in Step 3)

## Available Executors

- `CLAUDE_CODE` (default) - Claude Sonnet for coding
- `AMP` - Anthropic Model Protocol
- `GEMINI` - Google Gemini
- `CODEX` - OpenAI Codex
- `OPENCODE` - OpenCode executor
- `CURSOR_AGENT` - Cursor agent
- `QWEN_CODE` - Qwen coding model
- `COPILOT` - GitHub Copilot
- `DROID` - Droid executor

## Error Handling

- **No project_id**: Exit code 1 with error message
- **Git detection fails**: Try fallback config, if none exit 1
- **No ready tasks**: Exit code 0 (success, nothing to do)
- **Workspace start fails**: Log error, continue to next task
- **MCP unavailable**: Exit code 1 with error message

## Success Criteria

- At least one workspace session started successfully
- Task status updated to 'inprogress'
- Workspace session ID logged for tracking
- Return meaningful summary to user

## Example Usage

```bash
# Start ready tasks with default executor
./ralph.py run

# Start with specific executor
./ralph.py run --executor GEMINI

# Start with executor variant
./ralph.py run --executor CLAUDE_CODE --variant premium
```
