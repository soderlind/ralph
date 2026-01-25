# Ralph (Copilot CLI runner)

> Let AI implement your features while you sleep.

Ralph runs **GitHub Copilot CLI** in a loop, implementing one feature at a time until your PRD is complete.

[Quick Start](#quick-start) · [How It Works](#how-it-works) · [Configuration](#configuration) · [Command Reference](#command-reference) · [Demo](#demo)


---

## Quick Start

```bash
# Clone and enter the repo
git clone https://github.com/soderlind/ralph
cd ralph

# Add your work items to plans/prd.json

# Test with a single iteration
./ralph.py --allow-profile safe --max-iterations 1

# Run multiple iterations (iterative mode - RECOMMENDED)
./ralph.py --allow-profile safe --allow-dirty --max-iterations 10
```

Check `progress.txt` for a log of what was done.

---

## How It Works

Ralph implements the ["Ralph Wiggum" technique](https://www.humanlayer.dev/blog/brief-history-of-ralph):

1. **Read** — Copilot reads your PRD (if attached) and progress file
2. **Pick** — It chooses the highest-priority incomplete item
3. **Implement** — It writes code for that one feature
4. **Verify** — It runs your tests (`pnpm typecheck`, `pnpm test`)
5. **Update** — It marks the item complete and logs progress
6. **Commit** — It commits the changes
7. **Repeat** — Until all items pass or it signals completion


https://github.com/user-attachments/assets/28206ee1-8dad-4871-aef5-1a9f24625dba


### Learn More

- [Matt Pocock's thread](https://x.com/mattpocockuk/status/2007924876548637089)
- [Ship working code while you sleep (video)](https://www.youtube.com/watch?v=_IK18goX4X8)
- [11 Tips For AI Coding With Ralph Wiggum](https://www.aihero.dev/tips-for-ai-coding-with-ralph-wiggum)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Configuration

### Choose a Model

Set the `MODEL` environment variable (default: `gpt-5.2`):

```bash
MODEL=claude-opus-4.5 ./ralph.py --allow-profile safe --max-iterations 10
```

### Define Your Work Items

Create `plans/prd.json` with your requirements:

```json
[
  {
    "category": "functional",
    "description": "User can send a message and see it in the conversation",
    "steps": ["Open chat", "Type message", "Click Send", "Verify it appears"],
    "passes": false
  }
]
```

| Field         | Description                                |
|---------------|--------------------------------------------|
| `category`    | `"functional"`, `"ui"`, or custom          |
| `description` | One-line summary                           |
| `steps`       | How to verify it works                     |
| `passes`      | `false` → `true` when complete             |

See the [`plans/`](plans/) folder for more context.

### Use Custom Prompts

Prompts can be customized via `--prompt-prefix`:

```bash
./ralph.py --prompt-prefix prompts/my-prompt.txt --allow-profile safe --max-iterations 10
```

> **Note:** Custom tools require `--allow-profile` or `--allow-tools`.

---

## Command Reference

### `ralph.py` — Looped Runner

Runs Copilot up to N iterations. Stops early on `<promise>COMPLETE</promise>`.

```bash
./ralph.py [options]
```

**Examples:**

```bash
./ralph.py --allow-profile safe --max-iterations 10
./ralph.py --allow-profile safe --allow-dirty --max-iterations 10
./ralph.py --once --allow-profile safe
./ralph.py --prompt-prefix prompts/custom.txt --allow-profile safe --max-iterations 10
MODEL=claude-opus-4.5 ./ralph.py --allow-profile safe --max-iterations 10
```

### Options

| Option                   | Description                          | Default               |
|--------------------------|--------------------------------------|-----------------------|
| `--once`                 | Single iteration mode                | Loop mode             |
| `--allow-dirty`          | Allow uncommitted changes (iterative)| Clean repo enforced   |
| `--prompt-prefix <file>` | Load custom prompt prefix            | Built-in prompt       |
| `--prd <file>`           | Path to PRD JSON file                | `plans/prd.json`      |
| `--max-iterations <n>`   | Maximum iterations (loop mode)       | 10                    |
| `--allow-profile <name>` | Permission profile (see below)       | —                     |
| `--allow-tools <spec>`   | Allow specific tool (repeatable)     | —                     |
| `--deny-tools <spec>`    | Deny specific tool (repeatable)      | —                     |
| `-h, --help`             | Show help                            | —                     |

**Environment:**

| Variable | Description        | Default   |
|----------|--------------------|-----------|
| `MODEL`  | Model to use       | `gpt-5.2` |

### Permission Profiles

| Profile  | Allows                                 | Use Case                     |
|----------|----------------------------------------|------------------------------|
| `locked` | `write` only                           | File edits, no shell         |
| `safe`   | `write`, `shell(pnpm:*)`, `shell(git:*)` | Normal dev workflow        |
| `dev`    | All tools                              | Broad shell access           |

**Always denied:** `shell(rm)`, `shell(git push)`

**Custom tools:** If you pass `--allow-tools`, it replaces the profile defaults:

```bash
./ralph.py --allow-tools write --allow-tools 'shell(composer:*)' --allow-profile safe --max-iterations 10
```

---

## Demo

Try Ralph in a safe sandbox:

```bash
# Setup
git clone https://github.com/soderlind/ralph && cd ralph
git worktree add ../ralph-demo -b ralph-demo
cd ../ralph-demo

# Run
./ralph.py --allow-profile safe --max-iterations 1
./ralph.py --allow-profile safe --allow-dirty --max-iterations 10

# Inspect
git log --oneline -20
cat progress.txt

# Cleanup
cd .. && git worktree remove ralph-demo && git branch -D ralph-demo
```

---

## Project Structure

```
.
├── plans/prd.json        # Your work items
├── prompts/default.txt   # Example prompt
├── progress.txt          # Running log
├── ralph.py              # Main runner (Python)
├── .ralph/state.json     # Iteration state
└── test/                 # Test harness
```

---

## Install Copilot CLI

```bash
# Check version
copilot --version

# Homebrew
brew update && brew upgrade copilot

# npm
npm i -g @github/copilot

# Windows
winget upgrade GitHub.Copilot
```

---

## Testing Prompts

Run all prompts in isolated worktrees:

```bash
./test/run-prompts.sh
```

Logs: `test/log/`

---

## Copilot CLI Notes

Ralph is a Python-based wrapper around the Copilot CLI. The important flags it relies on are:

### Context attachment

Ralph passes context to Copilot via inline prompts. Ralph builds context per iteration that typically contains:

- `progress.txt` (always)
- PRD JSON (only if you pass `--prd <file>`)
- Custom prompt prefix (if `--prompt-prefix <file>` is provided)

This keeps the agent's input structured and clean.

### Tool permissions (`--allow-*` / `--deny-*`)

Ralph controls what Copilot is allowed to do by passing tool permission flags:

- `--allow-profile <safe|dev|locked>`: convenience presets implemented by Ralph.
- `--allow-tools <spec>`: allow a specific tool spec (repeatable). When you use this, it replaces the profile defaults.
- `--deny-tools <spec>`: deny a specific tool spec (repeatable).

For shell tools, prefer the pattern form `shell(cmd:*)` (for example `shell(git:*)`).

Ralph always denies a small set of dangerous commands (currently `shell(rm)` and `shell(git push)`).




## License

MIT — see [LICENSE](LICENSE).
