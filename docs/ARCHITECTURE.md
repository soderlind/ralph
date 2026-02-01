# Ralph SDLC Wrapper - Architecture Guide

Complete technical architecture showing HOW Ralph works internally.

> **See also:** [docs/RFC.md](RFC.md) for design philosophy (WHY Ralph exists)

---

## 🎯 Overview

Ralph transforms product development through a structured pipeline:

| Component | Purpose |
|-----------|---------|
| **ralph.py** | Command orchestrator and prompt generator |
| **Agentic Skills** | AI-executable markdown workflows |
| **Vibe-Kanban MCP** | Task management integration via Model Context Protocol |
| **Git Worktrees** | Isolated workspaces for parallel execution |
| **Two-mode execution** | Prompt generator (default) + Execute mode (automation) |

---

## 📊 System Architecture

### High-Level Components

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                           USER                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        ralph.py                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ print_prompt │  │ detect_git   │  │ load_config  │          │
│  │   ()         │  │ _branch()    │  │   ()         │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  Commands: brd, prd, tasks-kanban, run, review, cleanup         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ├──────────────┬──────────────┐
                     ▼              ▼              ▼
          ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
          │   Copilot    │ │  AI Skills   │ │ Config Files │
          │     CLI      │ │  (.copilot/  │ │  (ralph.json)│
          └──────┬───────┘ │   skills/)   │ └──────────────┘
                 │         └──────┬───────┘
                 │                │
                 └────────┬───────┘
                          ▼
              ┌─────────────────────┐
              │   Vibe-Kanban MCP   │
              │  (Task Management)  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │   Git Worktrees     │
              │ (Isolated Workspaces)│
              └─────────────────────┘
```

### Component Descriptions

**ralph.py**
- Python CLI orchestrator
- Generates prompts or executes commands
- Detects git context, loads configuration
- Routes commands to appropriate skills

**Copilot CLI**
- GitHub Copilot command-line interface
- Loads and executes AI skills
- Grants MCP permissions interactively
- Provides AI-powered code generation

**AI Skills**
- Markdown-based workflow instructions
- Loaded from `.copilot/skills/` and `.claude/skills/`
- Executed by AI (not scripted)
- 6 skills: brd-to-prd, prd-to-tasks, tasks-kanban, run, task-review, cleanup-agent

**Vibe-Kanban MCP**
- Model Context Protocol server for task management
- Runs locally via `npx vibe-kanban --mcp`
- Provides tools: list_projects, create_task, start_workspace_session, etc.
- Permissions managed by Copilot CLI

**Git Worktrees**
- Parallel isolated development environments
- One worktree per task (e.g., `vibe-kanban-TASK-001/`)
- Enables simultaneous task execution
- Cleaned up via `scripts/cleanup-worktrees.sh`

---

##🔄 Two-Mode Architecture

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
