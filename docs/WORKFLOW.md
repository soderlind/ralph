# Ralph SDLC Wrapper - Complete Workflow

End-to-end workflow for product development using Ralph + Vibe Kanban.

## Phase 1: Requirements → PRD

### Input: Business Requirements Document (BRD)

Create a BRD in markdown format:

```markdown
# Business Requirements Document

## Business Goals
- [Goal 1]
- [Goal 2]

## Market Context
- Target audience
- Competitive landscape

## High-Level Requirements
1. [Requirement 1]
2. [Requirement 2]

## Success Metrics
- [Metric 1]
- [Metric 2]

## Constraints
- Budget
- Timeline
- Technical constraints
```

### Command: Generate PRD

```bash
ralph brd plans/my-brd.md
```

**Output**: `plans/generated-prd.md` (structured markdown PRD)

**PRD Structure**:
- Overview
- Jobs To Be Done (JTBD)
- Acceptance Criteria
- User Flows
- Page Flows
- Technical Constraints
- Success Metrics

## Phase 2: PRD → Tasks

### Input: PRD Markdown

The PRD generated in Phase 1.

### Command: Generate Tasks

```bash
ralph prd plans/generated-prd.md
```

**Output**: `plans/tasks.json` (task breakdown with dependencies)

**Task Structure**:
```json
{
  "id": "TASK-001",
  "category": "architecture|functional|testing|documentation",
  "description": "Task summary",
  "details": "Detailed explanation",
  "steps": ["Step 1", "Step 2"],
  "acceptance": ["Criterion 1", "Criterion 2"],
  "dependencies": ["TASK-XXX"],
  "priority": "high|medium|low",
  "status": "todo"
}
```

## Phase 3: Tasks → Vibe Kanban

### Input: tasks.json

The tasks generated in Phase 2.

### Command: Create Tasks in Vibe Kanban

```bash
ralph tasks plans/tasks.json
```

**What happens**:
1. Checks/installs vibe-kanban
2. Fetches available projects (or uses configured project_id)
3. Interactive project selection if needed
4. Generates comprehensive prompt for coding agent
5. Coding agent creates all tasks via `vibe_kanban-create_task` MCP tool
6. Updates tasks.json with `kanban_id` for each task

**Output**: Tasks created in Vibe Kanban, tasks.json updated with kanban_ids

## Phase 4: Execute Tasks

### Work in Vibe Kanban

- Tasks appear in Vibe Kanban dashboard
- Coding agent can start workspace sessions for tasks
- Mark tasks as "done" when complete

## Phase 5: Review Completed Work

### Command: Review Tasks

```bash
ralph review plans/tasks.json
```

**What happens**:
1. Filters tasks with `status: "done"`
2. For each completed task, invokes `@task-review` skill
3. Generates implementation summary
4. **Appends** (not overwrites) to `docs/implementation-log.md`

**Output**: `docs/implementation-log.md` with task reviews

## Phase 6: Cleanup

### Command: Cleanup Completed Tasks

```bash
ralph cleanup
```

**What happens**:
1. Loads completed tasks from tasks.json
2. Invokes `@cleanup-agent` skill
3. Generates cleanup summary
4. Archives completed tasks to `plans/done/tasks-{timestamp}.json`
5. **Removes dependencies** on completed tasks from remaining tasks
6. **Appends** cleanup log to `docs/cleanup-log.md`
7. Runs `scripts/cleanup-worktrees.sh -f` to remove worktrees

**Output**:
- Archived tasks in `plans/done/`
- Updated tasks.json (dependencies adjusted)
- Cleanup log appended
- Worktrees removed

## Complete Example

```bash
# 1. Generate PRD from BRD
ralph brd plans/my-product-brd.md
# Output: plans/generated-prd.md

# 2. Generate tasks from PRD
ralph prd plans/generated-prd.md
# Output: plans/tasks.json

# 3. Create tasks in Vibe Kanban
ralph tasks plans/tasks.json
# Output: Tasks created, kanban_ids added to tasks.json

# 4. Work on tasks in Vibe Kanban dashboard
# (mark tasks as done when complete)

# 5. Review completed tasks
ralph review plans/tasks.json
# Output: docs/implementation-log.md (appended)

# 6. Cleanup completed work
ralph cleanup
# Output: Archived to plans/done/, dependencies adjusted, worktrees removed
```

## Configuration

### config/ralph.json

```json
{
  "vibe_kanban": {
    "executor": "CLAUDE_CODE",
    "model": "claude-sonnet-4.5",
    "project_id": null,  // Auto-prompt for selection
    "repo_config": {
      "setup_script": "npm install",
      "dev_server_script": "npm run dev",
      "cleanup_script": "git worktree prune"
    }
  },
  "paths": {
    "brd": "plans/brd.md",
    "prd": "plans/generated-prd.md",
    "tasks": "plans/tasks.json",
    "implementation_log": "docs/implementation-log.md",
    "cleanup_log": "docs/cleanup-log.md"
  }
}
```

## Skills Used

- **@brd-to-prd**: Transforms BRD → PRD markdown
- **@prd-to-tasks**: Breaks down PRD → tasks JSON
- **@task-review**: Reviews completed tasks, generates logs (append mode)
- **@cleanup-agent**: Cleans up, adjusts dependencies, archives (append mode)

## MCP Integration

Ralph uses **prompt-based MCP interaction**:

1. Ralph generates prompts
2. Coding agent (Copilot CLI) executes MCP calls
3. Ralph parses responses and updates files

**MCP Tools Used**:
- `vibe_kanban-list_projects`
- `vibe_kanban-create_task`
- `vibe_kanban-get_task`
- `vibe_kanban-update_task`
- `vibe_kanban-list_tasks`

## Next Steps

After initial setup:
1. Customize skills in `skills/` folder
2. Run `./scripts/sync-skills.sh` to sync changes
3. Adjust `config/ralph.json` for your project
4. Follow the workflow above

Happy building! 🚀
