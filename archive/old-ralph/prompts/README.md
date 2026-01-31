# Sample prompts

This folder contains example prompt files to use with `--prompt-prefix`.

## Usage

Looped runner (multiple iterations):

Runs up to N iterations. Good for making real progress on a PRD.

```bash
./ralph.py --allow-profile safe --max-iterations 10
```

Single run (test mode):

Runs exactly one iteration. Good for testing prompt wording and tool permissions.

```bash
./ralph.py --once --allow-profile safe
```

## The Default Prompt

The default prompt is built into `ralph.py`. It handles:

1. **Reading context** — Checks progress.txt and attached PRD
2. **Picking a feature** — Finds the highest-priority incomplete item
3. **Implementing** — Writes code for that feature
4. **Verifying** — Runs pnpm typecheck and pnpm test
5. **Updating PRD** — Marks feature as `passes: true` with notes
6. **Committing** — Creates a git commit
7. **Repeating** — Until all features are done or max iterations hit

### Example: Default workflow with PRD

```bash
./ralph.py --allow-profile safe --max-iterations 10
```

## Custom Prompts

Override the default prompt with `--prompt-prefix`:

```bash
./ralph.py --prompt-prefix prompts/custom.txt --allow-profile safe --max-iterations 10
```

Your custom prompt should:

- Reference `progress.txt` (always available)
- Parse the PRD JSON if you provide one
- Output clear progress updates
- Use structured headings for readability

Example custom prompt:

```
You are a code agent. Work on the next unfinished task in the PRD.

## Context
- Read progress.txt to see what's been built
- Check the PRD to understand requirements
- Implement ONE feature per iteration

## Steps
1. Pick the highest-priority incomplete feature
2. Write code that passes tests
3. Update the PRD (mark as passes: true)
4. Append progress notes to progress.txt
5. Make a git commit

## Important
- Always run `pnpm typecheck` before committing
- Only work on ONE feature per iteration
- Be clear about architectural decisions
```

## Tool Permissions

Tool access is controlled by `--allow-profile`, not the prompt file:

Safe mode (recommended):

```bash
./ralph.py --allow-profile safe --max-iterations 10
```

Write-only mode (no shell):

```bash
./ralph.py --allow-profile locked --max-iterations 10
```

Dev mode (full access):

```bash
./ralph.py --allow-profile dev --max-iterations 10
```

Custom permissions:

```bash
./ralph.py --allow-tools write --allow-tools 'shell(git:*)' --max-iterations 10
```

## Example Workflows

### Workflow 1: Start from scratch

```bash
# Test with 1 iteration (validate prompt and permissions)
./ralph.py --once --allow-profile safe

# Full run if test looks good
./ralph.py --allow-profile safe --max-iterations 10

# Check progress
cat progress.txt | tail -30
```

### Workflow 2: Custom features

```bash
# Create a custom PRD
cat > plans/prd-myapp.json << 'EOF'
[
  {
    "id": "feat-1",
    "category": "functional",
    "priority": 1,
    "description": "Build my feature",
    "steps": ["Step 1", "Step 2"],
    "passes": false,
    "dependsOn": []
  }
]
EOF

# Run with custom PRD
./ralph.py --prd plans/prd-myapp.json --allow-profile safe --max-iterations 5
```

### Workflow 3: Iterative development

For projects that are already started, use `--allow-dirty` to keep uncommitted changes:

```bash
./ralph.py --allow-dirty --allow-profile safe --max-iterations 10
```

This lets you keep local changes while Ralph makes its edits.
