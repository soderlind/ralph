```
╔════════════════════════════════════════════════════════════════╗
║       RALPH SDLC WRAPPER - COMPLETE WORKFLOW GUIDE             ║
╚════════════════════════════════════════════════════════════════╝
```

# Ralph SDLC Wrapper - Complete Workflow

End-to-end workflow for product development using Ralph + Vibe Kanban.

## 📝 Phase 1: BRD → PRD

### 📥 Input: Business Requirements Document (BRD)

Create a BRD in markdown format with business goals, market context, requirements, metrics, and constraints.

### 🔨 Command: Generate PRD

```bash
ralph brd-prd plans/my-brd.md
```

**Output**: `plans/generated-prd.md` (structured markdown PRD)

#### 📑 PRD Structure:
- Overview, JTBD, Acceptance Criteria
- User Flows, Page Flows
- Technical Constraints, Success Metrics

---

## 🎯 Phase 2: PRD → Tasks

### 📥 Input: PRD Markdown

The PRD generated in Phase 1.

### 🔨 Command: Generate Tasks

```bash
ralph prd-tasks plans/generated-prd.md
```

**Output**: `plans/tasks.json` (task breakdown with dependencies)

---

## 📊 Phase 3: Tasks → Vibe Kanban

### 📥 Input: tasks.json

The tasks generated in Phase 2.

### 🔨 Command: Create Tasks in Vibe Kanban

**Prompt Mode (Default - Recommended):**
```bash
# Generate prompt
ralph tasks-kanban plans/tasks.json

# Copy the output, then:
copilot
> [paste @ralph-tasks-kanban prompt]
> y  # Approve permissions
```

**Execute Mode (After permissions granted):**
```bash
ralph --execute tasks-kanban plans/tasks.json
```

#### ⚙️ What happens:

1. Resolves project name to ID via `vibe_kanban-list_projects`
2. Reads and validates tasks.json
3. Creates all tasks via `vibe_kanban-create_task` MCP
4. Reports results

**Output**: Tasks created in Vibe Kanban

---

## 🚀 Phase 4: Run Tasks (No Dependencies)

### 🔨 Command: Start Tasks

**Prompt Mode (Default):**
```bash
# Generate prompt
ralph run

# Copy and paste into:
copilot
> [paste @ralph-run prompt]
```

**Execute Mode:**
```bash
ralph --execute run
```

**YOLO Mode (Non-interactive):**
```bash
ralph --execute --yolo run
```

#### ⚙️ What happens:

1. Resolves project name to ID
2. Fetches all tasks from Vibe Kanban (live status)
3. Filters for `status='todo'` with no dependencies
4. Starts workspace sessions using `vibe_kanban-start_workspace_session` MCP
5. Reports started/failed sessions

> **📌 Note**: Always reads from Vibe Kanban (not tasks.json) — living status is in Vibe Kanban.

**Output**: Workspace sessions started for ready tasks

---

## 📋 Phase 5: Review Completed Work

### 🔨 Command: Review Tasks

**Prompt Mode (Default):**
```bash
# Generate prompt
ralph review

# Copy and paste into:
copilot
> [paste @ralph-task-review prompt]
```

**Execute Mode:**
```bash
ralph --execute review
```

#### ⚙️ What happens:

1. Filters tasks with `status='done'`
2. Invokes `@ralph-task-review` skill for each
3. **Appends** to `docs/implementation-log.md`

---

## 🧹 Phase 6: Cleanup

### 🔨 Command: Cleanup Completed Tasks

**Prompt Mode (Default):**
```bash
# Generate prompt
ralph cleanup

# Copy and paste into:
copilot
> [paste @ralph-cleanup-agent prompt]
```

**Execute Mode:**
```bash
ralph --execute cleanup
```

#### ⚙️ What happens:

1. Resolves project name to ID
2. Cross-references reviewed tasks with done tasks
3. Archives completed tasks to `plans/done/`
4. **Removes dependencies** on completed tasks in tasks.json
5. **Appends** to `docs/cleanup-log.md`
6. Runs `scripts/cleanup-worktrees.sh`

---

## 📚 Complete Example

### First-Time Workflow (Prompt Mode)

```bash
# ────────────────────────────────────────────────────────
# 1️⃣  Generate PRD from BRD (No MCP needed)
# ────────────────────────────────────────────────────────
ralph brd-prd plans/my-product-brd.md
# Output: plans/generated-prd.md

# ────────────────────────────────────────────────────────
# 2️⃣  Generate tasks from PRD (No MCP needed)
# ────────────────────────────────────────────────────────
ralph prd-tasks plans/generated-prd.md
# Output: plans/tasks.json

# ────────────────────────────────────────────────────────
# 3️⃣  Create tasks in Vibe Kanban (Prompt mode!)
# ────────────────────────────────────────────────────────
ralph tasks-kanban plans/tasks.json
# Copy the prompt, then:
copilot
> [paste prompt]
> y  # Approve vibe_kanban permissions

# ────────────────────────────────────────────────────────
# 4️⃣  Start ready tasks (Prompt mode!)
# ────────────────────────────────────────────────────────
ralph run
# Copy the prompt, then:
copilot
> [paste prompt]

# ────────────────────────────────────────────────────────
# 5️⃣  Review completed work (Prompt mode!)
# ────────────────────────────────────────────────────────
ralph review
# Copy the prompt, then:
copilot
> [paste prompt]

# ────────────────────────────────────────────────────────
# 6️⃣  Cleanup (Prompt mode!)
# ────────────────────────────────────────────────────────
ralph cleanup
# Copy the prompt, then:
copilot
> [paste prompt]
```

### Automation Workflow (Execute Mode - After Permissions Granted)

```bash
# ────────────────────────────────────────────────────────
# 1️⃣  Generate PRD from BRD
# ────────────────────────────────────────────────────────
ralph brd-prd plans/my-product-brd.md
# Output: plans/generated-prd.md

# ────────────────────────────────────────────────────────
# 2️⃣  Generate tasks from PRD
# ────────────────────────────────────────────────────────
ralph prd-tasks plans/generated-prd.md
# Output: plans/tasks.json

# ────────────────────────────────────────────────────────
# 3️⃣  Create tasks in Vibe Kanban (Execute mode!)
# ────────────────────────────────────────────────────────
ralph --execute tasks-kanban plans/tasks.json
# Output: Tasks created

# ────────────────────────────────────────────────────────
# 4️⃣  Start tasks with no dependencies (Execute mode!)
# ────────────────────────────────────────────────────────
ralph --execute run
# Output: Workspace sessions started

# ────────────────────────────────────────────────────────
# 5️⃣  Monitor progress in Vibe Kanban
# ────────────────────────────────────────────────────────
# (tasks automatically update status)

# ────────────────────────────────────────────────────────
# 6️⃣  Start next batch when ready (Execute mode!)
# ────────────────────────────────────────────────────────
ralph --execute run
# Output: Starts newly-ready tasks

# ────────────────────────────────────────────────────────
# 7️⃣  Review completed tasks (Execute mode!)
# ────────────────────────────────────────────────────────
ralph --execute review
# Output: docs/implementation-log.md (appended)

# ────────────────────────────────────────────────────────
# 8️⃣  Cleanup completed work (Execute mode!)
# ────────────────────────────────────────────────────────
ralph --execute cleanup
# Output: Archived, dependencies adjusted
```

---

## ⚙️ Configuration

### config/ralph.json

| Setting | Value |
|---------|-------|
| **Executor** | `CLAUDE_CODE` |
| **Model** | `claude-haiku-4.5` |
| **Project Name** | `ralph-copilot` (human-readable!) |
| **Setup Script** | `npm install` |
| **Dev Server** | `npm run dev` |
| **Cleanup Script** | `git worktree prune` |

```json
{
  "vibe_kanban": {
    "executor": "CLAUDE_CODE",
    "model": "claude-haiku-4.5",
    "project_name": "ralph-copilot",  // Changed from project_id!
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

---

## 🎓 Skills Used

| Skill | Purpose |
|-------|---------|
| **@ralph-brd-to-prd** | BRD → PRD markdown |
| **@ralph-prd-to-tasks** | PRD → tasks JSON |
| **@ralph-task-review** | Review completed tasks (append mode) |
| **@ralph-cleanup-agent** | Cleanup & archive (append mode) |

---

## 🔗 MCP Integration

Ralph uses **prompt-based MCP interaction**:

1. Ralph generates prompts
2. Coding agent executes MCP calls
3. Ralph parses responses and updates files

### 🛠️ MCP Tools Used

| Tool | Purpose |
|------|---------|
| `vibe_kanban-list_projects` | Get available projects |
| `vibe_kanban-create_task` | Create tasks |
| `vibe_kanban-list_tasks` | Get task status (live) |
| `vibe_kanban-start_workspace_session` | Start coding sessions |

---

## 🔑 Key Concepts

### 🔄 Living Status in Vibe Kanban

> **📌 Important**: Task status lives in Vibe Kanban, not in tasks.json.

| Artifact | Role |
|----------|------|
| **tasks.json** | **Initial definition** (created once) |
| **Vibe Kanban** | **Living system** (status updates in real-time) |
| **ralph run** | Always reads from Vibe Kanban |
| **ralph tasks-kanban** | Creates tasks and saves `kanban_id` for reference |

### 📊 Dependency Management

Tasks are started only when:

✓ Status is `todo`  
✓ No dependencies mentioned in task description  
✓ Workspace session can be started  

> `ralph run` can be called multiple times — it will always check the current state in Vibe Kanban and start newly-ready tasks.

---

## ✅ Next Steps

After initial setup:

1. Customize skills in `skills/` folder
2. Run `./scripts/sync-skills.sh` to sync changes
3. Set `project_id` in `config/ralph.json`
4. Follow the workflow above

---

```
╔════════════════════════════════════════════════════════════════╗
║                    Happy Building! 🚀                          ║
║         Let Ralph transform your product development           ║
╚════════════════════════════════════════════════════════════════╝
```
