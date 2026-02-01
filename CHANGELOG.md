# CHANGELOG

All notable changes to the Ralph Copilot project are documented here.

## [2026-01-31] - Task Review and Cleanup

### Added

- **Implementation Log** (`docs/implementation-log.md`): Comprehensive documentation of all completed Ralph tasks (TASK-001 through TASK-005) with detailed implementation summaries
- **Cleanup Log** (`docs/cleanup-log.md`): Record of archived tasks and cleanup operations
- **Archive Structure**: Organized archive directory for completed tasks at `archive/tasks/TASK-{ID}/`

### Cleanup Operations

- Each task documented in `archive/tasks/TASK-{ID}/README.md`
- Implementation summaries appended to `docs/implementation-log.md`
- Git worktrees cleaned up (1 worktree deleted)
- All tasks deleted from Vibe-Kanban project
- Complete audit trail maintained in `docs/cleanup-log.md`

### Technical Details

- **Git Worktrees Deleted**: 1 (TASK-005 workspace)
- **Vibe-Kanban Tasks Deleted**: 5 (TASK-001 through TASK-005)
- **Archive Path**: `archive/tasks/`
- **Safety Checks**: Double-verified (implementation-log.md + 'done' status)

---

## [2026-01-31] - Ralph Prompt Review Prompt Update

### Changed

- Updated `ralph review` prompt to explicitly mention cleanup behavior
- Prompt now includes step "7. Trigger @ralph-cleanup-agent to archive reviewed tasks" when auto-cleanup is enabled
- Context section shows `Auto-cleanup: Yes/No` to clarify user intent

### Impact

- Users can now see exactly what will happen before copying the prompt
- The prompt text matches the actual behavior
- Task format filtering (TASK-XXX:) only processes properly formatted tasks

---

## [2026-01-31] - Ralph-Run Skill Repository Resolution

### Changed

- Updated **Step 0** of ralph-run skill to resolve repository ID upfront
- Added `vibe_kanban-list_repos` call immediately after project ID resolution
- Eliminates "missing field repo_id" errors in workspace session creation

### Impact

- Cleaner workflow: project_id + repo_id resolved in Step 0
- No more repository lookup errors when starting workspaces
- More efficient MCP tool usage

---

## [Earlier] - Prompt Generator Mode Implementation

See `CHANGELOG-PROMPT-MODE.md` for detailed implementation history of the prompt generator feature, including:
- Dual-mode architecture (prompt vs execute)
- Git branch auto-detection
- Task format filtering (TASK-XXX:)
- Skill metadata standardization

---
