# Ralph (Copilot CLI runner)


[About](#about-ralph) | [prd.json format](#plansprdjson-format) | [Install/update Copilot CLI](#install--update-copilot-cli-standalone) | [ralph.sh (looped runner)](#ralphsh-looped-runner) | [ralph-once.sh (single run)](#ralph-oncesh-single-run) | [Demo](#demo) 


## About Ralph

Ralph is a small runner around **GitHub Copilot CLI (standalone)** inspired by [the“Ralph Wiggum” technique](https://www.humanlayer.dev/blog/brief-history-of-ralph): run a coding agent from a clean slate, over and over, until a stop condition is met.

The core idea:

- Run the agent in a finite bash loop (e.g. 10 iterations)
- Each iteration: implement exactly one scoped feature, then **commit**
- Append a short progress report to `progress.txt` after each run
- Keep CI green by running checks/tests every iteration
- Use a PRD-style checklist (here: `plans/prd.json` with `passes: false/true`) so the agent knows what to do next and when it’s done
- Stop early when the agent outputs `<promise>COMPLETE</promise>`

References:

- Thread: https://x.com/mattpocockuk/status/2007924876548637089
- Video:  [Ship working code while you sleep with the Ralph Wiggum technique | Matt Pocock](https://www.youtube.com/watch?v=_IK18goX4X8)

You’ll find two helper scripts:

- **`ralph.sh`** — runs Copilot in a loop for _N_ iterations (stops early if Copilot prints `<promise>COMPLETE</promise>`).
- **`ralph-once.sh`** — runs Copilot exactly once (useful for quick testing / dry-runs).


> You should adjust the prompt/instructions in the scripts to suit your project and workflow.


## Example output

Here’s an example of what running `MODEL=claude-opus-4.5 ./ralph-once.sh` might look like:

https://github.com/user-attachments/assets/221b4b44-d6ac-455c-86e9-66baa470953d



## Repo layout

```
.
├── plans/
│   └── prd.json
├── progress.txt
├── ralph.sh
├── ralph-once.sh
```



## `plans/prd.json` format

See the [`plans/`](plans/) folder for more context.

`plans/prd.json` is a JSON array where each entry is a “work item”, “acceptance test” or “user story”:

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



## List available models

 Force an error to print allowed models (quick check)

```bash
copilot --model not-a-real-model -p "hi"
```

You can also list/select models in interactive mode:

```bash
copilot
```

Then inside the Copilot prompt:

```text
/model
```



## Set the model (and default)

### One command
```bash
copilot --model gpt-5.2 -p "Hello"
```

### In the scripts (recommended pattern)

All scripts read a `MODEL` environment variable and default to `gpt-5.2` if not set:

```bash
MODEL="${MODEL:-gpt-5.2}"
```

Run with a specific model like this:

```bash
MODEL=claude-opus-4.5 ./ralph-once.sh
```



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



## `ralph-once.sh` (single run)

### What it does
- Runs Copilot exactly once with the same instructions as the loop script.

### Usage
```bash
./ralph-once.sh
```



## Notes on permissions / safety

Copilot CLI supports tool permission flags like:

- `--allow-tool 'write'` (file edits)
- `--allow-tool 'shell(git)'` / `--deny-tool 'shell(git push)'`
- `--allow-all-tools` (broad auto-approval; use with care)

The scripts in this bundle:
- enable non-interactive execution with `--allow-all-tools`
- explicitly deny dangerous commands like `rm` and `git push`

Adjust these to match your comfort level and CI/CD setup.



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

## Demo

Run Ralph in an isolated sandbox using a `git worktree` so you can delete everything afterwards.

1. Clone this repo and `cd` into it:
  ```bash
  git clone https://github.com/soderlind/ralph
  cd ralph
  ```

2. From the repo root, create a worktree on a new branch:
  ```bash
  ROOT_DIR="$PWD"
  git worktree add "$ROOT_DIR/../ralph-demo" -b ralph-demo
  cd "$ROOT_DIR/../ralph-demo"
  ```

3. (Optional) Confirm Copilot CLI is available:
  ```bash
  copilot --version
  ```

4. Run one iteration to validate everything works end-to-end:
  ```bash
  ./ralph-once.sh
  ```

5. Run multiple iterations (adjust the number as needed):
  ```bash
  ./ralph.sh 10
  ```

6. Inspect what happened:
  ```bash
  git --no-pager log --oneline --decorate -n 20
  cat progress.txt
  ```

7. Clean up (removes the worktree folder and deletes the demo branch):
  ```bash
  # IMPORTANT: run worktree commands against the same repo you created the worktree from.
  # Using `git -C "$ROOT_DIR" ...` avoids relying on `cd -` (which can change across shells).

  cd "$ROOT_DIR"
  git -C "$ROOT_DIR" worktree list
  git -C "$ROOT_DIR" worktree remove "$ROOT_DIR/../ralph-demo" || true

  # If you deleted the folder manually, prune stale worktree metadata then re-check:
  # git -C "$ROOT_DIR" worktree prune
  # git -C "$ROOT_DIR" worktree list

  git -C "$ROOT_DIR" branch -D ralph-demo
  ```

## Credits

- Prompt in scripts: [Matt Pocock](https://github.com/mattpocock)

## License

MIT — see [LICENSE](LICENSE).
