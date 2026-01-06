# Ralph (Copilot CLI runner)

This repo uses **GitHub Copilot CLI (standalone)** to iteratively implement items from a lightweight `plans/prd.json` and record work in `progress.txt`.

You’ll find two helper scripts:

- **`ralph.sh`** — runs Copilot in a loop for _N_ iterations (stops early if Copilot prints `<promise>COMPLETE</promise>`).
- **`ralph-once.sh`** — runs Copilot exactly once (useful for quick testing / dry-runs).

---

## Repo layout

```
.
├── plans/
│   └── prd.json
├── progress.txt
├── ralph.sh
└── ralph-once.sh
```

---

## `plans/prd.json` format

`plans/prd.json` is a JSON array where each entry is a “work item” or “acceptance test”:

```json
[
  {
    "category": "functional",
    "description": "User can send a message and see it appear in the conversation",
    "steps": [
      "Open the chat app and navigate to a conversation",
      "Type a message in the composer",
      "Click Send (or press Enter)",
      "Verify the message appears in the message list"
    ],
    "passes": false
  }
]
```

### Fields

- **`category`**: typically `"functional"` or `"ui"` (you can add more if you want).
- **`description`**: one-line requirement / behavior.
- **`steps`**: human-readable steps to verify.
- **`passes`**: boolean; set to `true` when complete.

Copilot is instructed to:
- pick the **highest-priority item** (it decides),
- implement **only one feature per run**,
- run `pnpm typecheck` and `pnpm test`,
- update `plans/prd.json`,
- append notes to `progress.txt`,
- commit changes.

---

## Install / update Copilot CLI (standalone)

### Check your installed version
```bash
copilot --version
# or
copilot -v
```

### Update (choose the one that matches how you installed it)

**Homebrew (macOS/Linux)**
```bash
brew update
brew upgrade copilot
```

**npm**
```bash
npm i -g @github/copilot
```

**WinGet (Windows)**
```powershell
winget upgrade GitHub.Copilot
```

> Tip: If you’re not sure how you installed it, run `which copilot` (macOS/Linux) or `where copilot` (Windows) to see where it’s coming from.

---

## List available models

Your Copilot CLI already exposes the model list via `--help`:

```bash
copilot --help
```

Look for the `--model <model>` line.

You can also list/select models in interactive mode:

```bash
copilot
```

Then inside the Copilot prompt:

```text
/model
```

---

## Set the model (and default)

### One command
```bash
copilot --model gpt-5 -p "Hello"
```

### In the scripts (recommended pattern)

Both scripts read a `MODEL` environment variable and default to `gpt-5` if not set:

```bash
MODEL="${MODEL:-gpt-5}"
```

Run with a specific model like this:

```bash
MODEL=claude-sonnet-4.5 ./ralph-once.sh
```

---

## `ralph.sh` (looped runner)

### What it does
- Runs Copilot up to **N iterations**
- Captures Copilot output each time
- Stops early if output contains:
  - `<promise>COMPLETE</promise>`

### Usage
```bash
./ralph.sh 10
```

### How it prompts Copilot
The prompt includes:
- `@plans/prd.json`
- `@progress.txt`

…plus instructions to implement **one** feature, run checks, update files, and commit.

---

## `ralph-once.sh` (single run)

### What it does
- Runs Copilot exactly once with the same instructions as the loop script.

### Usage
```bash
./ralph-once.sh
```

---

## Notes on permissions / safety

Copilot CLI supports tool permission flags like:

- `--allow-tool 'write'` (file edits)
- `--allow-tool 'shell(git)'` / `--deny-tool 'shell(git push)'`
- `--allow-all-tools` (broad auto-approval; use with care)

The scripts in this bundle:
- enable non-interactive execution with `--allow-all-tools`
- explicitly deny dangerous commands like `rm` and `git push`

Adjust these to match your comfort level and CI/CD setup.

---

## Typical workflow

1. Put work items in `plans/prd.json`
2. Run one iteration to validate your setup:
   ```bash
   ./ralph-once.sh
   ```
3. Run multiple iterations:
   ```bash
   ./ralph.sh 20
   ```
4. Review `progress.txt` for a running log of changes and next steps.
