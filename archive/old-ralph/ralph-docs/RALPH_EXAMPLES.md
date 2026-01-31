# Ralph.py Usage Examples

## Basic Usage

### 1. Single Run (Once Mode - replaces ralph-once.sh)
```bash
# Run one story and stop
./ralph.py --once --allow-profile safe

# With custom prompt
./ralph.py --once --prompt-prefix prompts/quick-task.txt --allow-profile safe

# Allow uncommitted changes
./ralph.py --once --allow-profile safe --allow-dirty
```

### 2. First Run (Clean Repo Required)
```bash
# Start fresh with clean repo
git status  # should show no changes

# Run 5 iterations
./ralph.py --allow-profile safe --max-iterations 5
```

### 2. Iterative Development (Recommended)
```bash
# Run 3 iterations, allow uncommitted changes
./ralph.py --allow-profile safe --allow-dirty --max-iterations 3

# Review what was done
cat progress.txt | tail -100
git diff

# Make manual adjustments if needed
# ...edit files...

# Continue with 3 more iterations
./ralph.py --allow-profile safe --allow-dirty --max-iterations 3
```

### 3. Custom PRD Location
```bash
# Use different PRD file
./ralph.py --prd plans/backend-prd.json --allow-profile safe --max-iterations 10

# Multiple PRDs for different features
./ralph.py --prd plans/frontend-prd.json --allow-profile safe --max-iterations 10
```

### 4. With Custom Prompt Instructions
```bash
# Create prompts/coding-style.txt with your conventions
cat > prompts/coding-style.txt << 'EOF'
CODING CONVENTIONS:
- Use TypeScript strict mode
- Add JSDoc to all exported functions
- Follow ESLint rules strictly
- Write tests for all new features
- Use semantic commit messages
EOF

# Run with custom prompt prefix
./ralph.py --allow-profile safe --prompt-prefix prompts/coding-style.txt --max-iterations 10
```

## Advanced Usage

### 5. Different Permission Profiles

**Safe (Default for Most Work)**
```bash
# Allows: write files, run pnpm commands, run git commands
./ralph.py --allow-profile safe --max-iterations 10
```

**Dev Mode (Full Access)**
```bash
# Allows: all tools including shell commands
./ralph.py --allow-profile dev --max-iterations 10
```

**Locked (Maximum Safety)**
```bash
# Allows: only write files, no shell commands
./ralph.py --allow-profile locked --max-iterations 5
```

### 6. Custom Model Selection
```bash
# Use Claude Sonnet
./ralph.py --allow-profile safe --model claude-sonnet-4.5 --max-iterations 10

# Use GPT-5
./ralph.py --allow-profile safe --model gpt-5 --max-iterations 10

# Use Haiku (faster, cheaper)
./ralph.py --allow-profile safe --model claude-haiku-4.5 --max-iterations 20
```

### 7. Custom Tool Permissions
```bash
# Allow specific additional tools
./ralph.py --allow-profile safe --allow-tool 'shell(docker:*)' --max-iterations 10

# Deny specific tools
./ralph.py --allow-profile dev --deny-tool 'shell(rm)' --deny-tool 'shell(docker rm)' --max-iterations 10
```

## Real-World Workflows

### Workflow 1: Daily Development Cycle
```bash
# Morning: Fresh start
git checkout -b feature/new-api
./ralph.py --allow-profile safe --allow-dirty --max-iterations 5

# Lunch break: Review and adjust
git diff > review.patch
# ...manual review and edits...

# Afternoon: Continue
./ralph.py --allow-profile safe --allow-dirty --max-iterations 5

# End of day: Final review and commit
git add -A
git commit -m "feat: implement new API endpoints"
```

### Workflow 2: Multiple Feature Branches
```bash
# Frontend branch
git checkout -b feature/ui-components
./ralph.py --prd plans/ui-prd.json --allow-profile safe --max-iterations 10

# Backend branch
git checkout -b feature/api-endpoints
./ralph.py --prd plans/api-prd.json --allow-profile safe --max-iterations 10

# Database branch
git checkout -b feature/schema-migration
./ralph.py --prd plans/db-prd.json --allow-profile safe --max-iterations 5
```

### Workflow 3: Test-First Development
```bash
# Create PRD with comprehensive tests
cat > plans/tdd-prd.json << 'EOF'
[
  {
    "id": "feat-001",
    "priority": 1,
    "description": "Implement user authentication",
    "tests": [
      "pnpm test auth.test.ts",
      "pnpm typecheck",
      "pnpm lint"
    ],
    "passes": false
  }
]
EOF

# Run ralph
./ralph.py --prd plans/tdd-prd.json --allow-profile safe --max-iterations 10
```

### Workflow 4: Continuous Iteration
```bash
# Run in loop until complete or max 50 iterations
./ralph.py --allow-profile safe --allow-dirty --max-iterations 50

# If it completes, you'll see:
# COMPLETE

# If it doesn't finish, review and continue:
./ralph.py --allow-profile safe --allow-dirty --max-iterations 50
```

## Debugging

### Check Progress
```bash
# View recent progress
tail -100 progress.txt

# Search for errors
grep -i "error\|fail\|block" progress.txt

# View state
cat .ralph/state.json
```

### Resume After Manual Fixes
```bash
# Ralph failed on a story, fix it manually
# ...edit files...

# Mark story as passing in PRD
# Edit plans/prd.json: set "passes": true

# Continue with next story
./ralph.py --allow-profile safe --allow-dirty --max-iterations 10
```

## Environment Variables

```bash
# Set default model
export RALPH_MODEL="claude-sonnet-4.5"
./ralph.py --allow-profile safe --max-iterations 10

# Set custom copilot binary path
export COPILOT_BIN="/usr/local/bin/copilot-custom"
./ralph.py --copilot-bin "$COPILOT_BIN" --allow-profile safe --max-iterations 10
```

## Common Patterns

### Pattern 1: Review Between Batches
```bash
# Small batches with review
for i in {1..5}; do
  echo "=== Batch $i ==="
  ./ralph.py --allow-profile safe --allow-dirty --max-iterations 3
  echo "Review progress.txt and press Enter to continue..."
  read
done
```

### Pattern 2: Different PRDs for Different Days
```bash
# Monday: Architecture
./ralph.py --prd plans/monday-arch.json --allow-profile safe --max-iterations 10

# Tuesday: Features
./ralph.py --prd plans/tuesday-features.json --allow-profile safe --max-iterations 10

# Wednesday: Polish
./ralph.py --prd plans/wednesday-polish.json --allow-profile safe --max-iterations 10
```

### Pattern 3: Progressive Permissions
```bash
# Start locked (safe exploration)
./ralph.py --allow-profile locked --max-iterations 3

# Review, then allow more tools
./ralph.py --allow-profile safe --allow-dirty --max-iterations 5

# Final push with full access
./ralph.py --allow-profile dev --allow-dirty --max-iterations 2
```
