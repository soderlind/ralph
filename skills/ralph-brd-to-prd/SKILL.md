---
name: ralph-brd-to-prd
description: "Transform Business Requirements Documents (BRDs) into Product Requirements Documents (PRDs) in structured markdown format"
---

# BRD to PRD Transformation Skill

Transform Business Requirements Documents (BRDs) into comprehensive Product Requirements Documents (PRDs) in **markdown format**.

## Output Format: Markdown PRD

Generate a well-structured markdown document with these sections:

```markdown
# Product Requirements Document: [Project Name]

**Version:** 1.0.0  
**Created:** [ISO timestamp]  
**Source:** [BRD filename]

## Overview

[2-3 paragraph summary: what this product does, who it's for, why it matters]

## Jobs To Be Done (JTBD)

### Primary JTBD

1. **[Persona]**: When [persona] wants to [job], so they can [goal]
   - **Context**: [when/where this arises]
   - **Success**: [how we know it's done well]

2. **[Persona]**: When [persona] wants to [job], so they can [goal]
   - **Context**: [when/where this arises]
   - **Success**: [how we know it's done well]

## Acceptance Criteria

- [ ] **AC-001**: [Specific, measurable criterion]
  - **Given**: [initial condition]
  - **When**: [action/trigger]
  - **Then**: [expected outcome]

- [ ] **AC-002**: [Specific, measurable criterion]
  - **Given**: [initial condition]
  - **When**: [action/trigger]
  - **Then**: [expected outcome]

## User Flows

### Flow 1: [Name]

**Trigger**: [What initiates this]  
**Actors**: [Who's involved]

**Steps**:
1. [User action]
2. [System response]
3. [Next action]
4. [Outcome]

**Edge Cases**: [How to handle errors/exceptions]

## Page Flows

### Page: [Name]

**Route**: `/path`  
**Purpose**: [Why this page exists]

**Components**:
- [Component 1]: [Purpose]
- [Component 2]: [Purpose]

**Navigation**:
- From: [Previous pages]
- To: [Next pages]

## Technical Constraints

### Hard Constraints
1. **[Category]**: [Constraint]
   - **Rationale**: [Why]
   - **Impact**: [How it affects implementation]

### Soft Constraints
1. **[Category]**: [Preferred approach]
   - **Alternatives**: [What else could work]

## Success Metrics

| Metric | Target | Measurement | Timeframe |
|--------|--------|-------------|-----------|
| [Name] | [Value] | [How] | [When] |

## Out of Scope

- [Explicitly excluded feature 1]
- [Explicitly excluded feature 2]
```

## Guidelines

- **Be comprehensive**: Cover all BRD aspects
- **Be specific**: Use concrete examples, avoid vague terms
- **Be measurable**: Every criterion should be verifiable
- **Flag uncertainties**: Mark anything needing clarification
- **Output**: Return ONLY the markdown PRD (no code fences wrapping the whole thing)
