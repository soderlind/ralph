# Credits & Attribution

## Original Inspiration

This project was inspired by **Per Soderlind's** innovative approach to AI-driven software development lifecycle (SDLC) automation, originally documented in his gist:

**📎 https://gist.github.com/soderlind/ca83ba5417e3d9e25b68c7bdc644832c**

Per's work demonstrated how AI assistants could be orchestrated through structured workflows to automate the journey from requirements to implementation. His vision of dependency-driven task execution and continuous automation cycles provided the conceptual foundation for Ralph.

---

## Important Clarification

**This is a fork but inspired only** of the repository at https://github.com/soderlind/ralph.

This Ralph was built from scratch with a completely different architecture, implementation approach, and technology stack. While we share similar goals and were inspired by the same vision, the codebases are independent.

---

## What We Borrowed

We adopted several key **concepts** from Per Soderlind's original design:

### 1. Task JSON Structure
The format for representing tasks with metadata (title, description, dependencies, status) that integrates cleanly with kanban systems. This structured approach makes tasks both human-readable and machine-parseable.

### 2. Dependency-Based Execution Model
The idea that tasks should be executed based on their dependency graph rather than arbitrary order. Tasks with no blocking dependencies can run in parallel, while dependent tasks wait for prerequisites to complete.

### 3. Continuous Review-Done-Run Cycle
The workflow pattern where completed tasks are reviewed, marked as done, which then unblocks new tasks that can be automatically detected and run. This creates a self-sustaining automation loop.

### 4. AI as Orchestrator
The vision that AI assistants should not just write code, but orchestrate the entire development lifecycle from requirements to implementation to documentation.

---

## What We Built Differently

Ralph takes a **completely new approach** to implementing these concepts:

### 1. Dual-Mode Architecture (Prompt + Execute)
**Our innovation:** Ralph defaults to **prompt generation mode**, creating formatted prompts that users paste into GitHub Copilot CLI. This solves MCP permission issues naturally while providing transparency and debugging capability.

```bash
# Default: Generate prompt (user pastes into copilot)
./ralph.py tasks-kanban plans/tasks.json

# Optional: Direct execution for automation
./ralph.py --execute tasks-kanban plans/tasks.json
```

**Original approach:** Direct execution only.

### 2. Markdown-First Workflow
**Our innovation:** Human-readable markdown documents drive the entire process:
- **BRD** (Business Requirements Document) → Markdown
- **PRD** (Product Requirements Document) → Markdown  
- **Tasks** → JSON (only at the kanban integration layer)

This makes requirements version-controllable, reviewable, and LLM-friendly.

**Original approach:** Different document formats and structures.

### 3. Agentic Skills System
**Our innovation:** Workflow steps are implemented as **agentic skills** - markdown-based AI instruction sets that live in `.copilot/skills/` and `.claude/skills/` directories. Skills are portable, versionable, and work across AI platforms.

Examples:
- `ralph-brd-to-prd` - Transform BRD → PRD
- `ralph-prd-to-tasks` - Break PRD → Tasks
- `ralph-run` - Execute ready tasks
- `ralph-task-review` - Review completed work
- `ralph-cleanup-agent` - Archive and cleanup

**Original approach:** Different implementation mechanism.

### 4. Local Vibe-Kanban Integration
**Our innovation:** Ralph integrates with **local Vibe-Kanban** (`npx vibe-kanban`) running. No cloud account needed, full data control, works offline.

The MCP server provides tools for project management, task creation, workspace orchestration, and dependency resolution.

**Original approach:** Different kanban/task management approach.

### 5. Git Worktree-Based Parallel Execution
**Our innovation:** Each task gets its own git worktree (`vibe-kanban-TASK-XXX/`), enabling true parallel development without branch conflicts. Multiple tasks can be actively developed simultaneously.

**Original approach:** Different workspace management.

### 6. Comprehensive Phase System
**Our innovation:** Six distinct phases with clear inputs/outputs:

```
Phase 1: BRD → PRD         (AI skill transformation)
Phase 2: PRD → Tasks       (AI skill breakdown)
Phase 3: Tasks → Kanban    (MCP integration)
Phase 4: Run               (Workspace orchestration)
Phase 5: Review            (Implementation summaries)
Phase 6: Cleanup           (Archive & delete)
```

Each phase is independently testable and can be run in isolation or as part of the full pipeline.

---

## Technology Stack Comparison

### Ralph's Stack:
- **Language:** Python 3.8+
- **AI Platform:** GitHub Copilot CLI (with Claude support)
- **Task Management:** Vibe-Kanban (local MCP server)
- **Skills:** Markdown-based agentic workflows
- **Version Control:** Git worktrees for parallel execution
- **Documents:** Markdown (BRD, PRD), JSON (tasks)

### Original Concept:
Different technology choices and implementation approach.

---

## Design Philosophy Differences

### Ralph's Philosophy:
1. **Transparency First** - Users see what will happen before it executes (prompt mode)
2. **Human-in-the-Loop** - Copy-paste workflow keeps humans engaged
3. **Tool Agnostic** - Works with any AI that supports skills (Copilot, Claude)
4. **Local First** - No cloud dependencies, full data control
5. **Git Native** - Everything versioned, reviewable, collaborative

### Shared Vision:
Both projects believe in AI-driven automation, structured workflows, and reducing manual SDLC overhead.

---

## License Compatibility

**Ralph:** MIT License (see [LICENSE](LICENSE))  
**Original Inspiration:** Check https://gist.github.com/soderlind/ca83ba5417e3d9e25b68c7bdc644832c for license terms

Both projects are open source, enabling community collaboration and innovation.

---

## Thank You

**Per Soderlind**, thank you for pioneering this vision of AI-driven SDLC automation. Your work opened our eyes to what's possible when we stop using AI as just a code assistant and start orchestrating it through structured workflows.

Your approach to dependency graphs, continuous automation, and task-driven development directly inspired Ralph's architecture. While we took different implementation paths, we share the same goal: **making software development more efficient, consistent, and enjoyable**.

---

## Community

If you're interested in AI-driven SDLC automation:

- **Ralph (this project):** https://github.com/ans4175/ralph-copilot
- **Original inspiration:** https://gist.github.com/soderlind/ca83ba5417e3d9e25b68c7bdc644832c
- **Per Soderlind's work:** https://github.com/soderlind

We encourage you to explore both approaches and choose (or build!) what works best for your team.

---

## Contributing

Have ideas for improving Ralph? We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Found this approach useful? Consider:
- ⭐ Starring this repository
- 📣 Sharing with your team
- 🐛 Reporting bugs and suggesting features
- 🤝 Contributing code or documentation

---

**Last Updated:** 2026-02-01
