# Ralph: SDLC Wrapper for Product Development

**Ralph** is an intelligent software development lifecycle orchestrator that transforms product requirements into executed code through a structured, LLM-powered workflow.

## What is Ralph?

Ralph automates the journey from **Business Requirements → Product Requirements → Implementation Tasks → Execution** using:

- **Markdown-based documentation** (human-readable, LLM-friendly)
- **AI-powered skill transformations** (BRD→PRD, PRD→Tasks)
- **Vibe-Kanban integration** (task management and workspace orchestration)
- **Prompt generator** (copy-paste ready commands, solves permission issues!)

---

## 🚀 Quick Start (No Complex Setup!)

Want to create tasks in Vibe-Kanban? Ralph generates the prompt for you:

```bash
# Generate a prompt
./ralph.py tasks-kanban plans/tasks.json

# Copy the output:
# @ralph-tasks-kanban create tasks from plans/tasks.json...

# Then run:
copilot
> [paste prompt here]
> y  # Approve permissions when asked
```

That's it! **No pre-setup, no permission headaches.** Ralph shows you what to run.

---

## 📋 Prerequisites

Before using Ralph, ensure you have:

### Required

1. **Python 3.8+** 
   ```bash
   python3 --version  # Should show 3.8 or higher
   ```

2. **GitHub Copilot CLI** 
   ```bash
   # Install globally
   npm install -g @githubnext/github-copilot-cli
   
   # Verify installation
   copilot --version
   ```

3. **Git** 
   ```bash
   git --version  # Should be installed
   ```

4. **Vibe-Kanban (Local Setup)**
   - Run locally: `npx vibe-kanban` or `npm run vibe-kanban`
   - Opens at http://localhost:3000
   - Create a project (you'll need the project name)
   - MCP server configured (see Setup Step 2)

5. **GitHub Copilot Subscription**
   - Required for Copilot CLI to work
   - Individual or Business plan

### Optional
- **npx** (comes with Node.js) - For running Vibe-Kanban MCP
- **jq** - For JSON parsing in shell scripts

---

## 🚀 Setup (Step-by-Step)

### Step 1: Install Ralph

```bash
# Clone the repository
git clone https://github.com/ans4175/ralph-copilot.git
cd ralph-copilot

# Make ralph.py executable
chmod +x ralph.py

# Test installation
./ralph.py --help

# Optional: Add alias to your shell profile (~/.bashrc or ~/.zshrc)
alias ralph="python3 /path/to/ralph-copilot/ralph.py"
source ~/.bashrc  # or ~/.zshrc
```

### Step 2: Configure Vibe-Kanban MCP Server

Ralph uses Vibe-Kanban MCP for task management. Configure it once:

#### 2.1 Create/Find your MCP config file

```bash
# For GitHub Copilot CLI:
mkdir -p ~/.copilot
touch ~/.copilot/mcp-config.json

# For Claude Desktop (optional):
mkdir -p ~/.claude
touch ~/.claude/mcp-config.json
```

#### 2.2 Add vibe-kanban MCP server configuration

Open `~/.copilot/mcp-config.json` and add:

```json
{
  "mcpServers": {
    "vibe-kanban": {
      "command": "npx",
      "args": ["-y", "vibe-kanban@latest", "--mcp"],
      "env": {}
    }
  }
}
```

**Note:** If you already have other MCP servers configured, just add the `vibe-kanban` entry to your existing `mcpServers` object.

**Reference**: See `config/mcp-config.json` in this repo for a complete example.

### Step 3: Grant MCP Permissions (CRITICAL!)

**This is a one-time setup that MUST be done before Ralph can work!**

Vibe-Kanban MCP requires permission approval. This can ONLY be done in interactive Copilot mode:

```bash
# 1. Start Copilot in interactive mode
copilot

# 2. In the chat, type exactly this:
Use vibe_kanban-list_projects to show all my projects

# 3. You'll see a permission prompt like:
#    "vibe-kanban wants to use vibe_kanban-list_projects. Allow? (y/n)"
# 
# 4. Type: y (and press Enter)
#    Permission is saved permanently in ~/.copilot/permissions.json
#
# 5. You should see your Vibe-Kanban projects listed
#
# 6. Type: exit (to quit Copilot)
```

**Why is this needed?** MCP tools require explicit user permission for security. Ralph cannot grant permissions automatically - it can only be done in interactive mode.

**Troubleshooting:**
- If you don't see a permission prompt, the MCP server might not be configured correctly (check Step 2)
- If permission is denied, you'll need to manually edit `~/.copilot/permissions.json`
- Run `copilot -v` to see MCP server connection logs

### Step 4: Configure Ralph for Your Project

Edit `config/ralph.json` in the ralph-copilot directory:

```json
{
  "project_name": "ralph-sdlc-wrapper",
  "version": "0.1.0",
  "vibe_kanban": {
    "project_name": "your-project-name",  // ← SET THIS to your Vibe-Kanban project name
    "executor": "CLAUDE_CODE",             // Coding agent (CLAUDE_CODE, COPILOT, etc.)
    "model": "claude-sonnet-4.5"           // Default LLM model
  },
  "paths": {
    "brd": "plans/brd.md",
    "prd": "plans/generated-prd.md",
    "tasks": "plans/tasks.json",
    "implementation_log": "docs/implementation-log.md",
    "cleanup_log": "docs/cleanup-log.md",
    "archive_dir": "plans/done"
  }
}
```

**To find your Vibe-Kanban project name:**
```bash
# List all projects
copilot -p "Use vibe_kanban-list_projects to show all projects"

# Or start Vibe-Kanban UI
npm run vibe-kanban
```

### Step 5: Sync Skills to Project Scope

Ralph uses agentic skills that need to be synced to your project:

```bash
# Run the sync script (from ralph-copilot directory)
./scripts/sync-skills.sh
# Or use npm:
npm run sync-skills

# This copies skills/ to:
#   - .copilot/skills/  (for Copilot CLI)
#   - .claude/skills/   (for Claude Desktop)

# You should see:
# ✨ Skills synced successfully!
#   - ralph-brd-to-prd
#   - ralph-prd-to-tasks
#   - ralph-tasks-kanban
#   - ralph-run
#   - ralph-task-review
#   - ralph-cleanup-agent
```

**Note:** Re-run this script whenever you update skill files.

### Step 5.5: Optional - Set Up Vibe-Kanban UI (Dashboard)

If you want to run Vibe-Kanban UI locally to view your projects and tasks in a dashboard:

```bash
# Start Vibe-Kanban UI
npm run vibe-kanban

# In another terminal, you can now view your Vibe-Kanban dashboard
# Create tasks, view progress, manage workspaces

# When done, stop the UI:
npm run stop-vibe-kanban
# Or manually: Ctrl+C in the terminal where it's running
```

**Requirements for Vibe-Kanban UI:**
- Node.js 16+ (comes with `npx`)
- No cloud account needed - runs locally

**Note:** The Vibe-Kanban UI is optional. You don't need it to use Ralph - you can manage tasks entirely through Copilot CLI and MCP tools.

### Step 6: Verify Setup (Test End-to-End)

Let's verify everything works:

```bash
# 1. Check ralph.py runs
./ralph.py --help

# 2. Test prompt generator (NEW DEFAULT!)
./ralph.py tasks-kanban test-tasks.json
# ✓ Should show a formatted prompt to copy-paste
# ✓ Copy the @ralph-tasks-kanban prompt

# 3. Run copilot and paste
copilot
> [paste the prompt from step 2]
> y  # Approve permissions
# ✓ Should create task in Vibe-Kanban

# 4. View tasks in Vibe-Kanban UI
npm run vibe-kanban
# ✓ You should see your test task in the project

# 5. Test execute mode (after permissions granted)
./ralph.py --execute tasks-kanban test-tasks.json
# ✓ Should execute immediately
```

If all steps succeed, Ralph is ready to use! 🎉

---

## 🛠️ Common Commands

Ralph provides both shell scripts and npm commands for common operations:

### Ralph Workflow Commands

```bash
# Display help
./ralph.py --help
npm run ralph:help

# Transform BRD to PRD
./ralph.py brd plans/my-brd.md
npm run ralph:brd -- plans/my-brd.md

# Transform PRD to Tasks
./ralph.py prd plans/my-prd.md
npm run ralph:prd -- plans/my-prd.md

# Create tasks in Vibe-Kanban
./ralph.py tasks-kanban plans/tasks.json
npm run ralph:tasks -- plans/tasks.json

# Start workspace sessions
./ralph.py run
npm run ralph:run

# Review completed tasks
./ralph.py review
npm run ralph:review

# Archive and cleanup tasks
./ralph.py cleanup
npm run ralph:cleanup
```

### Advanced Commands (with --execute)

```bash
# Execute directly (requires permissions granted)
./ralph.py --execute tasks-kanban plans/tasks.json

# Non-interactive mode (for CI/CD)
./ralph.py --execute --yolo run
```

### Maintenance Commands

```bash
# Sync skills to project scope
./scripts/sync-skills.sh
npm run sync-skills

# Clean up git worktrees
./scripts/cleanup-worktrees.sh
npm run cleanup-worktrees

# Force cleanup (skip confirmation)
./scripts/cleanup-worktrees.sh -f
npm run cleanup-worktrees:force

# Start Vibe-Kanban UI dashboard
npm run vibe-kanban

# Stop Vibe-Kanban UI (if running)
npm run stop-vibe-kanban
```

### Using npm Scripts

All commands can be run with `npm run`:

```bash
npm run ralph:help        # Show ralph help
npm run ralph:brd -- <file>      # Create PRD from BRD
npm run ralph:prd -- <file>      # Create tasks from PRD
npm run ralph:tasks -- <file>    # Create Kanban tasks
npm run ralph:run         # Start workspaces
npm run ralph:review      # Review completed tasks
npm run ralph:cleanup     # Archive tasks
npm run sync-skills       # Sync skills to project scope
npm run vibe-kanban       # Start Vibe-Kanban UI
npm run stop-vibe-kanban  # Stop Vibe-Kanban UI
```

---

## 📖 Two Ways to Use Ralph

Ralph has **two modes** to fit different workflows:

### 1. Prompt Mode (Default - Recommended for First-Time)

**What it does:** Generates copy-paste ready prompts for Copilot CLI

```bash
# Shows formatted prompt
./ralph.py tasks-kanban plans/tasks.json

# Output:
# ╭──────────────────────────────────────────────────╮
# │ 📋 Copy this prompt into Copilot CLI:            │
# ╰──────────────────────────────────────────────────╯
#
# @ralph-tasks-kanban create tasks from...
#
# [Instructions for use]

# Then run:
copilot
> [paste prompt]
```

**Best for:**
- ✅ First-time users (solves permission issues!)
- ✅ Learning how skills work
- ✅ Debugging (you can modify prompts)
- ✅ Sharing commands with team

### 2. Execute Mode (For Automation)

**What it does:** Runs commands immediately (requires permissions already granted)

```bash
# Execute directly
./ralph.py --execute tasks-kanban plans/tasks.json

# Non-interactive (CI/CD)
./ralph.py --execute --yolo run
```

**Best for:**
- ✅ Automation scripts
- ✅ CI/CD pipelines
- ✅ Repeated tasks (after initial setup)
- ✅ Power users who have granted permissions

**Note:** If you see permission errors, switch to prompt mode!

---

## 🎯 Quick Start Guide

### Example: Build a Simple Todo App

Let's walk through creating a simple todo app from scratch.

#### Step 1: Create a BRD (Business Requirements Document)

Create `plans/todo-app-brd.md`:

```markdown
# Todo App - Business Requirements

## Business Goals
- Help users track their daily tasks
- Simple, fast, no login required
- Works on any device

## Market Context
- Target: Busy professionals
- Competition: Todoist, Any.do (too complex)
- Our edge: Simplicity

## High-Level Requirements
- Add new todos
- Mark todos as complete
- Delete completed todos
- Persist data in browser

## Success Metrics
- User can add 5 todos in under 30 seconds
- Zero load time (client-side only)

## Constraints
- Must work offline
- No backend/database
- Under 100 lines of code
```

#### Step 2: Transform BRD → PRD

```bash
python ralph.py brd-prd plans/todo-app-brd.md
```

**What happens:**
- Ralph reads your BRD
- Uses AI to create a detailed Product Requirements Document
- Saves to `plans/generated-prd.md`
- Shows you the output

**Output example**: `plans/generated-prd.md` will contain:
- Jobs To Be Done (JTBD)
- Acceptance Criteria
- User Flows
- Technical Constraints
- Success Metrics

#### Step 3: Break PRD → Tasks

```bash
python ralph.py prd-tasks plans/generated-prd.md
```

**What happens:**
- Ralph reads the PRD
- Uses AI to break it into atomic implementation tasks
- Identifies dependencies between tasks
- Saves to `plans/tasks.json`

**Output example**: `plans/tasks.json` will contain:
```json
[
  {
    "id": "TASK-001",
    "description": "Create HTML structure",
    "dependencies": [],
    ...
  },
  {
    "id": "TASK-002",
    "description": "Add todo functionality",
    "dependencies": ["TASK-001"],
    ...
  }
]
```

#### Step 4: Create Tasks in Vibe-Kanban

```bash
python ralph.py tasks-kanban plans/tasks.json
```

**What happens:**
- Ralph checks if Vibe-Kanban MCP is running
- Prompts you to select a project (or uses configured project_name)
- Creates all tasks in Vibe-Kanban with their dependencies
- View tasks: `npm run vibe-kanban`

**Interactive**: If no project_name is set, you'll be asked to select:
```
Available projects:
1. MyProject
2. AnotherProject

Type the project name:
```

#### Step 5: Start Ready Tasks

```bash
python ralph.py run
```

**What happens:**
- Ralph fetches all TODO tasks from Vibe-Kanban
- Filters tasks with Ralph IDs (TASK-001, TASK-002, etc.)
- Identifies tasks with no dependencies
- Starts workspace sessions for ready tasks
- Coding agents begin implementing them in parallel

**Progressive Execution**: Call `ralph run` multiple times as tasks complete:
```bash
# First run: starts TASK-001, TASK-002 (no dependencies)
python ralph.py run

# Wait for completion...

# Second run: starts TASK-003 (depends on TASK-001, TASK-002)
python ralph.py run
```

#### Step 6: Review Completed Work

```bash
python ralph.py review
```

**What happens:**
- Fetches all DONE tasks from Vibe-Kanban
- Generates implementation summaries
- Appends to `docs/implementation-log.md`
- Auto-runs cleanup (removes from Vibe-Kanban, archives locally)

**Optional**: Review without cleanup:
```bash
python ralph.py review --no-cleanup
```

#### Step 7: Cleanup (Optional, if not auto-cleaned)

```bash
python ralph.py cleanup
```

**What happens:**
- Only processes tasks that were reviewed (in implementation-log.md)
- Archives completed tasks to `plans/done/`
- Removes dependencies from remaining tasks
- Cleans up git worktrees
- Deletes from Vibe-Kanban
- Appends to `docs/cleanup-log.md`

---

## 📖 The Complete Workflow

```
┌─────────────┐
│   BRD.md    │  Business requirements in markdown
│  (Manual)   │
└──────┬──────┘
       │ ralph brd-prd
       ▼
┌─────────────┐
│   PRD.md    │  Product requirements with acceptance criteria
│  (Generated)│
└──────┬──────┘
       │ ralph prd-tasks
       ▼
┌─────────────┐
│ tasks.json  │  Atomic tasks with dependencies
│  (Generated)│
└──────┬──────┘
       │ ralph tasks-kanban
       ▼
┌─────────────┐
│ Vibe Kanban │  Tasks created as kanban cards
│  (Living)   │
└──────┬──────┘
       │ ralph run (multiple times)
       ▼
┌─────────────┐
│  Workspace  │  Coding agents implement tasks
│  Sessions   │
└──────┬──────┘
       │ ralph review
       ▼
┌─────────────┐
│   Done &    │  Implementation log + cleanup
│  Archived   │
└─────────────┘
```

---

## 📚 Command Reference

### `ralph brd-prd <brd-file>`

Transform Business Requirements into Product Requirements Document.

**Input**: Markdown file with business goals, market context, requirements  
**Output**: `plans/generated-prd.md` (or custom path)  
**AI Skill**: `@ralph-brd-to-prd`

**Example**:
```bash
python ralph.py brd-prd plans/my-feature-brd.md

# Custom output path
python ralph.py brd-prd plans/my-feature-brd.md plans/custom-prd.md
```

---

### `ralph prd-tasks <prd-file>`

Break Product Requirements into atomic implementation tasks.

**Input**: Markdown PRD file  
**Output**: `plans/tasks.json` with tasks and dependencies  
**AI Skill**: `@ralph-prd-to-tasks`

**Example**:
```bash
python ralph.py prd-tasks plans/generated-prd.md

# Custom output path
python ralph.py prd-tasks plans/my-prd.md plans/custom-tasks.json
```

**Output Structure**:
```json
[
  {
    "id": "TASK-001",
    "category": "setup",
    "description": "Create project structure",
    "details": "...",
    "steps": ["Step 1", "Step 2"],
    "acceptance": ["Criteria 1", "Criteria 2"],
    "dependencies": [],
    "priority": 1,
    "status": "todo"
  }
]
```

---

### `ralph tasks-kanban [tasks-file]`

Create tasks in Vibe-Kanban from tasks.json.

**Input**: `plans/tasks.json` (default) or custom path  
**Output**: Tasks created in Vibe-Kanban  
**MCP**: Uses `vibe_kanban-create_task`

**Example**:
```bash
# Use default tasks.json location
python ralph.py tasks-kanban

# Custom tasks file
python ralph.py tasks-kanban plans/my-tasks.json
```

**What it does**:
1. Checks Vibe-Kanban MCP is running
2. Lists available projects (or uses configured project_name)
3. Prompts you to select project (if needed)
4. Creates all tasks with dependencies
5. Shows Vibe-Kanban URL

**Interactive**:
- If `project_name` not set in config, you'll be prompted to select
- Permission approval required on first use (see Troubleshooting)

---

### `ralph run`

Start workspace sessions for ready tasks (no dependencies).

**Input**: Fetches tasks from Vibe-Kanban (status=todo)  
**Output**: Starts coding agent workspace sessions  
**MCP**: Uses `vibe_kanban-list_tasks`, `vibe_kanban-start_workspace_session`

**Example**:
```bash
# Start ready tasks
python ralph.py run

# Call again after some tasks complete
python ralph.py run
```

**How it works**:
1. Fetches all TODO tasks from Vibe-Kanban
2. Filters tasks with Ralph IDs (TASK-001, TASK-002, etc.)
3. Parses dependencies from task descriptions
4. Starts tasks with no unmet dependencies
5. Respects `max_parallel_tasks` config (default: 3)

**Progressive Execution**:
```bash
# Round 1: Starts TASK-001, TASK-002 (no dependencies)
python ralph.py run

# ... wait for completion ...

# Round 2: Starts TASK-003 (depends on TASK-001)
python ralph.py run

# ... wait for completion ...

# Round 3: Starts TASK-004 (depends on TASK-002, TASK-003)
python ralph.py run
```

---

### `ralph review [--no-cleanup]`

Review completed tasks and optionally cleanup.

**Input**: Fetches DONE tasks from Vibe-Kanban  
**Output**: Appends to `docs/implementation-log.md`  
**AI Skill**: `@ralph-task-review`

**Example**:
```bash
# Review and auto-cleanup
python ralph.py review

# Review only (no cleanup)
python ralph.py review --no-cleanup
```

**What it does**:
1. Fetches DONE tasks from Vibe-Kanban
2. Filters tasks with Ralph IDs
3. Generates implementation summaries
4. Appends to `docs/implementation-log.md`
5. Auto-runs cleanup (unless `--no-cleanup`)

---

### `ralph cleanup`

Cleanup reviewed tasks (archive, remove dependencies, delete from Vibe-Kanban).

**Input**: Reads `docs/implementation-log.md` for reviewed task IDs  
**Output**: Appends to `docs/cleanup-log.md`  
**AI Skill**: `@ralph-cleanup-agent`

**Example**:
```bash
python ralph.py cleanup
```

**What it does**:
1. Reads reviewed task IDs from `docs/implementation-log.md`
2. Archives tasks to `plans/done/tasks-{timestamp}.json`
3. Removes completed task IDs from remaining tasks' dependencies
4. Runs `scripts/cleanup-worktrees.sh`
5. Deletes tasks from Vibe-Kanban
6. Appends to `docs/cleanup-log.md`

**Safety**: Only processes tasks that are:
- Listed in `docs/implementation-log.md` (reviewed)
- In DONE status in Vibe-Kanban

---

## 📁 Project Structure

```
ralph-copilot/
├── ralph.py                     # Main CLI entry point
├── README.md                    # This file
├── LICENSE
│
├── config/
│   ├── ralph.json              # Main configuration
│   └── mcp-config.json         # Vibe-Kanban MCP boilerplate
│
├── docs/
│   ├── ARCHITECTURE.md         # Technical architecture & schemas
│   ├── WORKFLOW.md             # Complete workflow guide
│   ├── implementation-log.md   # Auto-generated (task reviews)
│   └── cleanup-log.md          # Auto-generated (cleanup summaries)
│
├── lib/
│   └── vibe_kanban_client.py   # Vibe-Kanban MCP prompt generator
│
├── skills/                     # AI skills for transformations
│   ├── ralph-brd-to-prd/
│   │   └── skill.md            # BRD → PRD transformation
│   ├── ralph-prd-to-tasks/
│   │   └── skill.md            # PRD → Tasks breakdown
│   ├── ralph-task-review/
│   │   └── skill.md            # Task review & summary
│   └── ralph-cleanup-agent/
│       └── skill.md            # Cleanup & dependency adjustment
│
├── scripts/
│   ├── sync-skills.sh          # Sync skills to project scope
│   └── cleanup-worktrees.sh    # Git worktree cleanup utility
│
└── plans/                      # Your project files
    ├── done/                   # Archived completed tasks
    ├── tasks.json              # Generated tasks (if exists)
    └── *.md                    # Your BRDs and PRDs
```

---

## ⚙️ Configuration

### `config/ralph.json`

Main configuration file with all Ralph settings:

```json
{
  "project_name": "ralph-sdlc-wrapper",
  "version": "0.1.0",
  
  "vibe_kanban": {
    "project_name": null,           // Set to auto-select Vibe-Kanban project
    "executor": "CLAUDE_CODE",      // Default coding agent
    "model": "claude-sonnet-4.5",   // Default model
    "repo_config": {
      "base_branch": "main",
      "setup_script": "",
      "cleanup_script": "",
      "dev_server_script": ""
    }
  },
  
  "task_defaults": {
    "categories": ["setup", "functional", "documentation", "testing"],
    "default_category": "functional"
  },
  
  "execution": {
    "max_parallel_tasks": 3,       // Max tasks to run simultaneously
    "poll_interval_seconds": 30,
    "max_retries": 3
  },
  
  "paths": {
    "brd": "plans/input-brd.md",
    "prd": "plans/generated-prd.md",
    "tasks": "plans/tasks.json",
    "implementation_log": "docs/implementation-log.md",
    "cleanup_log": "docs/cleanup-log.md",
    "archive_dir": "plans/done"
  },
  
  "skills": {
    "ralph-brd-to-prd": {
      "path": "skills/ralph-brd-to-prd",
      "model": "claude-sonnet-4.5",
      "temperature": 0.7
    },
    "ralph-prd-to-tasks": {
      "path": "skills/ralph-prd-to-tasks",
      "model": "claude-sonnet-4.5",
      "temperature": 0.5
    }
  }
}
```

**Key Settings**:
- `vibe_kanban.project_name`: Set this to auto-select your Vibe-Kanban project
- `execution.max_parallel_tasks`: Control how many tasks run simultaneously
- `paths.*`: Customize where files are saved

---

## 🔧 Troubleshooting

### Problem: "Permission denied" when running `ralph tasks-kanban`

**Symptom**:
```
❌ Permission denied for vibe_kanban MCP
💡 Please grant permission when prompted by Copilot
```

**Root Cause**: Vibe-Kanban MCP requires permission approval, which can only happen in **interactive mode**.

**Solution** (one-time setup):

1. Start Copilot interactively:
   ```bash
   copilot
   ```

2. In the chat, type:
   ```
   Use vibe_kanban-list_projects to show all my projects
   ```

3. When prompted, approve the permission:
   ```
   ⚠️  MCP Tool Permission Request
       Tool: vibe_kanban-list_projects
       Server: vibe-kanban
   
       Allow this tool? [y/N]: y
   ```

4. Permission is saved permanently! Now exit:
   ```
   exit
   ```

5. Try `ralph tasks-kanban` again - it should work now!

**Alternative**: If you know your project name, add it to `config/ralph.json`:
```json
"vibe_kanban": {
  "project_name": "YourProjectName"
}
```

---

### Problem: "No valid Ralph tasks found"

**Symptom**:
```
💡 No valid Ralph tasks found in todo status
   Tasks created by ralph should have IDs like TASK-001, TASK-002, etc.
```

**Cause**: Ralph only processes tasks with IDs matching the pattern `TASK-001`, `TASK-002`, etc.

**Solution**:
- Ensure your tasks.json has proper IDs
- Run `ralph tasks-kanban` to create tasks with correct IDs
- Tasks created manually in Vibe-Kanban without Ralph IDs are skipped (by design)

---

### Problem: Tasks not starting (dependencies)

**Symptom**: `ralph run` says no ready tasks, but you see TODO tasks in Vibe-Kanban

**Cause**: Tasks have unmet dependencies

**Solution**:
1. Check task descriptions for dependency mentions:
   ```
   Depends on: TASK-001, TASK-002
   ```
2. Complete those tasks first
3. Run `ralph run` again - dependent tasks will start automatically

---

### Problem: "Vibe-Kanban MCP not running"

**Symptom**:
```
❌ vibe-kanban MCP may not be running
💡 Please ensure vibe-kanban MCP is configured
```

**Solution**:
1. Check your MCP config file exists:
   ```bash
   cat ~/.copilot/mcp-config.json
   # or
   cat ~/.claude/mcp-config.json
   ```

2. Ensure vibe-kanban is configured:
   ```json
   {
     "vibe-kanban": {
       "command": "npx",
       "args": ["-y", "vibe-kanban@latest", "--mcp"]
     }
   }
   ```

3. Restart your Copilot CLI or coding environment

---

## 🎯 Key Concepts

### Living Status in Vibe-Kanban
- **tasks.json**: Initial task definitions (created once, becomes stale)
- **Vibe-Kanban**: Living status (real-time, always current)
- **ralph run**: Always reads from Vibe-Kanban, never tasks.json
- This enables progressive execution - call `ralph run` multiple times

### Task ID Filtering
Ralph only processes tasks with IDs like `TASK-001`, `TASK-002`:
- ✅ `TASK-001: Create database` → Ralph will process
- ✅ `FEATURE-042: Add API` → Ralph will process  
- ❌ `Fix homepage bug` → Ralph will skip (no ID)
- ❌ `Update docs` → Ralph will skip (no ID)

This prevents Ralph from starting or cleaning tasks you created manually.

### Progressive Execution
```bash
# Round 1: Start tasks with no dependencies
ralph run
# Output: Started TASK-001, TASK-002

# ... wait for completion ...

# Round 2: Start tasks that depended on TASK-001, TASK-002
ralph run
# Output: Started TASK-003 (was waiting for TASK-001)

# Round 3: Continue until all done
ralph run
# Output: No ready tasks (all done or waiting)
```

### Append-Only Logging
- `docs/implementation-log.md`: Appended by `ralph review`
- `docs/cleanup-log.md`: Appended by `ralph cleanup`
- History is never lost, only added to
- Each entry is timestamped

---

## 📖 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture, data schemas, CLI structure
- **[WORKFLOW.md](docs/WORKFLOW.md)** - Complete workflow guide with examples
- **[SUMMARY.md](SUMMARY.md)** - Implementation status and changelog

---

## 💡 Design Principles

1. **Markdown for Documents** - Human-readable, LLM-parseable, version-controllable
2. **Prompt-Based Integration** - Clean separation between Ralph and coding agents
3. **Skills in Project Scope** - Skills loaded natively by coding agents
4. **Living Status in Vibe-Kanban** - Single source of truth for task status
5. **Phase-Contextual Commands** - Clear workflow progression from BRD → PRD → Tasks → Execution

---

## 📦 Requirements

- Python 3.8+
- GitHub Copilot CLI (`npm install -g @githubnext/github-copilot-cli`)
- Git
- Vibe-Kanban MCP (configured in MCP settings)
- GitHub account with Copilot subscription

---

## 📝 License

See [LICENSE](LICENSE) file.

---

## 🤝 Contributing

Ralph is a work in progress. See [SUMMARY.md](SUMMARY.md) for current status and roadmap.

---

## 🙏 Acknowledgments

Inspired by [Per Soderlind's AI-driven SDLC approach](https://gist.github.com/soderlind/ca83ba5417e3d9e25b68c7bdc644832c). While Ralph is a completely new implementation with a different architecture, we're grateful for the conceptual foundation his work provided. See [CREDITS.md](CREDITS.md) for full attribution and details on what we borrowed vs. what we built differently.

---

**Built with ❤️ for product teams who want to scale their development workflow.**
