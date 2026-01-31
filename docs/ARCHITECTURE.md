# Ralph SDLC Wrapper - Data Schemas

## 1. BRD Schema (Business Requirements Document)

**File format**: Markdown (`.md`)
**Location**: `plans/brd.md`

```markdown
# Business Requirements Document

## Business Goals
- Goal 1: [High-level business objective]
- Goal 2: [What problem are we solving?]

## Market Context
- Target audience: [Who is this for?]
- Market opportunity: [Why now?]
- Competitive landscape: [What alternatives exist?]

## High-Level Requirements
1. Requirement 1: [User-facing capability]
2. Requirement 2: [Key feature]
3. Requirement 3: [Integration or constraint]

## Success Metrics
- Metric 1: [How do we measure success?]
- Metric 2: [What KPIs matter?]

## Constraints
- Budget: [Financial constraints]
- Timeline: [When do we need this?]
- Technical: [Platform, technology, or infrastructure constraints]
```

---

## 2. PRD Schema (Product Requirements Document)

**File format**: JSON (`.json`)
**Location**: `plans/prd.json`

```json
{
  "project_name": "string",
  "version": "string",
  "created_at": "ISO 8601 timestamp",
  "brd_source": "path/to/brd.md",
  "overview": "string (high-level summary)",
  "jtbd": [
    {
      "persona": "string (e.g., 'End User', 'Admin')",
      "job": "string (what they want to accomplish)",
      "outcome": "string (why it matters)"
    }
  ],
  "acceptance_criteria": [
    {
      "id": "AC-001",
      "description": "string",
      "category": "functional|non-functional|technical"
    }
  ],
  "user_flows": [
    {
      "id": "UF-001",
      "name": "string (e.g., 'User Login Flow')",
      "steps": [
        "Step 1: User lands on login page",
        "Step 2: User enters credentials",
        "Step 3: System validates and redirects"
      ],
      "acceptance_criteria_ids": ["AC-001", "AC-002"]
    }
  ],
  "page_flows": [
    {
      "id": "PF-001",
      "name": "string (e.g., 'Dashboard to Settings')",
      "pages": [
        {"page": "Dashboard", "action": "Click settings icon"},
        {"page": "Settings", "action": "View/edit"}
      ]
    }
  ],
  "technical_constraints": [
    {
      "type": "platform|technology|integration|security|performance",
      "description": "string",
      "rationale": "string (why this constraint exists)"
    }
  ]
}
```

---

## 3. Task Schema

**File format**: JSON (`.json`)
**Location**: `plans/tasks.json`

```json
[
  {
    "id": "TASK-001",
    "category": "functional|architecture|documentation|testing|infrastructure",
    "description": "string (one-line summary)",
    "details": "string (optional: technical context, notes)",
    "steps": [
      "Step 1: Create component X",
      "Step 2: Implement logic Y",
      "Step 3: Add tests for Z"
    ],
    "acceptance": [
      "Acceptance 1: Tests pass",
      "Acceptance 2: Code compiles without errors"
    ],
    "dependencies": ["TASK-002", "TASK-003"],
    "priority": 1,
    "status": "todo|in_progress|done|blocked",
    "kanban_id": "uuid (from vibe-kanban MCP)",
    "created_at": "ISO 8601 timestamp",
    "completed_at": "ISO 8601 timestamp (optional)"
  }
]
```

**Dependency Rules**:
- Tasks with no dependencies can run in parallel
- Tasks with dependencies run only when all dependencies are "done"
- When cleanup runs, dependencies on cleaned tasks are removed from remaining tasks

---

## 4. CLI Command Structure

```bash
# Step 1: BRD → PRD
ralph brd <brd-file.md>
  → Invokes brd-to-prd skill
  → Saves output to plans/generated-prd.json
  → Prompts user to review/edit

# Step 2: PRD → Tasks
ralph prd <prd-file.json>
  → Invokes prd-to-tasks skill
  → Saves output to plans/tasks.json
  → Flags dependencies needing human review
  → Prompts user to confirm

# Step 3: Create Kanban Tasks
ralph tasks <tasks-file.json>
  → Pre-flight: npx vibe-kanban (ensure installed)
  → Check MCP connection
  → If no project_id in config: list projects, prompt user to select
  → For each task: vibe_kanban-create_task
  → Store kanban_id in tasks.json

# Step 4: Execute Tasks
ralph run [--parallel] [--limit N]
  → Identify tasks with no dependencies or satisfied dependencies
  → If --parallel: start multiple vibe-kanban workspace sessions
  → Poll vibe-kanban task status until done
  → Mark tasks as "in_progress" / "done" in tasks.json

# Step 5: Review Tasks
ralph review <tasks-file.json>
  → List completed tasks with summaries
  → Prompt user to accept/request changes
  → Update task status in tasks.json
  → APPEND to docs/implementation-log.md

# Step 6: Cleanup
ralph cleanup
  → Invoke cleanup skill (auto-generate summary)
  → APPEND to docs/cleanup-log.md
  → Remove dependencies from remaining tasks
  → Run scripts/cleanup-worktrees.sh -f
  → Close done tasks in vibe-kanban
  → Archive tasks.json → done/tasks-{timestamp}.json
```

---

## 5. Vibe-Kanban MCP Integration Points

### Required MCP Endpoints:
1. **vibe_kanban-list_projects** → Get project list (for user selection)
2. **vibe_kanban-create_task** → Create task in kanban board
3. **vibe_kanban-get_task** → Get task status/details
4. **vibe_kanban-list_tasks** → List all tasks in project
5. **vibe_kanban-update_task** → Update task status
6. **vibe_kanban-start_workspace_session** → Start coding agent on task
7. **vibe_kanban-list_repos** → Get repo config for project

### Workflow:
```
ralph tasks → create_task (get kanban_id)
ralph run → start_workspace_session → poll get_task (check status)
ralph cleanup → update_task (close) + delete_task
```

---

## 6. Philosophy: Full SDLC Wrapper (No Backward Compatibility)

**Design Decision**: This is a complete reimagining of Ralph, not an extension of the old loop-based approach.

**Key Differences from Old ralph.py**:
- **Old**: Simple loop executing PRD items sequentially with Copilot CLI
- **New**: Full SDLC workflow (BRD → PRD → Tasks → Execute → Review → Cleanup)
- **Old**: Programmatic Copilot CLI calls
- **New**: Vibe-Kanban coding agent orchestration via prompts
- **Old**: Single progress.txt log
- **New**: Structured logs (implementation-log.md, cleanup-log.md)

**What We Keep**:
- `scripts/cleanup-worktrees.sh` (enhanced for vibe-kanban)
- `plans/` folder structure
- Append-only logging philosophy

---

## Next Steps

- [x] Define schemas (this document)
- [ ] Create config/ralph.json with defaults
- [ ] Create lib/vibe_kanban_client.py wrapper
- [ ] Implement CLI commands (ralph brd, ralph prd, ralph tasks, etc.)
- [ ] Build skills (brd-to-prd, prd-to-tasks, task-review, cleanup-agent)
