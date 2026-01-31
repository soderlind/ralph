# Ralph SDLC Wrapper - Complete Workflow

End-to-end workflow for product development using Ralph + Vibe Kanban.

## Phase 1: BRD → PRD

### Input: Business Requirements Document (BRD)

Create a BRD in markdown format with business goals, market context, requirements, metrics, and constraints.

### Command: Generate PRD

```bash
ralph brd-prd plans/my-brd.md
```

**Output**: `plans/generated-prd.md` (structured markdown PRD)

**PRD Structure**:
- Overview, JTBD, Acceptance Criteria
- User Flows, Page Flows
- Technical Constraints, Success Metrics

## Phase 2: PRD → Tasks

### Input: PRD Markdown

The PRD generated in Phase 1.

### Command: Generate Tasks

```bash
ralph prd-tasks plans/generated-prd.md
```

**Output**: `plans/tasks.json` (task breakdown with dependencies)

## Phase 3: Tasks → Vibe Kanban

### Input: tasks.json

The tasks generated in Phase 2.

### Command: Create Tasks in Vibe Kanban

```bash
ralph tasks-kanban plans/tasks.json
```

**What happens**:
1. Checks/installs vibe-kanban
2. Fetches available projects (or uses configured project_id)
3. Interactive project selection if needed
4. Coding agent creates all tasks via `vibe_kanban-create_task` MCP
5. Updates tasks.json with `kanban_id` for each task

**Output**: Tasks created in Vibe Kanban, tasks.json updated

## Phase 4: Run Tasks (No Dependencies)

### Command: Start Tasks

```bash
ralph run
```

**What happens**:
1. Fetches all tasks from Vibe Kanban (live status)
2. Filters for `status='todo'` with no dependencies
3. Starts workspace sessions using `vibe_kanban-start_workspace_session` MCP
4. Reports started/failed sessions

**Note**: Always reads from Vibe Kanban (not tasks.json) - living status is in Vibe Kanban.

**Output**: Workspace sessions started for ready tasks

## Phase 5: Review Completed Work

### Command: Review Tasks

```bash
ralph review plans/tasks.json
```

**What happens**:
1. Filters tasks with `status='done'`
2. Invokes `@task-review` skill for each
3. **Appends** to `docs/implementation-log.md`

## Phase 6: Cleanup

### Command: Cleanup Completed Tasks

```bash
ralph cleanup
```

**What happens**:
1. Archives completed tasks to `plans/done/`
2. **Removes dependencies** on completed tasks
3. **Appends** to `docs/cleanup-log.md`
4. Runs `scripts/cleanup-worktrees.sh`

## Complete Example

```bash
# 1. Generate PRD from BRD
ralph brd-prd plans/my-product-brd.md
# Output: plans/generated-prd.md

# 2. Generate tasks from PRD
ralph prd-tasks plans/generated-prd.md
# Output: plans/tasks.json

# 3. Create tasks in Vibe Kanban
ralph tasks-kanban plans/tasks.json
# Output: Tasks created, kanban_ids added

# 4. Start tasks with no dependencies
ralph run
# Output: Workspace sessions started

# 5. Monitor progress in Vibe Kanban
# (tasks automatically update status)

# 6. Start next batch when ready
ralph run
# Output: Starts newly-ready tasks

# 7. Review completed tasks (optional)
ralph review plans/tasks.json
# Output: docs/implementation-log.md (appended)

# 8. Cleanup completed work (optional)
ralph cleanup
# Output: Archived, dependencies adjusted
```

## Configuration

### config/ralph.json

```json
{
  "vibe_kanban": {
    "executor": "CLAUDE_CODE",
    "model": "claude-sonnet-4.5",
    "project_id": "your-project-uuid-here",
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

- **@brd-to-prd**: BRD → PRD markdown
- **@prd-to-tasks**: PRD → tasks JSON
- **@task-review**: Review completed tasks (append mode)
- **@cleanup-agent**: Cleanup & archive (append mode)

## MCP Integration

Ralph uses **prompt-based MCP interaction**:

1. Ralph generates prompts
2. Coding agent executes MCP calls
3. Ralph parses responses and updates files

**MCP Tools Used**:
- `vibe_kanban-list_projects` - Get available projects
- `vibe_kanban-create_task` - Create tasks
- `vibe_kanban-list_tasks` - Get task status (live)
- `vibe_kanban-start_workspace_session` - Start coding sessions

## Key Concepts

### Living Status in Vibe Kanban

**Important**: Task status lives in Vibe Kanban, not in tasks.json.

- `tasks.json` is the **initial definition** (created once)
- Vibe Kanban is the **living system** (status updates in real-time)
- `ralph run` always reads from Vibe Kanban
- `ralph tasks-kanban` creates tasks and saves `kanban_id` for reference

### Dependency Management

Tasks are started only when:
1. Status is `todo`
2. No dependencies mentioned in task description
3. Workspace session can be started

`ralph run` can be called multiple times - it will always check the current state in Vibe Kanban and start newly-ready tasks.

## Next Steps

After initial setup:
1. Customize skills in `skills/` folder
2. Run `./scripts/sync-skills.sh` to sync changes
3. Set `project_id` in `config/ralph.json`
4. Follow the workflow above

Happy building! 🚀
