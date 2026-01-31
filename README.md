# Ralph: SDLC Wrapper for Product Development

**Ralph** is an intelligent software development lifecycle orchestrator that transforms product requirements into executed code through a structured, LLM-powered workflow.

## What is Ralph?

Ralph automates the journey from **Business Requirements → Product Requirements → Implementation Tasks → Execution** using:

- **Markdown-based documentation** (human-readable, LLM-friendly)
- **AI-powered skill transformations** (BRD→PRD, PRD→Tasks)
- **Vibe-Kanban integration** (task management and workspace orchestration)
- **Phase-contextual commands** (clear workflow progression)

## Quick Start

Choose your starting point:

### Option A: Start with Business Requirements (BRD)

If you have business requirements in markdown format:

#### 1. Transform BRD → PRD

```bash
ralph brd-prd plans/my-product-brd.md
# Output: plans/generated-prd.md (Product Requirements Document)
```

#### 2. Break PRD into Tasks

```bash
ralph prd-tasks plans/generated-prd.md
# Output: plans/tasks.json (atomic tasks with dependencies)
```

### Option B: Start with Product Requirements (PRD)

If you already have a PRD in markdown format:

#### 1. Break PRD into Tasks

```bash
ralph prd-tasks plans/my-product-prd.md
# Output: plans/tasks.json (atomic tasks with dependencies)
```

### Both Options: Create Tasks & Execute

#### 2. Create Tasks in Vibe-Kanban

```bash
ralph tasks-kanban plans/tasks.json
# Creates tasks in Vibe-Kanban, saves kanban_ids
```

#### 3. Start Ready Tasks

```bash
ralph run
# Starts workspace sessions for tasks with no dependencies
# Call again to start newly-ready tasks
```

## The Workflow

```
BRD.md → brd-prd → PRD.md → prd-tasks → tasks.json → tasks-kanban → Vibe Kanban
                                                                           ↓
                                                                         run
                                                                           ↓
                                                                   Workspace Sessions
```

### Phase 1: BRD → PRD
Transform business requirements into a product requirements document with acceptance criteria, user flows, and technical constraints.

**Command**: `ralph brd-prd <brd-file>`

### Phase 2: PRD → Tasks
Break the PRD into atomic, executable tasks with clear dependencies and priorities.

**Command**: `ralph prd-tasks <prd-file>`

### Phase 3: Tasks → Kanban
Create tasks in Vibe-Kanban, linking them to a coding agent executor.

**Command**: `ralph tasks-kanban <tasks-file>`

### Phase 4: Execute Tasks
Start workspace sessions for tasks that are ready (status=todo, no dependencies).

**Command**: `ralph run`

### Phase 5: Review & Cleanup (Optional)
Review completed work and clean up dependencies.

**Commands**: `ralph review`, `ralph cleanup`

## Project Structure

```
ralph-copilot/
├── README.md                    # This file
├── LICENSE
│
├── config/
│   ├── ralph.json              # Main configuration
│   └── mcp-config.json         # Vibe-Kanban MCP configuration
│
├── docs/
│   ├── ARCHITECTURE.md         # Technical architecture & schemas
│   └── WORKFLOW.md             # Complete workflow guide
│
├── lib/
│   └── vibe_kanban_client.py   # Vibe-Kanban integration library
│
├── skills/                     # AI skills for transformations
│   ├── brd-to-prd/
│   ├── prd-to-tasks/
│   ├── task-review/
│   └── cleanup-agent/
│
├── scripts/
│   └── cleanup-worktrees.sh    # Workspace cleanup utility
│
└── plans/                      # BRD, PRD, tasks storage
    └── done/                   # Archived completed tasks
```

## Key Features

### 🎯 Markdown-First Design
- BRDs and PRDs are plain markdown files
- Human-readable and version-controllable
- LLMs understand markdown excellently

### 🤖 AI-Powered Transformations
Each phase uses domain-specific skills:
- **@brd-to-prd**: Transforms business goals into product requirements
- **@prd-to-tasks**: Breaks requirements into executable tasks
- **@task-review**: Documents technical decisions
- **@cleanup-agent**: Handles completion and dependency cleanup

### 🔗 Living Status in Vibe-Kanban
- Task definitions start in `tasks.json`
- Real-time status lives in Vibe-Kanban
- `ralph run` always reads current state
- Call multiple times to start newly-ready tasks

### 📋 Dependency Management
Tasks are executed progressively:
1. Only tasks with `status='todo'` and no dependencies start
2. As dependencies complete, new tasks become ready
3. `ralph run` can be called repeatedly to start next batches

### 📝 Append-Only Logging
- `ralph review` and `ralph cleanup` append to logs
- History is preserved, nothing is overwritten
- Easy to track decisions and changes

## Configuration

Edit `config/ralph.json` to customize:

```json
{
  "vibe_kanban": {
    "executor": "CLAUDE_CODE",
    "model": "claude-sonnet-4.5",
    "project_id": "your-project-uuid-here"
  },
  "paths": {
    "brd": "plans/brd.md",
    "prd": "plans/generated-prd.md",
    "tasks": "plans/tasks.json"
  }
}
```

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/ralph-copilot.git
   cd ralph-copilot
   ```

2. **Ensure GitHub Copilot CLI is installed**
   ```bash
   copilot --version
   ```

3. **Configure Vibe-Kanban** (optional)
   ```bash
   cp config/mcp-config.json ~/.copilot/mcp-config.json
   # Edit to add your vibe-kanban MCP server details
   ```

4. **Set your project ID** in `config/ralph.json`

## Usage Examples

### Complete Workflow Example

```bash
# 1. Generate PRD from BRD
ralph brd-prd plans/my-product.md
# Review and edit plans/generated-prd.md

# 2. Generate tasks from PRD
ralph prd-tasks plans/generated-prd.md
# Review and edit plans/tasks.json

# 3. Create tasks in Vibe-Kanban
ralph tasks-kanban plans/tasks.json
# Tasks now in Vibe-Kanban with kanban_ids

# 4. Start first batch of ready tasks
ralph run
# Workspace sessions start for tasks with no dependencies

# 5. Monitor progress in Vibe-Kanban dashboard
# (tasks update status as work progresses)

# 6. Start next batch when ready
ralph run
# Starts newly-ready tasks

# 7. Review completed tasks (optional)
ralph review plans/tasks.json
# Appends to docs/implementation-log.md

# 8. Cleanup completed work (optional)
ralph cleanup
# Archives tasks, adjusts dependencies, appends to docs/cleanup-log.md
```

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture, data schemas, CLI structure
- **[WORKFLOW.md](docs/WORKFLOW.md)** - Complete workflow guide with examples

## Troubleshooting

### MCP Permission Denied

If you see "Permission denied" when running `ralph tasks-kanban`:

**Problem**: Vibe-Kanban MCP requires permission approval, which can only happen in **interactive mode**.

**Solution**: Grant permission once (saved permanently):

1. Run Copilot in interactive mode:
   ```bash
   copilot
   ```

2. In the chat, type:
   ```
   Use vibe_kanban-list_projects to show all my projects
   ```

3. When prompted, approve the permission by typing `y`

4. After approval, `ralph tasks-kanban` will work!

**Alternative**: If you know your project name, add it to `config/ralph.json`:
```json
"vibe_kanban": {
  "project_name": "YourProjectName"
}
```

## Design Principles

1. **Markdown for Documents** - Human-readable, LLM-parseable, version-controllable
2. **Prompt-Based Integration** - Clean separation between Ralph and coding agents
3. **Skills in Project Scope** - Skills loaded natively by coding agents
4. **Living Status in Vibe-Kanban** - Single source of truth for task status
5. **Phase-Contextual Commands** - Clear workflow progression from BRD → PRD → Tasks → Execution

## Requirements

- Python 3.8+
- GitHub Copilot CLI
- Git
- Vibe-Kanban (optional, for task management)

## License

See [LICENSE](LICENSE) file.

## Contributing

Ralph is a work in progress. See [SUMMARY.md](SUMMARY.md) for current status and roadmap.

---

**Built with ❤️ for product teams who want to scale their development workflow.**
