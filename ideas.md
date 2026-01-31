# Project Ideas & Enhancements

## 1. Override/Append Prompt for Each Phase Command
**Description**: Allow users to customize or append additional context to the AI prompt at each SDLC phase.

**Details**:
- Add `--prompt` or `--append-prompt` flag to phase commands (e.g., `ralph prd --append-prompt "focus on mobile-first"`)
- Store custom prompts per project or per phase
- Merge custom prompt with default phase instructions before sending to AI
- Use cases:
  - Add company-specific guidelines (security requirements, coding standards)
  - Add domain-specific context (fintech regulations, healthcare compliance)
  - Customize tone/style (formal vs casual, detailed vs concise)
  - Add project-specific constraints (tech stack, performance requirements)
- Implementation approach:
  - Config file per project or `.ralph.json`
  - CLI flag override + config file merging
  - Prompt templating system for reusability

---

## 2. Architecture Review First + Produce Docs in PRD Phase
**Description**: Make architecture design and documentation an optional/explicit step before or during PRD, as a gating function.

**Details**:
- Add `--review-architecture` flag to PRD command
- When enabled, PRD phase includes:
  - System design diagram (ASCII or structured format)
  - Component architecture breakdown
  - Data flow diagram
  - Integration points & external dependencies
  - Technology stack justification
  - Scalability & performance considerations
- Output as markdown docs that feed into final PRD
- Benefits:
  - Catches architectural issues early before dev starts
  - Creates shared understanding across team
  - Dev team has clearer technical specs
  - Reduces rework/refactoring during dev
- Gate logic:
  - Can require architecture approval before moving to Dev phase
  - Flag issues or unknowns that block development
- Implementation:
  - New sub-command or phase: `ralph architecture-review`
  - Or integrated into PRD with optional output sections

---

## 3. Test-Driven First + Produce Test Fixtures in PRD Phase
**Description**: Enable TDD (Test-Driven Development) workflow by generating test fixtures and acceptance test cases during PRD, before development starts.

**Details**:
- Add `--test-driven` flag to PRD command
- When enabled, PRD phase produces:
  - Test fixtures/mock data (JSON, CSV, SQL inserts)
  - Acceptance test cases (Gherkin/BDD format or Jest snapshots)
  - Unit test templates for acceptance criteria
  - Test data generation scripts
  - Edge case & negative test scenarios
- Output structure:
  - `tests/fixtures/` - mock data sets
  - `tests/acceptance/` - acceptance test specs
  - `tests/unit-templates/` - function test stubs
- Benefits:
  - Dev team writes code against clear test contracts
  - Reduces ambiguity in acceptance criteria
  - Tests document expected behavior upfront
  - Faster code review (tests already exist)
  - Lower defect rates
- Integration:
  - Test files auto-generated as PRD output
  - Dev phase references these tests
  - Review phase verifies code passes fixtures
- Implementation:
  - Template test generators (Jest, Gherkin, etc.)
  - Mock data faker integration
  - Parameterized test generation from user stories

---

## 4. Test-Driven Task Phase Before Development Features
**Description**: Insert explicit "Test-Driven" task phase that runs before Dev phase when `--test-driven` flag is enabled.

**Details**:
- New phase sequence: BRD → PRD → **TEST-DRIVEN** → Dev → Review → Done
- Test-Driven phase generates and validates:
  - Test fixtures and mock data
  - Acceptance test specs (BDD/Gherkin)
  - Unit test templates
  - Test data generation scripts
  - Edge case scenarios
- Kanban workflow:
  - Creates "Test Generation" task(s) from PRD user stories
  - Task moves through: Todo → In Progress → In Review → Done
  - Dev team pulls Dev tasks only after Test-Driven tasks are Done
  - Tests become deliverables (not just side-effect)
- Benefits:
  - Clear contract between QA/Test team and Dev team
  - Dev cannot start until tests are ready
  - Enforces test-first mindset
  - Reduces "gotchas" during code review
  - Test coverage is pre-planned, not afterthought
- Gating logic:
  - Block Dev phase entry until all Test-Driven tasks are Done
  - Visibility: highlight test coverage gaps
  - Metrics: track test creation velocity
- Implementation:
  - Phase command: `ralph test-driven` (when flag enabled in PRD)
  - Auto-create test tasks in Kanban board
  - Link Dev tasks to their corresponding Test-Driven tasks

---

## 5. Cleanup Phase with Centralized Test Validation Gate
**Description**: Add optional `--run-tests` flag to Cleanup phase to validate ALL test generation tasks are passing before final cleanup/done.

**Details**:
- New optional flag: `ralph cleanup --run-tests`
- When enabled, Cleanup phase:
  - Aggregates all test fixtures and acceptance tests from all tasks
  - Runs full test suite across all completed Dev tasks
  - Validates test results against acceptance criteria
  - Generates test coverage report
  - Flags failing tests or coverage gaps
  - Blocks cleanup if tests fail (requires fix)
- Test centralization:
  - Collect tests from all task phases (Test-Driven → Dev → Review)
  - Merge test suites by feature area
  - Run against code in current branch/PR
  - Report: pass/fail per test, per task, per feature
- Benefits:
  - Proof that "Done" is truly done before deployment
  - Prevents shipping with broken tests
  - Real validation that code meets acceptance criteria
  - Confidence for stakeholders: "tests pass = feature works"
  - Catches integration issues between tasks
- Gate logic:
  - Tests must PASS before moving to Done
  - If tests fail: task → back to Dev or Review
  - Metrics: track test pass rate, coverage % by task
- Implementation:
  - Centralized test runner (aggregates Jest, Gherkin, etc.)
  - Task metadata: link to test fixtures/specs
  - Report generation: HTML/Markdown summary
  - Optional: fail-fast vs collect-all-failures modes

---

---

## 6. Smart Task Creation CLI Command (`add-task`)
**Description**: New CLI command that intelligently enhances user task prompts using AI skills, then creates detailed tasks directly in Kanban board via MCP.

**Details**:
- New CLI command: `ralph add-task "user prompt description"`
- Interactive workflow:
  1. User provides quick task idea/description
  2. System analyzes prompt intent and context
  3. Routes to relevant **skills** for enhancement:
     - `ralph-task-review` skill: refine task description, acceptance criteria
     - `brainstorming` skill: explore requirements, edge cases, dependencies
     - `ralph-prd-to-tasks` skill: break down into atomic subtasks
     - `doc-coauthoring` skill: structure task documentation
  4. Skills enhance the prompt with:
     - Detailed task title and description
     - Clear acceptance criteria
     - Subtasks/dependencies
     - Estimated effort (if applicable)
     - Links to related tasks/phases
     - Technical constraints/considerations
  5. Display enriched task to user for review
  6. User approves or refines further
  7. Auto-create in Kanban board using MCP (`vibe_kanban` tools)

- Workflow examples:
  ```
  $ ralph add-task "fix login bug"
  # Skills enhance → detailed acceptance criteria, test cases, related tasks
  
  $ ralph add-task "add dark mode support"
  # Skills break down → UI tasks, API tasks, database tasks, test tasks
  
  $ ralph add-task "integrate payment gateway"
  # Skills identify → security review, compliance, architecture review, dev tasks
  ```

- Features:
  - `--skip-review` flag: auto-create without user approval
  - `--phase <phase>` flag: tag task to specific SDLC phase (dev, review, etc.)
  - `--link-to <task-id>` flag: create dependency on existing task
  - `--priority <high|medium|low>` flag: set priority
  - `--assignee <user>` flag: assign to team member
  - `--project <project-id>` flag: target specific project

- Benefits:
  - **Faster task creation**: no manual detailing required
  - **Consistent quality**: skills ensure standards (acceptance criteria, dependencies)
  - **Reduced planning overhead**: AI handles breakdown/structuring
  - **Better tracking**: auto-linked to phases, projects, other tasks
  - **Knowledge capture**: every task gets documented context
  - **Less rework**: acceptance criteria pre-vetted by skills

- Technical approach:
  - Parse user prompt for intent/context
  - Chain skill calls sequentially (each enhances previous output)
  - Aggregate skill outputs into structured task format
  - Map to Kanban MCP task structure
  - Create task via `vibe_kanban-create_task` with full details
  - Return task URL/ID for user

- Integration with SDLC phases:
  - Can be called from any phase (e.g., `ralph dev --add-task "...")
  - Auto-tags task with current phase context
  - Links to parent epic/story if in story-driven workflow
  - Inherits project-level config (custom prompts from Idea 1)

---

## 7. Run Tasks with Custom Model Parameters
**Description**: Allow users to execute tasks with custom model parameters and configuration options for fine-tuned control over AI behavior.

**Details**:
- Add parameters support for task execution commands
- Model configuration options:
  - Temperature control for creativity vs consistency
  - Max tokens for response length
  - Custom model selection (GPT-4, Claude, etc.)
  - System prompt overrides
  - Response format preferences (JSON, Markdown, etc.)
- Command syntax examples:
  ```
  $ ralph run-task <task-id> --model gpt-4 --temperature 0.7 --max-tokens 4000
  $ ralph run-task <task-id> --model claude-3-opus --system-prompt "Be concise"
  $ ralph dev --model-params temperature=0.3,max_tokens=2000
  ```
- Features:
  - `--model <model-name>` flag: select AI model (gpt-4, claude-3-opus, etc.)
  - `--temperature <0.0-1.0>` flag: control randomness/creativity
  - `--max-tokens <number>` flag: limit response length
  - `--system-prompt <text>` flag: add custom system instructions
  - `--format <json|markdown|yaml>` flag: specify output format
  - `--model-params <key=value,key=value>` flag: bulk parameter setting
  - Config file support: `.ralph.json` with default model params per phase
  - Task-level overrides: different params for different task types
- Use cases:
  - **Code generation**: lower temperature (0.2-0.4) for consistent, predictable code
  - **Creative brainstorming**: higher temperature (0.7-0.9) for diverse ideas
  - **Documentation**: medium temperature (0.5-0.6) for clear but engaging text
  - **Bug fixes**: low temperature + specific model for reliable solutions
  - **Architecture design**: high-quality model (GPT-4, Claude Opus) for complex reasoning
  - **Quick tasks**: faster/cheaper model for simple operations
- Benefits:
  - **Cost optimization**: use cheaper models for simple tasks, premium for complex
  - **Quality control**: tune parameters for specific task requirements
  - **Flexibility**: different phases can use different model strategies
  - **Experimentation**: A/B test different model configs for best results
  - **Consistency**: standardize model behavior across team with config files
- Configuration structure:
  ```json
  {
    "models": {
      "default": "gpt-4",
      "phases": {
        "dev": {
          "model": "claude-3-opus",
          "temperature": 0.3,
          "max_tokens": 4000
        },
        "prd": {
          "model": "gpt-4",
          "temperature": 0.6,
          "max_tokens": 3000
        },
        "brainstorm": {
          "model": "gpt-4",
          "temperature": 0.8,
          "max_tokens": 2000
        }
      },
      "task_types": {
        "bug_fix": {"temperature": 0.2},
        "feature": {"temperature": 0.5},
        "architecture": {"model": "claude-3-opus"}
      }
    }
  }
  ```
- Implementation approach:
  - Parse CLI flags and merge with config file
  - Pass parameters to AI provider APIs
  - Log model usage/costs per task for tracking
  - Validate parameters against model capabilities
  - Fallback to defaults if custom model unavailable

---

## Ideas Status
- [ ] Idea 1 - Override/Append Prompt - In discussion
- [ ] Idea 2 - Architecture Review First - In discussion
- [ ] Idea 3 - Test-Driven First + Fixtures - In discussion
- [ ] Idea 4 - Test-Driven Task Phase - In discussion
- [ ] Idea 5 - Cleanup with Test Validation - In discussion
- [ ] Idea 6 - Smart Task Creation - In discussion
- [ ] Idea 7 - Run Tasks with Custom Model Parameters - In discussion
