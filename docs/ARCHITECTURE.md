```
╔════════════════════════════════════════════════════════════════╗
║          RALPH SDLC WRAPPER - ARCHITECTURE GUIDE               ║
╚════════════════════════════════════════════════════════════════╝
```

# Ralph SDLC Wrapper Architecture

Complete technical architecture for the Ralph SDLC wrapper integrating with Vibe-Kanban.

## 🎯 Overview

Ralph transforms product development from requirements to implementation using:

| Component | Purpose |
|-----------|---------|
| **Markdown PRDs** | Human-readable, LLM-parseable specifications |
| **Agentic Skills** | Loaded by coding agent from project scope |
| **Vibe-Kanban integration** | Via prompt-based MCP protocol |
| **Phase-contextual commands** | Clear workflow progression (brd-prd → prd-tasks → tasks-kanban → run) |
| **Two-mode execution** | Prompt generator (default) + Execute mode (automation) |

## 🔄 Two-Mode Architecture

Ralph operates in two distinct modes to address different use cases:

### Mode 1: Prompt Generator (Default)

**Purpose:** Solves MCP permission issues by generating prompts for interactive Copilot

**Flow:**
```
User → ralph.py → print_prompt() → Terminal
                                      ↓
User copies prompt                    
                                      ↓
User → copilot (interactive)
                                      ↓
Skills execute → MCP tools → Permissions granted naturally
```

**Benefits:**
- ✅ No pre-setup permission headaches
- ✅ Users see what will happen before running
- ✅ Learning tool (shows skill usage)
- ✅ Easy to share with team

### Mode 2: Execute (--execute flag)

**Purpose:** Direct automation for scripts and CI/CD

**Flow:**
```
User → ralph.py --execute → invoke_copilot() → copilot subprocess
                                                    ↓
                                              Skills execute → MCP tools
```

**Requirements:**
- ⚠️ MCP permissions already granted
- ✅ For automation/scripts
- ✅ Use with --yolo for non-interactive

**Usage:**
```bash
# Prompt mode (default)
./ralph.py tasks-kanban plans/tasks.json

# Execute mode
./ralph.py --execute tasks-kanban plans/tasks.json

# Execute + YOLO (CI/CD)
./ralph.py --execute --yolo run
```

## Data Flow

```
BRD.md → brd-prd → PRD.md → prd-tasks → tasks.json → tasks-kanban → Vibe Kanban
                                                                           ↓
                                                                         run
                                                                           ↓
                                                                     Workspace Sessions
```

## 📋 Data Schemas

### 1️⃣ BRD (Business Requirements Document) - Markdown

| Attribute | Value |
|-----------|-------|
| **File** | `plans/*.md` |
| **Format** | Markdown |
| **Structure** | Business Goals, Market Context, Requirements, Metrics, Constraints |

### 2️⃣ PRD (Product Requirements Document) - Markdown

| Attribute | Value |
|-----------|-------|
| **File** | `plans/generated-prd.md` |
| **Format** | Markdown (NOT JSON) |

#### ✨ Why Markdown?
- ✓ Human-readable and editable
- ✓ LLMs parse markdown excellently  
- ✓ Better for reviews and version control
- ✓ No JSON↔MD conversion needed

#### 📑 Structure:
- Overview, JTBD, Acceptance Criteria
- User Flows, Page Flows
- Technical Constraints, Success Metrics

### 3️⃣ Tasks JSON

| Attribute | Value |
|-----------|-------|
| **File** | `plans/tasks.json` |
| **Format** | JSON Array |
| **Important** | This is the **initial definition only**. Living status is in Vibe Kanban. |

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

## ⚙️ CLI Commands

### 🔨 ralph brd-prd

| Property | Value |
|----------|-------|
| **Phase** | BRD → PRD |
| **Skill** | `@ralph-brd-to-prd` |

```bash
ralph brd-prd plans/my-brd.md
# Output: plans/generated-prd.md (markdown)
```

---

### 🔨 ralph prd-tasks

| Property | Value |
|----------|-------|
| **Phase** | PRD → Tasks |
| **Skill** | `@ralph-prd-to-tasks` |

```bash
ralph prd-tasks plans/generated-prd.md
# Output: plans/tasks.json
```

---

### 🔨 ralph tasks-kanban

| Property | Value |
|----------|-------|
| **Phase** | Tasks → Vibe Kanban |
| **MCP** | `vibe_kanban-create_task` |

```bash
ralph tasks-kanban plans/tasks.json
# Creates tasks in Vibe Kanban, saves kanban_ids
```

---

### 🔨 ralph run

| Property | Value |
|----------|-------|
| **Phase** | Start Ready Tasks |
| **MCP** | `vibe_kanban-list_tasks`, `vibe_kanban-start_workspace_session` |

```bash
ralph run
# Starts tasks with no dependencies
```

#### ⭐ Key Features:
- ✓ Reads from Vibe Kanban (NOT tasks.json)
- ✓ Living status in Vibe Kanban
- ✓ Progressive execution (call multiple times)

## 🔄 Living Status Concept

> **⚠️ Critical**: Task status lives in Vibe Kanban, not tasks.json.

```
┌───────────────────────────────────────────────────────────┐
│ tasks.json          → Initial definition (created once)   │
│ Vibe Kanban         → Living system (real-time status)    │
│ ralph tasks-kanban  → Creates tasks, saves kanban_ids     │
│ ralph run           → Reads Vibe Kanban, starts ready tasks│
└───────────────────────────────────────────────────────────┘
```

## 🎓 Skills Architecture

### 🔧 Skill Loading Pattern

| Aspect | Details |
|--------|---------|
| **Location** | `.copilot/skills/`, `.claude/skills/` |
| **Reference** | By name: `@ralph-brd-to-prd` |
| **Agent** | Coding agent loads skills natively |
| **Truth** | Source of truth: `skills/` folder |

### 📚 Available Skills

| Skill | Description | Est. Size |
|-------|-------------|-----------|
| **@ralph-brd-to-prd** | BRD markdown → PRD markdown | ~100 lines |
| **@prd-tasks** | PRD markdown → tasks JSON | ~100 lines |
| **@ralph-task-review** | Review completed tasks | future |
| **@ralph-cleanup-agent** | Cleanup & archive | future |

## 🔗 Vibe-Kanban Integration

### 🎯 Pattern: Prompt-Based MCP

```
Ralph ──▶ Prompts ──▶ Coding Agent ──▶ MCP Calls ──▶ Vibe-Kanban
```

### 🛠️ MCP Tools Used

| Tool | Purpose |
|------|---------|
| `vibe_kanban-list_projects` | Get projects |
| `vibe_kanban-create_task` | Create tasks |
| `vibe_kanban-list_tasks` | Get task status |
| `vibe_kanban-start_workspace_session` | Start work |

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

## 💡 Design Principles

1. **📝 Markdown for PRDs** — Human-readable, LLM-parseable
2. **🎯 Prompt-Based MCP** — Clean separation of concerns
3. **📦 Skills in Project Scope** — Native loading by agent
4. **🔒 Living Status in Vibe Kanban** — Single source of truth
5. **🚀 Phase-Contextual Commands** — Clear workflow progression

---

```
╔════════════════════════════════════════════════════════════════╗
║                  Version 2.0                                   ║
║      Markdown PRD • Phase-Contextual Commands • Ralph Run       ║
╚════════════════════════════════════════════════════════════════╝
```
