# RFC: Ralph - AI-First SDLC Wrapper

**Status:** Implemented  
**Author:** ans4175  
**Created:** 2026-01-31  
**Type:** Design Document

---

## 1. The Problem

Building software involves repetitive steps that AI assistants can help with, but most teams face these issues:

1. **Scattered workflows** - Ideas live in docs, tasks in Jira, code in GitHub, coordination in Slack
2. **Context switching** - Developers constantly jump between tools and lose flow state
3. **Inconsistent processes** - Each team member does things differently
4. **Manual handoffs** - Requirements → Tasks → Code requires lots of copying/pasting
5. **Lost knowledge** - When tasks finish, context disappears unless manually documented

Most project management tools are designed for *tracking* work, not *doing* work. We needed something different.

---

## 2. The Insight

**What if the AI assistant could understand the entire product lifecycle?**

Instead of just asking AI to "write a function" or "fix a bug," what if we could say:
- "Here's a business idea, turn it into a spec"
- "Break this spec into executable tasks"
- "Execute these tasks in the right order"
- "Document what was done"

The AI already has these skills. We just need to **orchestrate** them through a consistent workflow.

### Background & Inspiration

This vision was pioneered by **Per Soderlind** in his innovative work on AI-driven SDLC automation ([original gist](https://gist.github.com/soderlind/ca83ba5417e3d9e25b68c7bdc644832c)). His approach demonstrated how AI could be orchestrated through dependency graphs to automate software development cycles continuously.

Ralph builds on these foundational concepts—dependency-based task execution, continuous review-run cycles, and structured task representations—but implements them through a completely new architecture. Where the original focused on direct execution, Ralph introduces **prompt generation mode** as the default, making AI orchestration transparent and permission-friendly. We also added markdown-first workflows (BRD → PRD → Tasks), an agentic skills system, and local-first tooling with Vibe-Kanban.

While our implementation differs significantly, we're grateful for the conceptual foundation Per's work provided. See [CREDITS.md](../CREDITS.md) for detailed attribution.

---

## 3. The Solution: Ralph

Ralph is a **wrapper** around your existing tools that creates an AI-friendly SDLC pipeline:

```
Business Idea → Requirements → Tasks → Execution → Review → Archive
```

### Core Philosophy

1. **Documents as Input** - Start with human-readable markdown (BRDs, PRDs)
2. **AI as Executor** - Let AI do the mechanical work
3. **Version Control Everything** - All artifacts live in Git
4. **Skills Not Scripts** - Use reusable AI skills instead of hardcoded scripts
5. **Prompt-First Design** - Show users what will happen before it happens

### What Ralph Does

Ralph orchestrates AI through 6 stages:

1. **BRD → PRD** - Transform business ideas into technical requirements
2. **PRD → Tasks** - Break requirements into atomic work items with dependencies
3. **Tasks → Kanban** - Create tracked tasks in project management system
4. **Run** - Execute ready tasks automatically in isolated workspaces
5. **Review** - Generate implementation summaries from completed work
6. **Cleanup** - Archive artifacts, delete workspaces, maintain audit trail

Each stage is a **skill** that AI follows, not a script that runs.

---

## 4. Why This Approach?

### Alternative Approaches We Didn't Use

**Option A: Build a new project management tool**
- ❌ Adds another tool to learn
- ❌ Requires migration from existing systems
- ❌ Competes with established tools

**Option B: Create automation scripts**
- ❌ Brittle - breaks when tools change
- ❌ Hard to customize
- ❌ Not AI-native

**Option C: Just use AI chat directly**
- ❌ No consistency
- ❌ No workflow enforcement
- ❌ Lost context between sessions

### Why Ralph Works Better

**Wraps existing tools** - Integrates with Vibe-Kanban, GitHub Copilot, Git  
**AI-native** - Uses skills, not scripts, so AI can adapt  
**Transparent** - Shows prompts before execution (prompt mode)  
**Flexible** - Can run manually or automated (execute mode)  
**Auditable** - Everything is documented in Git

---

## 5. Key Design Decisions

### 5.1 Prompt Mode as Default

**Decision:** Ralph shows AI prompts by default instead of executing immediately.

**Why:**
- Solves MCP permission issues (permissions work in interactive Copilot)
- Users see what will happen before it happens
- Easy to modify prompts for edge cases
- Great for learning and debugging
- Safe by default

**Trade-off:** One extra step (copy-paste) vs immediate execution

### 5.2 Skills Over Scripts

**Decision:** Use AI skills (markdown instructions) instead of shell scripts.

**Why:**
- AI can read and adapt skills to different situations
- Skills can handle edge cases without code changes
- Easy to update and extend
- Self-documenting
- Language/tool agnostic

**Trade-off:** Requires AI to interpret vs guaranteed behavior

### 5.3 Git as Source of Truth

**Decision:** All artifacts (BRDs, PRDs, tasks, implementations) live in Git.

**Why:**
- Version control for free
- Code and context in one place
- Works offline
- Standard developer workflow
- Easy to search and reference

**Trade-off:** Requires Git knowledge, can't share with non-technical stakeholders easily

### 5.4 Task Format Convention

**Decision:** Enforce `TASK-XXX:` naming format for all automated tasks.

**Why:**
- Clear distinction between automated and manual tasks
- Easy to filter and track
- Prevents accidental execution of unrelated tasks
- Grep-friendly for documentation

**Trade-off:** One more convention to learn

### 5.5 Workspace Isolation

**Decision:** Use Git worktrees for task execution instead of branches.

**Why:**
- Multiple tasks can run in parallel
- No branch switching conflicts
- Clean separation of work
- Easy cleanup
- Preserves main working directory

**Trade-off:** Uses more disk space, requires understanding of worktrees

---

## 6. How It Works

### The Happy Path

1. **Non Developer writes a BRD** (business requirements in markdown)
   ```bash
   ralph.py brd plans/my-idea.md
   ```
   → AI generates PRD (product requirements)

2. **Review PRD, generate tasks**
   ```bash
   ralph.py prd plans/my-idea-prd.md
   ```
   → AI breaks PRD into JSON task list with dependencies

3. **Create tasks in project tracker**
   ```bash
   ralph.py tasks-kanban plans/tasks.json
   ```
   → Tasks appear in Vibe-Kanban with proper sequencing

4. **Execute ready tasks**
   ```bash
   ralph.py run
   ```
   → AI finds tasks with no blockers, creates workspaces, executes them

5. **Review completed work**
   ```bash
   ralph.py review
   ```
   → AI generates implementation summaries, appends to implementation log

6. **Archive finished tasks**
   ```bash
   ralph.py cleanup
   ```
   → Tasks archived, worktrees deleted, Kanban updated, CHANGELOG maintained

### Two Modes

**Prompt Mode (default):**
```bash
ralph.py run
# Shows: Copy this prompt into Copilot CLI...
# User: [pastes into copilot]
# Copilot: [grants permissions, executes]
```

**Execute Mode (automation):**
```bash
ralph.py --execute run
# Runs immediately (requires pre-granted permissions)
```

---

## 7. What Makes This Different

### Compared to Traditional PM Tools

| Traditional Tools | Ralph |
|------------------|-------|
| Manual task creation | AI-generated from specs |
| Static task descriptions | Living documentation in Git |
| Manual status updates | Auto-updated via review cycle |
| Separate from code | Integrated with codebase |
| Tracking focus | Execution focus |

### Compared to CI/CD

| CI/CD | Ralph |
|-------|-------|
| Code-triggered | Document-triggered |
| Build/test/deploy | Plan/execute/review |
| Post-commit | Pre-commit (planning) + execution |
| Single workflow | Full SDLC pipeline |

### Compared to Just Using AI

| Raw AI Chat | Ralph |
|------------|-------|
| Ad-hoc requests | Structured workflow |
| Lost context | Preserved in Git |
| No audit trail | Full documentation |
| Manual coordination | Automatic orchestration |
| One-off solutions | Reusable patterns |

---

## 8. When to Use Ralph

### ✅ Good Fit

- Small to medium teams (2-10 developers)
- Greenfield projects or new features
- Teams comfortable with Git and command line
- Projects where AI can help with execution (web apps, scripts, APIs)
- Need for good documentation without manual work

### ⚠️ Limitations

- Requires GitHub Copilot subscription
- Use Vibe-Kanban Platform
- Non-technical teams still needs to learn a bit
- AI can make mistakes (review is essential)
- Works best for tasks AI can handle (code generation, refactoring, docs)

---

## 9. Future Possibilities

### Short Term
- Custom skill templates
- Better error recovery
- Metrics dashboard
- All [IDEAS.md](IDEAS.md) implemented

### Long Term
- Integration with design tools
- Automatic testing generation
- Performance analytics

---

## 10. Conclusion

Ralph doesn't replace your tools - it **orchestrates** them through AI.

**The core idea:** Let AI handle the mechanical parts of software development (requirements → tasks → code → docs) while humans focus on the creative parts (ideas, architecture, review).

By wrapping the SDLC in AI-friendly skills and maintaining everything in Git, Ralph makes it possible to go from business idea to documented implementation with minimal manual work.

It's not about replacing developers. It's about letting them work at a higher level of abstraction.

---

## Appendix: Prior Art

Ralph builds on several existing concepts:

- **Agentic AI** - Claude/Copilot skills that execute workflows
- **Git Worktrees** - Parallel isolated workspaces
- **Kanban Systems** - Task tracking and visualization
- **Documentation as Code** - Markdown specs in version control
- **Trunk-Based Development** - Feature branches that merge quickly
- **Continuous Documentation** - Automated implementation logs

What's new is putting them together in an **AI-orchestrated pipeline**.

---

## Getting Started

See [README.md](README.md) for installation and setup instructions.
