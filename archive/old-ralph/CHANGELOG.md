# Changelog

All notable changes to this project will be documented in this file.

## [2.0.1] - 2026-01-28

### Changed
- Moved default `progress.txt` location from repository root to `.ralph/progress.txt`
- Consolidated state files under `.ralph/` directory for better project organization

### Breaking Changes
- Scripts with hardcoded paths to `progress.txt` at repository root will need updating
- Use the `--progress` flag to override the default location if needed

## [2.0.0] - 2026-01-24

### Added
- `ralph.py` - New Python implementation replacing bash scripts
- `--once` flag for single iteration mode
- `--allow-dirty` flag for iterative workflow with uncommitted changes
- `--prompt-prefix` flag for custom instructions
- `--prd` flag for custom PRD path
- State persistence via `.ralph/state.json`
- Story-based iteration (one story at a time)
- Better error handling and logging
- Comprehensive documentation: `RALPH.md`, `RALPH_FEATURES.md`, `RALPH_EXAMPLES.md`, `RALPH_MIGRATION.md`

### Removed
- `ralph.sh` - Replaced by `ralph.py`
- `ralph-once.sh` - Replaced by `ralph.py --once`
- `RALPH_DEPRECATED_SCRIPTS.md` - Documentation of removed scripts

### Fixed
- Exit status 1 bug - Copilot now executes properly
- Prompt passing - Uses inline text instead of file references
- Streaming output - See Copilot work in real-time

### Changed
- Migrated from bash to Python 3.10+ for cleaner implementation
- Auto-commit per story implementation
- Dynamic prompt building from PRD
- Proper test enforcement

## [1.1.0] - 2026-01-12

### Added
- `--skill <a[,b,...]>` support in `ralph.sh` and `ralph-once.sh` (prepends `skills/<name>/SKILL.md` into the attached context).
- `--only <prompt1[,prompt2...]>` filter in `test/run-prompts.sh` to run selected prompt tests.
- Vendored WordPress skills under `test/skills/` for the harness:

  - `wp-plugin-development`
  - `wp-project-triage`

### Fixed
- `test/run-prompts.sh`: WordPress skill staging now copies from `$ROOT/test/skills/...` (so it works inside per-prompt worktrees).
- `test/run-prompts.sh`: WordPress assertions/skill injection now match `wordpress-plugin-agent.txt` consistently.

### Changed
- `test/run-prompts.sh`: WordPress prompt test now stages those vendored skills into a top-level `skills/` folder inside the worktree and injects the WP plugin skill into the context attachment.

## [1.0.0] - 2026-01-10

### Added
- `CHANGELOG.md`.
- `RALPH_VERSION="1.0.0"` in the runner scripts.
- `prompts/pest-coverage.txt`.
- Harness support for running `pest-coverage.txt` without a PRD.

### Changed
- `ralph.sh` / `ralph-once.sh`: `--prompt` is required (no implicit default prompt).
- `ralph.sh` / `ralph-once.sh`: `--prd` is optional and only attached when explicitly provided.
- Normalized shell tool allow/deny specs to the pattern form `shell(cmd:*)`.
- Prevented emitting empty tool spec arguments (avoids `--allow-tool ''` / `--deny-tool ''`).
- `test/run-prompts.sh`: runs prompts in isolated git worktrees and captures Copilot output via pseudo-TTY transcript.

### Documentation
- Updated README usage/examples to reflect `--prompt` required and `--prd` optional.
- Added per-prompt examples in `prompts/README.md`.
