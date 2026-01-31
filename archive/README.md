# Old Ralph Archive

This directory contains the original Ralph loop-based implementation, archived when transitioning to the new SDLC wrapper architecture.

## What was archived (2026-01-31)

- `ralph.py` - Original Python loop script
- `prompts/` - Old prompt templates
- `ralph-docs/` - Original Ralph documentation
- `progress.txt` - Old logging format
- `.ralph/` - Old state management
- `__pycache__/` - Python cache
- `README.md` → `README-original.md` - Original README
- `CHANGELOG.md` - Original changelog

## Why the change?

The new SDLC wrapper is a complete reimagining:

**Old Ralph (loop-based):**
- Sequential PRD execution via Copilot CLI
- Simple loop: pick task → implement → test → mark done
- Single progress.txt log

**New Ralph (SDLC wrapper):**
- Full workflow: BRD → PRD → Tasks → Execute (parallel) → Review → Cleanup
- Vibe-Kanban integration for task execution
- Skill-based architecture (brd-to-prd, prd-to-tasks, task-review, cleanup-agent)
- Structured logging (implementation-log.md, cleanup-log.md)
- Dependency-aware parallel execution

## What was kept?

- `scripts/cleanup-worktrees.sh` - Enhanced for vibe-kanban
- `plans/` folder - Still used, new formats
- `LICENSE` - Same license

## Can I restore old Ralph?

Yes, the files are preserved here. However, the new SDLC wrapper is incompatible with the old format. To use old Ralph:

1. Copy `ralph.py` back to project root
2. Restore `prompts/` folder
3. Use old PRD format (see `ralph-docs/RALPH.md`)

## Learn more

- New architecture: `../docs/ARCHITECTURE.md`
- New skills: `../skills/`
- New config: `../config/ralph.json`
