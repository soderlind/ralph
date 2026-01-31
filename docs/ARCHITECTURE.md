# Ralph SDLC Wrapper Architecture

Complete technical architecture for the Ralph SDLC wrapper integrating with Vibe-Kanban.

## Overview

Ralph transforms product development from requirements to implementation using:
- **Markdown PRDs** (human-readable, LLM-parseable)
- **Skills** (loaded by coding agent from project scope)
- **Vibe-Kanban integration** (via prompt-based MCP)
- **Phase-contextual commands** (brd-prd, prd-tasks, tasks-kanban, run)

## Data Flow

```
BRD.md → brd-prd → PRD.md → prd-tasks → tasks.json → tasks-kanban → Vibe Kanban
                                                                           ↓
                                                                         run
                                                                           ↓
                                                                     Workspace Sessions
```

## Data Schemas

### 1. BRD (Business Requirements Document) - Markdown

**File**: `plans/*.md`  
**Format**: Markdown

Structure: Business Goals, Market Context, Requirements, Metrics, Constraints

### 2. PRD (Product Requirements Document) - Markdown

**File**: `plans/generated-prd.md`  
**Format**: Markdown (NOT JSON)

**Why Markdown?**
- Human-readable and editable
- LLMs parse markdown excellently  
- Better for reviews and version control
- No JSON↔MD conversion needed

**Structure**:
- Overview, JTBD, Acceptance Criteria
- User Flows, Page Flows
- Technical Constraints, Success Metrics

### 3. Tasks JSON

**File**: `plans/tasks.json`  
**Format**: JSON Array

**Important**: This is the **initial definition only**. Living status is in Vibe Kanban.

```json
[
  {
    "id": "TASK-001",
    "category": "architecture|functional|testing|documentation",
    "description": "One-line summary",
    "details": "Detailed explanation",
    "steps": ["Step 1", "Step 2"],
    "acceptance": ["Criterion 1", "Criterion 2"],
    "dependencies": ["TASK-002"],
    "priority": "high|medium|low",
    "status": "todo",
    "kanban_id": "uuid-from-vibe-kanban",
    "created_at": "ISO timestamp",
    "completed_at": null
  }
]
```

## CLI Commands

### ralph brd-prd

**Phase**: BRD → PRD  
**Skill**: `@brd-to-prd`

```bash
ralph brd-prd plans/my-brd.md
# Output: plans/generated-prd.md (markdown)
```

### ralph prd-tasks

**Phase**: PRD → Tasks  
**Skill**: `@prd-to-tasks`

```bash
ralph prd-tasks plans/generated-prd.md
# Output: plans/tasks.json
```

### ralph tasks-kanban

**Phase**: Tasks → Vibe Kanban  
**MCP**: `vibe_kanban-create_task`

```bash
ralph tasks-kanban plans/tasks.json
# Creates tasks in Vibe Kanban, saves kanban_ids
```

### ralph run

**Phase**: Start Ready Tasks  
**MCP**: `vibe_kanban-list_tasks`, `vibe_kanban-start_workspace_session`

```bash
ralph run
# Starts tasks with no dependencies
```

**Key Features**:
- Reads from Vibe Kanban (NOT tasks.json)
- Living status in Vibe Kanban
- Progressive execution (call multiple times)

## Living Status Concept

**Critical**: Task status lives in Vibe Kanban, not tasks.json.

```
tasks.json          → Initial definition (created once)
Vibe Kanban         → Living system (real-time status)
ralph tasks-kanban  → Creates tasks, saves kanban_ids
ralph run           → Reads Vibe Kanban, starts ready tasks
```

## Skills Architecture

### Skill Loading Pattern

- Skills in project scope: `.copilot/skills/`, `.claude/skills/`
- Ralph references by name: `@brd-to-prd`
- Coding agent loads skills natively
- Source of truth: `skills/` folder

### Available Skills

1. **@brd-to-prd**: BRD markdown → PRD markdown (~100 lines)
2. **@prd-tasks**: PRD markdown → tasks JSON (~100 lines)
3. **@task-review**: Review completed tasks (future)
4. **@cleanup-agent**: Cleanup & archive (future)

## Vibe-Kanban Integration

### Pattern: Prompt-Based MCP

```
Ralph → Prompts → Coding Agent → MCP Calls → Vibe-Kanban
```

### MCP Tools Used

- `vibe_kanban-list_projects` - Get projects
- `vibe_kanban-create_task` - Create tasks
- `vibe_kanban-list_tasks` - Get task status
- `vibe_kanban-start_workspace_session` - Start work

## Configuration

```json
{
  "vibe_kanban": {
    "executor": "CLAUDE_CODE",
    "model": "claude-sonnet-4.5",
    "project_id": "uuid"
  },
  "paths": {
    "prd": "plans/generated-prd.md",
    "tasks": "plans/tasks.json"
  }
}
```

## Design Principles

1. **Markdown for PRDs** - Human-readable, LLM-parseable
2. **Prompt-Based MCP** - Clean separation of concerns
3. **Skills in Project Scope** - Native loading by agent
4. **Living Status in Vibe Kanban** - Single source of truth
5. **Phase-Contextual Commands** - Clear workflow progression

---

**Version**: 2.0 (Markdown PRD, phase-contextual commands, ralph run)
