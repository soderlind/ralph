# Ralph — Autonomous Feature Builder

> Let AI implement your PRD. Ralph runs GitHub Copilot CLI in a loop, one feature at a time.

**What:** Ralph is a Python automation runner that chains Copilot iterations until your product requirements are complete.

**Why use Ralph:**
- ✅ Automate repetitive implementation work — define features in JSON, Ralph builds them
- ✅ Test-driven feedback loop — each feature runs tests and validates before commit
- ✅ Clear progress tracking — human-readable log + git commits per feature
- ✅ Resume-safe — pause and resume workflows without context loss
- ✅ Works with any codebase — respects your test commands and project structure

**Key difference from other AI coding tools:**
Ralph is **iterative and PRD-aware**. It treats your requirements as a state machine: pick incomplete items, implement one, verify with tests, mark complete, repeat. This creates reliable incremental progress, not one-shot code generation.

[Quick Start](#quick-start) · [How to Use](#how-to-use) · [Technical Details](#technical-details) · [CLI Reference](#cli-reference) · [Learn More](#learn-more)

---

## Quick Start

```bash
# Clone and setup
git clone https://github.com/soderlind/ralph && cd ralph

# Define work items in plans/prd.json (JSON array with description, steps, passes: false)

# Test one iteration
./ralph.py --allow-profile safe --max-iterations 1

# Run iteratively (RECOMMENDED)
./ralph.py --allow-profile safe --allow-dirty --max-iterations 10
```

Check `progress.txt` for detailed logs. When all features pass, Ralph stops automatically.

---

## How It Works

Ralph implements the [**Ralph Wiggum technique**](https://www.humanlayer.dev/blog/brief-history-of-ralph):

1. **Read** — Copilot reads your PRD and progress file
2. **Pick** — Selects the first incomplete feature (`passes: false`)
3. **Implement** — Writes code based on description + steps
4. **Verify** — Runs tests to validate the feature works
5. **Update** — Marks feature `passes: true`, appends to progress.txt
6. **Commit** — Auto-commits with feature ID in message
7. **Repeat** — Loops until all features pass or max-iterations reached

**Why this works:**
- Each iteration builds on the last — Copilot sees what was done before
- Tests keep old features from breaking — regression prevention built-in
- PRD is your source of truth — features stay tracked, progress is visible

Learn more: [Matt Pocock's Thread](https://x.com/mattpocockuk/status/2007924876548637089) · [Video](https://www.youtube.com/watch?v=_IK18goX4X8) · [Anthropic's Guide](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

See **Learn More** section for additional resources.

---

## How to Use

### 1. Define Your PRD

Create `plans/prd.json`:

```json
[
  {
    "id": "feature-001",
    "category": "functional",
    "description": "User can send messages",
    "details": "Build chat input field with validation",
    "steps": ["Create input component", "Add validation", "Wire to API"],
    "tests": ["pnpm test -- chat"],
    "passes": false
  }
]
```

| Field | Required | Purpose |
|-------|----------|---------|
| `id` | Yes | Unique identifier for commits and tracking |
| `description` | Yes | One-line feature summary for Copilot |
| `details` | No | Technical context (optional) |
| `steps` | Yes | Verification steps or how to validate |
| `tests` | No | Commands to run (default: `pnpm test`) |
| `passes` | Yes | `false` → `true` when complete |
| `dependsOn` | No | Array of feature IDs that must pass first (see Feature Dependencies below) |

### 2. Run Ralph

```bash
# Single iteration (safest first run)
./ralph.py --allow-profile safe --max-iterations 1

# Iterative mode (keeps running, auto-commits)
./ralph.py --allow-profile safe --allow-dirty --max-iterations 10

# Custom model
MODEL=claude-opus-4.5 ./ralph.py --allow-profile safe --max-iterations 10

# Custom prompt
./ralph.py --prompt-prefix prompts/my-prompt.txt --allow-profile safe --max-iterations 10
```

### 3. Monitor Progress

Ralph logs to two files:
- `progress.txt` — human-readable transcript (append-only)
- `.ralph/state.json` — iteration metadata (for resuming)

Each feature gets a git commit tagged with its ID.

---

## Technical Details

### State Management

Ralph uses a **PRD-first architecture** with 3 key files:

| File | Role |
|------|------|
| `plans/prd.json` | **Source of truth** — requirements with `passes: true/false` |
| `progress.txt` | **Append-only log** — what was done, why, and errors |
| `.ralph/state.json` | **Resume metadata** — iteration count, PRD hash, last run |

This ensures:
- ✅ No context loss (progress.txt is human-readable)
- ✅ Pause & resume (state.json tracks progress)
- ✅ Test integrity (all tests re-run each iteration)
- ✅ Clear git history (commits reference feature IDs)

**How it works:** Ralph reads `plans/prd.json`, picks the first incomplete feature, implements it, runs tests, marks it complete, commits, then repeats. See **How It Works** section above.

### Feature Dependencies

Use `dependsOn` to ensure dependent features re-test when base features change:

```json
{
  "id": "auth-001",
  "description": "Login endpoint",
  "dependsOn": ["api-setup-001"],
  "tests": ["pnpm test", "curl http://localhost:3000/api/login"]
}
```

When `auth-001` is tested, Ralph ensures all dependencies still pass.

---

## CLI Reference

### `./ralph.py` — Main Runner

```bash
./ralph.py [OPTIONS]
```

**Options:**

| Option | Type | Default | Purpose |
|--------|------|---------|---------|
| `--once` | flag | Loop mode | Run one iteration only |
| `--allow-dirty` | flag | Off | Allow uncommitted changes (required for iterative mode) |
| `--allow-profile` | `safe\|dev\|locked` | — | Permission preset (required) |
| `--allow-tools` | spec | — | Allow specific tool (repeatable, replaces profile) |
| `--deny-tools` | spec | — | Deny specific tool (repeatable) |
| `--prompt-prefix` | file | Built-in | Custom system prompt |
| `--prd` | file | `plans/prd.json` | Path to PRD JSON |
| `--max-iterations` | N | 10 | Loop limit |
| `-h, --help` | flag | — | Show help |

**Environment:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `MODEL` | `gpt-5.2` | AI model to use (e.g., `claude-opus-4.5`) |

### Permission Profiles

| Profile | Allows | Best For |
|---------|--------|----------|
| `locked` | `write` only | File edits, no shell commands |
| `safe` | `write`, `shell(pnpm:*)`, `shell(git:*)` | **Most common** — npm scripts + git |
| `dev` | All tools except `shell(rm)` and `shell(git push)` | Broad shell access (less safe) |

Custom tools replace profile defaults:

```bash
./ralph.py --allow-tools write --allow-tools 'shell(composer:*)' --allow-profile safe
```

Ralph always denies: `shell(rm)`, `shell(git push)` (hardcoded safety).

---

## Advanced Examples

### Demo in Sandbox

```bash
git clone https://github.com/soderlind/ralph && cd ralph
git worktree add ../ralph-demo -b ralph-demo && cd ../ralph-demo

./ralph.py --allow-profile safe --max-iterations 1
./ralph.py --allow-profile safe --allow-dirty --max-iterations 10

git log --oneline -10 && cat progress.txt

cd .. && git worktree remove ralph-demo && git branch -D ralph-demo
```

### Test Harness

Run all prompts in isolated worktrees to test changes:

```bash
./test/run-prompts.sh
# Logs in test/log/
```

---

## Learn More

- [Ralph Wiggum Technique](https://www.humanlayer.dev/blog/brief-history-of-ralph) — Origins and philosophy
- [Matt Pocock's Thread](https://x.com/mattpocockuk/status/2007924876548637089) — Why iterative agents work
- [Ship Working Code While You Sleep (video)](https://www.youtube.com/watch?v=_IK18goX4X8)
- [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Anthropic's guide
- [Ralph Loop Reference](https://gist.github.com/soderlind/ca83ba5417e3d9e25b68c7bdc644832c) — Detailed implementation example

---

## Installation

### Install Copilot CLI

Ralph requires the Copilot CLI:

```bash
# Homebrew (macOS/Linux)
brew update && brew upgrade copilot

# npm
npm i -g @github/copilot

# Windows
winget upgrade GitHub.Copilot

# Verify
copilot --version
```

### Project Structure

```
.
├── ralph.py                 # Main runner
├── plans/prd.json          # Your requirements
├── prompts/default.txt     # Default system prompt
├── progress.txt            # Running log (generated)
├── .ralph/state.json       # State metadata (generated)
└── test/
    ├── run-prompts.sh      # Test harness
    └── log/                # Test logs (generated)
```

---

## License

MIT — see [LICENSE](LICENSE).
