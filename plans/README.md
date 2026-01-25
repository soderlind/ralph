# Plans

This folder contains the PRD (Product Requirements Document) that Ralph uses to guide the AI agent.

## Files

| File | Purpose |
|------|---------|
| `prd.json` | Default PRD — your work items |
| `prd-<name>.json` | Optional per-prompt PRDs |

## `prd.json` Format

A JSON array of work items:

```json
[
  {
    "id": "feature-001",
    "category": "functional",
    "priority": 1,
    "description": "User can send a message and see it in chat",
    "details": "Implement basic messaging functionality with persistence",
    "steps": [
      "Create message input component",
      "Build send endpoint",
      "Display messages in chat feed",
      "Test: send message → appears in feed"
    ],
    "passes": false,
    "dependsOn": []
  },
  {
    "id": "feature-002",
    "category": "ui",
    "priority": 2,
    "description": "Mobile responsive layout",
    "details": "Ensure all pages work on mobile/tablet/desktop",
    "steps": [
      "Test on iPhone SE, iPad, 1920px desktop",
      "Verify touch-friendly buttons (≥44px)",
      "Fix layout shifts and spacing"
    ],
    "passes": false,
    "dependsOn": ["feature-001"]
  }
]
```

| Field | Description |
|-------|-------------|
| `id` | Unique identifier (e.g., `feature-001`) |
| `category` | `"functional"`, `"ui"`, `"architecture"`, `"content"`, `"documentation"` |
| `priority` | Execution order (1 = highest) |
| `description` | One-line requirement |
| `details` | Full context and rationale |
| `steps` | Detailed acceptance criteria and test steps |
| `passes` | `false` → `true` when complete |
| `dependsOn` | Array of prerequisite feature IDs |

## Best Practices

- **Keep items small** — one feature per agent iteration
- **Be specific** — clear acceptance criteria help the agent
- **Start with `passes: false`** — the agent flips it to `true`
- **Order by priority** — agent picks from the top
- **Add dependencies** — use `dependsOn` to control ordering
- **Include test steps** — helps agent verify work
- **Reuse existing tests** — reference tests from prerequisite features in `dependsOn`

## Test Reuse & Architecture Dependencies

Features that depend on earlier work should **reference and extend** tests from their dependencies. This ensures:

1. **Boilerplate/architecture tests remain passing** as new features are built
2. **New features layer on top** without breaking existing functionality
3. **Clear verification** that dependencies are working correctly

### Example: Chained Dependencies with Test Inheritance

```json
[
  {
    "id": "arch-001",
    "category": "architecture",
    "priority": 1,
    "description": "Setup TypeScript & testing framework",
    "steps": [
      "Create tsconfig.json with strict mode",
      "Install Jest and setup test runner",
      "Ensure pnpm typecheck && pnpm test passes"
    ],
    "passes": false,
    "dependsOn": []
  },
  {
    "id": "data-001",
    "category": "documentation",
    "priority": 2,
    "description": "Document user data model",
    "details": "Create data schema that auth and dashboard will use",
    "steps": [
      "Define User schema: { id, email, name, createdAt }",
      "Create src/types/user.ts with TypeScript types",
      "Write unit test: User type compiles and validates",
      "Ensure: pnpm typecheck && pnpm test (includes arch-001 tests)"
    ],
    "passes": false,
    "dependsOn": ["arch-001"]
  },
  {
    "id": "auth-001",
    "category": "functional",
    "priority": 3,
    "description": "Implement login with mock auth",
    "details": "Create auth system using User schema from data-001",
    "steps": [
      "Create login page component",
      "Build /api/auth/login endpoint (uses User type)",
      "Write tests: login creates session, User type validates",
      "Ensure: pnpm typecheck && pnpm test (all 3 features' tests pass)"
    ],
    "passes": false,
    "dependsOn": ["data-001"]
  },
  {
    "id": "dashboard-001",
    "category": "functional",
    "priority": 4,
    "description": "Build user dashboard",
    "details": "Display user profile from authenticated session",
    "steps": [
      "Create dashboard page (uses User type + auth)",
      "Fetch logged-in user and display profile",
      "Write integration test: login → dashboard shows correct user",
      "Ensure: pnpm typecheck && pnpm test (all 4 features' tests pass)"
    ],
    "passes": false,
    "dependsOn": ["auth-001"]
  }
]
```

### How Test Reuse Works

1. **arch-001** creates `pnpm test` infrastructure
2. **data-001** adds types and type-checking tests; runs **all previous tests**
3. **auth-001** builds auth logic; runs **all previous tests** + new auth tests
4. **dashboard-001** uses auth + types; runs **all tests** to verify nothing broke

Each feature's `steps` should explicitly call `pnpm typecheck && pnpm test` to verify:
- ✅ No TypeScript errors
- ✅ All previous features still work
- ✅ New feature tests pass

## Example: Stock Screening App

This repo includes a real PRD for a stock screening app (saham-apayak) with 13 features organized by priority:

```bash
# View the full PRD
cat plans/prd.json | jq '.[0:3]'  # First 3 items

# Run with it
./ralph.py --allow-profile safe --max-iterations 10
```

## Per-Prompt PRDs

Use `--prd` to specify a different PRD file:

```bash
./ralph.py --prd plans/prd-wordpress.json --allow-profile safe --max-iterations 10
```
