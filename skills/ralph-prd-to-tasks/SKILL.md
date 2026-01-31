---
name: ralph-prd-to-tasks
description: "Break down markdown PRDs into atomic, actionable tasks with dependencies"
---

# PRD to Tasks Breakdown Skill

Analyze markdown PRDs and decompose them into atomic implementation tasks.

## Input: Markdown PRD

You'll receive a structured markdown PRD with:
- Overview
- JTBD (Jobs To Be Done)
- Acceptance Criteria
- User/Page Flows
- Technical Constraints

## Output: Tasks JSON Array

Generate tasks in this JSON format:

```json
[
  {
    "id": "TASK-001",
    "category": "architecture|functional|testing|documentation",
    "description": "One-line task summary",
    "details": "Detailed explanation of what needs to be done",
    "steps": [
      "Step 1: Specific action",
      "Step 2: Next action",
      "Step 3: Final outcome"
    ],
    "acceptance": [
      "Criterion 1: How to verify task is done",
      "Criterion 2: Another verification method"
    ],
    "dependencies": ["TASK-XXX"],
    "priority": "high|medium|low",
    "status": "todo"
  }
]
```

## Task Breakdown Principles

1. **Atomic**: Each task independently testable
2. **Dependencies**: Flag sequential requirements
3. **Parallel-ready**: Group independent tasks
4. **Category-aware**: architecture → functional → testing → docs

## Dependency Rules

- Architecture tasks: Usually no dependencies (foundational)
- Functional tasks: May depend on architecture or other features
- Testing tasks: Depend on features they test
- Documentation: Depends on completed features

## Important

- Flag uncertain dependencies with "⚠️ Uncertain dependency" in details
- Output ONLY the JSON array (no markdown fences, no extra text)
- Make tasks atomic and actionable
