---
name: ralph-tasks-kanban
description: "Create tasks in Vibe-Kanban from JSON files with dependency handling and validation"
---

# ralph-tasks-kanban Skill

**Agentic skill for creating tasks in vibe-kanban from JSON files.**

## Purpose

Read a tasks JSON file and create corresponding task records in vibe-kanban project. Handle dependencies, validation, and batch creation.

## When to Use

Invoked by `ralph.py tasks-kanban` command when user wants to populate vibe-kanban with tasks from a JSON file.

## Inputs Required

- **tasks_file**: Path to JSON file containing tasks array
- **project_name**: Human-readable project name (e.g., "ralph-copilot", "my-project")

## Instructions for Agent

### Step 0: Resolve Project Name to ID

1. Use `vibe_kanban-list_projects` MCP tool to get all projects
2. Find project where name matches the provided project_name (case-insensitive)
3. Extract the project UUID (id field)
4. If not found: report error "Project '{project_name}' not found" and exit code 1
5. If found: use this project_id for all subsequent operations

### Step 1: Read and Validate Tasks File

1. Read the tasks JSON file from the provided path
2. Parse JSON and validate it's an array
3. Check each task has required fields: `id`, `title`
4. Optional fields: `description`, `dependencies` (array of task IDs)

### Step 2: Check vibe-kanban MCP Availability

1. Use `vibe_kanban-list_projects` MCP tool to verify connection (already done in Step 0)
2. If fails: report "vibe-kanban MCP server not available" and exit with code 1

### Step 3: Create Tasks in Dependency Order

1. Build dependency graph from tasks
2. Sort tasks by dependencies (tasks with no deps first)
3. For each task in order:
   - Use `vibe_kanban-create_task` MCP tool with:
     - `project_id`: from Step 0
     - `title`: from task JSON
     - `description`: from task JSON (optional)
   - Store returned task UUID for dependency linking
   - If task creation fails: log error and continue to next task

### Step 4: Report Results

1. Count successful vs failed task creations
2. Report summary: "✅ Created X/Y tasks in project '{project_name}'"
3. If any failures: list failed task IDs/titles
4. Return exit code 0 if majority succeeded, 1 if majority failed

## MCP Tools Available

- `vibe_kanban-list_projects` - list all projects (for name resolution)
- `vibe_kanban-create_task` - create individual task
- `vibe_kanban-list_tasks` - list existing tasks (for validation)
- `vibe_kanban-get_task` - get task details

## Error Handling

- **Project not found**: Exit code 1 with clear error message
- **JSON parse error**: Report line/column and exit code 1
- **Missing required fields**: Skip task, log warning, continue
- **MCP unavailable**: Report and exit code 1
- **Task creation fails**: Log error, continue to next task
- **Circular dependencies**: Detect and report, skip affected tasks

## Success Criteria

- Project name resolved to valid UUID
- At least 80% of tasks created successfully
- No circular dependency deadlocks
- All dependency relationships preserved
- Return meaningful summary to user

## Example Task JSON Format

```json
[
  {
    "id": "TASK-001",
    "title": "Setup database schema",
    "description": "Create tables and migrations",
    "dependencies": []
  },
  {
    "id": "TASK-002",
    "title": "Implement API endpoints",
    "description": "REST API for CRUD operations",
    "dependencies": ["TASK-001"]
  }
]
```
