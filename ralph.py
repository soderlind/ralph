#!/usr/bin/env python3
"""
Ralph SDLC Wrapper - CLI Entry Point

A full SDLC workflow orchestrator that integrates with vibe-kanban:
BRD → PRD → Tasks → Execute → Review → Cleanup
"""

from __future__ import annotations
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def now_iso() -> str:
    """Return current timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def log(msg: str) -> None:
    """Print timestamped log message."""
    print(f"[{now_iso()}] {msg}", flush=True)


def load_config(config_path: Path = Path("config/ralph.json")) -> Dict[str, Any]:
    """Load Ralph configuration from JSON."""
    if not config_path.exists():
        log(f"⚠️  Config not found: {config_path}, using defaults")
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def verify_skill_exists(skill_name: str) -> bool:
    """
    Verify that skill exists in project scope (.copilot/skills/ or .claude/skills/).
    
    Args:
        skill_name: Name of skill folder (e.g., 'brd-to-prd')
        
    Returns:
        True if skill found, False otherwise
    """
    copilot_skill = Path(f".copilot/skills/{skill_name}/skill.md")
    claude_skill = Path(f".claude/skills/{skill_name}/skill.md")
    
    if copilot_skill.exists() or claude_skill.exists():
        return True
    
    log(f"❌ Skill '{skill_name}' not found in project scope")
    log(f"   Run: ./scripts/sync-skills.sh")
    return False


def invoke_copilot(
    skill_name: str,
    task_prompt: str,
    model: Optional[str] = None,
    **kwargs
) -> str:
    """
    Invoke GitHub Copilot CLI with skill reference.
    
    Coding agent will load skill from .copilot/skills/ or .claude/skills/.
    
    Args:
        skill_name: Name of skill to use (e.g., 'brd-to-prd')
        task_prompt: The task/context for the skill to process
        model: Optional model override
        
    Returns:
        Copilot's response as string
    """
    config = load_config()
    
    # Get model from args or config
    if model is None:
        model = config.get("skills", {}).get("default_model", "claude-sonnet-4.5")
    
    # Build prompt with skill reference (coding agent loads it)
    full_prompt = f"@{skill_name} {task_prompt}"
    
    cmd = [
        "copilot",
        "--model", model,
        "--no-color",
        "--stream", "off",
        "-p", full_prompt
    ]
    
    log(f"🤖 Invoking Copilot with @{skill_name} (model: {model})...")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes
            check=True
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        log("❌ Copilot timed out (5 minutes)")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        log(f"❌ Copilot failed with exit code {e.returncode}")
        log(f"Error: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        log("❌ Copilot CLI not found. Install with: brew install github/gh/copilot")
        sys.exit(1)


def cmd_brd_prd(args: argparse.Namespace) -> int:
    """
    Handle 'ralph brd-prd' command.
    
    Reads BRD markdown file, invokes brd-to-prd skill, saves PRD markdown.
    """
    brd_path = Path(args.brd_file)
    
    if not brd_path.exists():
        log(f"❌ BRD file not found: {brd_path}")
        return 1
    
    # Verify skill exists in project scope
    skill_name = "brd-to-prd"
    if not verify_skill_exists(skill_name):
        return 1
    
    log(f"📖 Reading BRD: {brd_path}")
    brd_content = brd_path.read_text(encoding="utf-8")
    
    # Build task prompt (skill will be loaded by coding agent)
    task_prompt = f"""Generate a PRD (Product Requirements Document) in MARKDOWN format from this BRD.

BRD File: {brd_path}

---

{brd_content}

---

Output the PRD as clean markdown with proper sections:
- Overview
- Jobs To Be Done (JTBD)
- Acceptance Criteria
- User Flows
- Page Flows
- Technical Constraints
- Success Metrics
- Out of Scope

Output ONLY the markdown content (no code fences, no JSON, just markdown)."""
    
    # Invoke Copilot (it loads @brd-to-prd from project scope)
    config = load_config()
    skill_config = config.get("skills", {}).get("brd_to_prd", {})
    model = skill_config.get("model", "claude-sonnet-4.5")
    
    response = invoke_copilot(skill_name, task_prompt, model=model)
    
    # Clean response - remove markdown code fences if present
    response_cleaned = response.strip()
    import re
    
    # Remove markdown code fences (```markdown or ``` at start/end)
    if response_cleaned.startswith("```markdown"):
        response_cleaned = response_cleaned.split("```markdown", 1)[1]
    elif response_cleaned.startswith("```md"):
        response_cleaned = response_cleaned.split("```md", 1)[1]
    elif response_cleaned.startswith("```"):
        response_cleaned = response_cleaned.split("```", 1)[1]
    
    if response_cleaned.endswith("```"):
        response_cleaned = response_cleaned.rsplit("```", 1)[0]
    
    response_cleaned = response_cleaned.strip()
    
    # Save PRD as markdown
    output_path = Path(args.output or config.get("paths", {}).get("prd", "plans/generated-prd.md"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(response_cleaned + "\n", encoding="utf-8")
    
    log(f"✅ PRD generated successfully!")
    log(f"💾 Saved to: {output_path}")
    log("")
    log("📋 PRD is in markdown format - human-readable and LLM-parseable")
    log("")
    log("👉 Next step: Review the PRD, then run:")
    log(f"   ralph prd-tasks {output_path}")
    
    return 0


def cmd_prd_tasks(args: argparse.Namespace) -> int:
    """
    Handle 'ralph prd' command.
    
    Reads PRD markdown file, invokes prd-to-tasks skill, saves tasks.json.
    """
    prd_path = Path(args.prd_file)
    
    if not prd_path.exists():
        log(f"❌ PRD file not found: {prd_path}")
        return 1
    
    # Verify skill exists in project scope
    skill_name = "prd-to-tasks"
    if not verify_skill_exists(skill_name):
        return 1
    
    log(f"📖 Reading PRD: {prd_path}")
    prd_content = prd_path.read_text(encoding="utf-8")
    
    # Build task prompt (skill will be loaded by coding agent)
    task_prompt = f"""Break down this PRD into atomic, actionable tasks with dependencies.

PRD File: {prd_path}

---

{prd_content}

---

Output ONLY the tasks JSON array (no markdown fences, no extra text)."""
    
    # Invoke Copilot (it loads @prd-to-tasks from project scope)
    config = load_config()
    skill_config = config.get("skills", {}).get("prd_to_tasks", {})
    model = skill_config.get("model", "claude-sonnet-4.5")
    
    response = invoke_copilot(skill_name, task_prompt, model=model)
    
    # Parse and validate JSON
    # Strip markdown artifacts and leading characters
    response_cleaned = response.strip()
    import re
    
    # Remove ANSI color codes and control characters
    response_cleaned = re.sub(r'\x1b\[[0-9;]*m', '', response_cleaned)
    response_cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response_cleaned)
    
    # Remove leading bullets, asterisks, spaces
    response_cleaned = re.sub(r'^[●\*\-\s]+', '', response_cleaned, flags=re.MULTILINE)
    
    # Extract JSON from markdown code fences
    if "```json" in response_cleaned:
        parts = response_cleaned.split("```json", 1)
        if len(parts) > 1:
            json_part = parts[1].split("```", 1)[0]
            response_cleaned = json_part.strip()
    elif "```" in response_cleaned:
        # Try to find JSON between backticks
        parts = response_cleaned.split("```")
        if len(parts) >= 3:
            response_cleaned = parts[1].strip()
    
    # Try to extract just the JSON array/object
    # Find first [ or { and last ] or }
    start_idx = min(
        (response_cleaned.find('[') if '[' in response_cleaned else len(response_cleaned)),
        (response_cleaned.find('{') if '{' in response_cleaned else len(response_cleaned))
    )
    
    if start_idx < len(response_cleaned):
        # Determine if it's array or object
        is_array = response_cleaned[start_idx] == '['
        end_char = ']' if is_array else '}'
        
        # Find matching closing bracket/brace
        bracket_count = 0
        end_idx = -1
        for i in range(start_idx, len(response_cleaned)):
            if response_cleaned[i] in '[{':
                bracket_count += 1
            elif response_cleaned[i] in ']}':
                bracket_count -= 1
                if bracket_count == 0:
                    end_idx = i + 1
                    break
        
        if end_idx > start_idx:
            response_cleaned = response_cleaned[start_idx:end_idx]
    
    response_cleaned = response_cleaned.strip()
    
    try:
        tasks_data = json.loads(response_cleaned)
    except json.JSONDecodeError as e:
        log(f"⚠️  Response is not valid JSON, saving as-is")
        log(f"Parse error: {e}")
        # Save raw response for debugging
        output_path = Path(args.output or "plans/tasks.txt")
        output_path.write_text(response, encoding="utf-8")
        log(f"💾 Saved raw response to: {output_path}")
        log("⚠️  Please manually convert to JSON or re-run")
        return 1
    
    # Validate it's an array
    if not isinstance(tasks_data, list):
        log(f"❌ Expected tasks JSON array, got: {type(tasks_data).__name__}")
        return 1
    
    # Save tasks
    output_path = Path(args.output or "plans/tasks.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(tasks_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    
    log(f"✅ Tasks generated successfully!")
    log(f"💾 Saved to: {output_path}")
    log("")
    
    # Display summary
    log("📋 Tasks Summary:")
    log(f"  - Total tasks: {len(tasks_data)}")
    
    # Count by category
    categories = {}
    for task in tasks_data:
        cat = task.get("category", "uncategorized")
        categories[cat] = categories.get(cat, 0) + 1
    
    log(f"  - Categories:")
    for cat, count in sorted(categories.items()):
        log(f"    • {cat}: {count}")
    
    # Count tasks with dependencies
    tasks_with_deps = sum(1 for t in tasks_data if t.get("dependencies"))
    log(f"  - Tasks with dependencies: {tasks_with_deps}")
    
    # Flag uncertain dependencies for review
    uncertain_tasks = [t for t in tasks_data if t.get("uncertain_dependencies")]
    if uncertain_tasks:
        log("")
        log(f"⚠️  {len(uncertain_tasks)} task(s) have uncertain dependencies - please review:")
        for task in uncertain_tasks[:5]:  # Show first 5
            log(f"    • Task {task.get('id')}: {task.get('description', 'N/A')[:60]}")
        if len(uncertain_tasks) > 5:
            log(f"    ... and {len(uncertain_tasks) - 5} more")
    
    log("")
    log("Next steps:")
    log("  1. Review tasks in: " + str(output_path))
    log("  2. Adjust dependencies if needed")
    log("  3. Create tasks in Vibe Kanban: ralph tasks")
    
    return 0


def cmd_tasks_kanban(args: argparse.Namespace) -> int:
    """
    Handle 'ralph tasks-kanban' command.
    
    Creates tasks in Vibe Kanban via MCP using coding agent.
    Defaults to plans/tasks.json if no path provided.
    """
    config = load_config()
    tasks_path = Path(args.tasks_file or config["paths"]["tasks"])
    
    if not tasks_path.exists():
        if args.tasks_file:
            log(f"❌ Tasks file not found: {tasks_path}")
        else:
            log(f"❌ Tasks file not found: {tasks_path} (default location)")
            log(f"💡 Generate tasks first: ralph prd-tasks <prd-file>")
        return 1
    
    log(f"📖 Reading tasks: {tasks_path}")
    tasks_content = tasks_path.read_text(encoding="utf-8")
    
    try:
        tasks_data = json.loads(tasks_content)
    except json.JSONDecodeError as e:
        log(f"❌ Invalid tasks JSON: {e}")
        return 1
    
    if not isinstance(tasks_data, list):
        log(f"❌ Expected tasks JSON array")
        return 1
    
    # Test if vibe-kanban MCP is running
    log("🔍 Checking if vibe-kanban MCP is running...")
    model = config.get("vibe_kanban", {}).get("model", "claude-sonnet-4.5")
    
    try:
        test_result = subprocess.run(
            ["copilot", "--model", model, "--no-color", "--stream", "off", "-p", 
             "Use the vibe_kanban-list_projects MCP tool to list all projects. Return only 'OK' if the tool is available, or 'ERROR' if not."],
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )
        
        if "OK" in test_result.stdout or "vibe_kanban" in test_result.stdout.lower():
            log("✅ vibe-kanban MCP is running")
        else:
            log("❌ vibe-kanban MCP may not be running")
            log("💡 Please ensure vibe-kanban MCP is configured in your MCP settings")
            log("   See config/mcp-config.json for configuration example")
            return 1
    except Exception as e:
        log(f"❌ Failed to connect to vibe-kanban MCP: {e}")
        log("💡 Please ensure vibe-kanban MCP is running")
        return 1
    
    # Get project name from config
    project_name = config.get("vibe_kanban", {}).get("project_name")
    
    if project_name:
        log(f"📋 Using configured project: {project_name}")
    else:
        log("📋 No project name configured. Will prompt for selection...")
    
    # Build comprehensive prompt that handles project selection
    log("🤖 Preparing task creation via MCP...")
    model = config.get("vibe_kanban", {}).get("model", "claude-sonnet-4.5")
    
    # Build task creation prompt with project selection logic
    task_list = "\n".join([f"- {t['id']}: {t['description']}" for t in tasks_data[:5]])
    if len(tasks_data) > 5:
        task_list += f"\n... and {len(tasks_data) - 5} more tasks"
    
    agent_prompt = f"""You are helping create tasks in Vibe Kanban.

STEP 1: Get the project
Use vibe_kanban-list_projects to list all available projects.

{"STEP 2: Find project '" + project_name + "'" if project_name else "STEP 2: Ask user to select a project"}
{f"Look for a project with name matching '{project_name}' (case insensitive)." if project_name else "Show the user the list of projects and ask them to type the project name."}
{f"If found, use that project's ID. If not found, show available projects and ask user to select." if project_name else ""}

STEP 3: Create all {len(tasks_data)} tasks
Use vibe_kanban-create_task for each task with:
- project_id: (from step 2)
- title: Task ID + description (e.g., "TASK-001: Create TEST.md file")
- description: Full task details including steps, acceptance criteria, and dependencies

Tasks to create:
{task_list}

Full task data is in the JSON below:
{json.dumps(tasks_data, indent=2)}

After creating all tasks, respond with:
"✅ Created {len(tasks_data)} tasks in project [project_name]"
"""
    
    log(f"🚀 Creating {len(tasks_data)} tasks in Vibe Kanban...")
    log("   (This may take a minute...)")
    
    try:
        result = subprocess.run(
            ["copilot", "--model", model, "-p", agent_prompt],
            text=True,
            timeout=300,
            check=True
        )
        
        log("✅ Tasks created successfully!")
        log(f"💡 View tasks at: https://vibekanban.com/")
        return 0
        
    except subprocess.TimeoutExpired:
        log("❌ Task creation timed out (>5 minutes)")
        return 1
    except Exception as e:
        log(f"❌ Failed to create tasks: {e}")
        return 1


def cmd_run(args: argparse.Namespace) -> int:
    """
    Handle 'ralph run' command.
    
    Starts tasks with no dependencies from Vibe Kanban.
    Can be called multiple times for progressive execution.
    """
    config = load_config()
    
    # Get project_id from args or config
    project_id = args.project_id if hasattr(args, 'project_id') and args.project_id else None
    if not project_id:
        project_id = config.get("vibe_kanban", {}).get("project_id")
    
    if not project_id:
        log("❌ No project_id configured")
        log("💡 Set vibe_kanban.project_id in config/ralph.json or use --project-id")
        return 1
    
    log(f"🚀 Starting tasks from Vibe Kanban project: {project_id}")
    
    # Auto-detect current git repository
    log("🔍 Detecting current git repository...")
    try:
        # Get remote URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10
        )
        repo_url = result.stdout.strip()
        
        # Extract repo name from URL
        # Handle both https://github.com/user/repo.git and git@github.com:user/repo.git
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]
        repo_name = repo_url.split("/")[-1]
        
        log(f"✅ Repository: {repo_name}")
    except Exception as e:
        log(f"❌ Failed to detect git repository: {e}")
        log("💡 Make sure you're in a git repository")
        return 1
    
    # Get repo config
    repo_config = config.get("vibe_kanban", {}).get("repo_config", {})
    base_branch = repo_config.get("base_branch", "main")
    
    # Step 1: List tasks with status='todo' from Vibe Kanban
    log("📋 Fetching todo tasks from Vibe Kanban...")
    
    model = config.get("vibe_kanban", {}).get("model", "claude-sonnet-4.5")
    
    list_prompt = f"""Use the vibe_kanban-list_tasks MCP tool to get all tasks with status='todo' from project {project_id}.

Return ONLY a JSON array of tasks with these fields:
[
  {{
    "task_id": "uuid",
    "title": "task title",
    "description": "task description (may contain dependencies)"
  }},
  ...
]

Output ONLY the JSON array, no markdown fences, no extra text."""
    
    try:
        result = subprocess.run(
            ["copilot", "--model", model, "--no-color", "--stream", "off", "-p", list_prompt],
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )
        response = result.stdout.strip()
        
        # Clean and parse JSON
        import re
        response_cleaned = re.sub(r'\x1b\[[0-9;]*m', '', response)
        response_cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response_cleaned)
        
        if "```json" in response_cleaned:
            response_cleaned = response_cleaned.split("```json", 1)[1].split("```")[0]
        elif "```" in response_cleaned:
            response_cleaned = response_cleaned.split("```", 1)[1].split("```")[0]
        
        tasks = json.loads(response_cleaned.strip())
        
        if not tasks:
            log("✅ No tasks in todo status")
            log("💡 All tasks may be in progress or completed!")
            return 0
        
        log(f"✅ Found {len(tasks)} todo tasks")
        
    except Exception as e:
        log(f"❌ Failed to fetch tasks: {e}")
        return 1
    
    # Step 2: Filter tasks with valid Ralph task IDs
    log("🔍 Filtering tasks with valid task IDs...")
    
    valid_tasks = []
    skipped_tasks = []
    
    import re
    task_id_pattern = re.compile(r'\b([A-Z]+-\d+)\b')
    
    for task in tasks:
        title = task.get("title", "")
        description = task.get("description", "")
        
        # Look for task ID pattern in title or description
        match = task_id_pattern.search(title + " " + description)
        
        if match:
            # Extract and store the Ralph task ID
            task["ralph_task_id"] = match.group(1)
            valid_tasks.append(task)
        else:
            skipped_tasks.append(task)
    
    log(f"✅ Valid Ralph tasks: {len(valid_tasks)}")
    if skipped_tasks:
        log(f"⏭️  Skipped (no task ID): {len(skipped_tasks)} tasks")
    
    if not valid_tasks:
        log("")
        log("💡 No valid Ralph tasks found in todo status")
        log("   Tasks created by ralph should have IDs like TASK-001, TASK-002, etc.")
        return 0
    
    # Step 3: Parse dependencies and filter ready tasks
    log("🔍 Analyzing dependencies...")
    
    ready_tasks = []
    blocked_tasks = []
    
    for task in tasks:
        description = task.get("description", "")
        
        # Parse dependencies using regex patterns
        # Look for: "Depends on: TASK-001, TASK-002" or "Dependencies: TASK-XXX"
        import re
        dep_patterns = [
            r'Depends on:\s*([A-Z]+-\d+(?:\s*,\s*[A-Z]+-\d+)*)',
            r'Dependencies:\s*([A-Z]+-\d+(?:\s*,\s*[A-Z]+-\d+)*)',
            r'Dependency:\s*([A-Z]+-\d+)',
        ]
        
        has_dependencies = False
        for pattern in dep_patterns:
            if re.search(pattern, description, re.IGNORECASE):
                has_dependencies = True
                break
        
        if has_dependencies:
            blocked_tasks.append(task)
        else:
            ready_tasks.append(task)
    
    log(f"✅ Ready to start: {len(ready_tasks)} tasks")
    log(f"⏸️  Blocked by dependencies: {len(blocked_tasks)} tasks")
    
    if not ready_tasks:
        log("")
        log("💡 No tasks ready to start (all have dependencies)")
        log("   Complete some tasks first, then run 'ralph run' again")
        return 0
    
    # Step 4: Respect max_parallel_tasks limit
    max_parallel = config.get("execution", {}).get("max_parallel_tasks", 3)
    tasks_to_start = ready_tasks[:max_parallel]
    
    if len(ready_tasks) > max_parallel:
        log(f"⚠️  Limiting to {max_parallel} tasks (max_parallel_tasks config)")
    
    # Step 5: Start workspace sessions
    log(f"\n🚀 Starting {len(tasks_to_start)} workspace sessions...")
    
    executor = config.get("vibe_kanban", {}).get("executor", "CLAUDE_CODE")
    variant = config.get("vibe_kanban", {}).get("variant")
    
    started = []
    failed = []
    
    for task in tasks_to_start:
        task_id = task.get("task_id")
        title = task.get("title", "Untitled")
        ralph_task_id = task.get("ralph_task_id", "UNKNOWN")
        
        log(f"\n📌 Starting: [{ralph_task_id}] {title}")
        log(f"   Vibe Kanban ID: {task_id}")
        
        # Build prompt to start workspace session
        start_prompt = f"""Use the vibe_kanban-start_workspace_session MCP tool to start work on task {task_id}.

Parameters:
- task_id: {task_id}
- executor: {executor}
{"- variant: " + variant if variant else ""}
- repos: [
    {{
      "repo": "{repo_name}",
      "base_branch": "{base_branch}"
    }}
  ]

After starting, return a JSON response:
{{
  "success": true,
  "task_id": "{task_id}",
  "message": "Workspace started"
}}

Or if failed:
{{
  "success": false,
  "task_id": "{task_id}",
  "error": "error message"
}}"""
        
        try:
            result = subprocess.run(
                ["copilot", "--model", model, "--no-color", "--stream", "off", "-p", start_prompt],
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
            
            # Consider it started if command succeeded
            started.append({"task_id": task_id, "title": title, "ralph_id": ralph_task_id})
            log(f"   ✅ Started")
            
        except Exception as e:
            failed.append({"task_id": task_id, "title": title, "ralph_id": ralph_task_id, "error": str(e)})
            log(f"   ❌ Failed: {e}")
    
    # Step 6: Report summary
    log("\n" + "="*60)
    log("📊 Summary")
    log("="*60)
    log(f"✅ Started: {len(started)} tasks")
    for task in started:
        ralph_id = task.get('ralph_id', 'N/A')
        log(f"   • [{ralph_id}] {task['title']} ({task['task_id']})")
    
    if failed:
        log(f"\n❌ Failed: {len(failed)} tasks")
        for task in failed:
            ralph_id = task.get('ralph_id', 'N/A')
            log(f"   • [{ralph_id}] {task['title']} ({task['task_id']})")
            log(f"     Error: {task['error']}")
    
    if skipped_tasks:
        log(f"\n⏭️  Skipped: {len(skipped_tasks)} tasks (no Ralph task ID)")
        for task in skipped_tasks[:5]:  # Show first 5
            log(f"   • {task.get('title', 'Untitled')}")
        if len(skipped_tasks) > 5:
            log(f"   ... and {len(skipped_tasks) - 5} more")
    
    if blocked_tasks:
        log(f"\n⏸️  Blocked: {len(blocked_tasks)} tasks (have dependencies)")
    
    if len(ready_tasks) > max_parallel:
        remaining = len(ready_tasks) - max_parallel
        log(f"\n💡 {remaining} more tasks ready - run 'ralph run' again to start them")
    
    log("")
    log("👉 Next steps:")
    log("   1. Monitor task progress in Vibe Kanban dashboard")
    log("   2. Run 'ralph run' again to start more tasks")
    log("   3. Review completed work: ralph review")
    
    return 0 if not failed else 1


def cmd_review(args: argparse.Namespace) -> int:
    """
    Handle 'ralph review' command.
    
    Reviews completed tasks, appends to implementation-log.md.
    By default, auto-runs cleanup unless --no-cleanup flag is set.
    """
    config = load_config()
    
    # Get project_id from config
    project_id = config.get("vibe_kanban", {}).get("project_id")
    if not project_id:
        log("❌ No project_id configured")
        log("💡 Set vibe_kanban.project_id in config/ralph.json")
        return 1
    
    log(f"📋 Reviewing completed tasks from Vibe Kanban project: {project_id}")
    
    # Step 1: List tasks with status='done' from Vibe Kanban
    log("🔍 Fetching done tasks...")
    
    model = config.get("vibe_kanban", {}).get("model", "claude-sonnet-4.5")
    
    list_prompt = f"""Use the vibe_kanban-list_tasks MCP tool to get all tasks with status='done' from project {project_id}.

Return ONLY a JSON array of tasks with these fields:
[
  {{
    "task_id": "uuid",
    "title": "task title",
    "description": "task description (full details)"
  }},
  ...
]

Output ONLY the JSON array, no markdown fences, no extra text."""
    
    try:
        result = subprocess.run(
            ["copilot", "--model", model, "--no-color", "--stream", "off", "-p", list_prompt],
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )
        response = result.stdout.strip()
        
        # Clean and parse JSON
        import re
        response_cleaned = re.sub(r'\x1b\[[0-9;]*m', '', response)
        response_cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response_cleaned)
        
        if "```json" in response_cleaned:
            response_cleaned = response_cleaned.split("```json", 1)[1].split("```")[0]
        elif "```" in response_cleaned:
            response_cleaned = response_cleaned.split("```", 1)[1].split("```")[0]
        
        done_tasks = json.loads(response_cleaned.strip())
        
        if not done_tasks:
            log("✅ No tasks to review (no done tasks)")
            return 0
        
        log(f"✅ Found {len(done_tasks)} done tasks")
        
    except Exception as e:
        log(f"❌ Failed to fetch done tasks: {e}")
        return 1
    
    # Step 2: Filter tasks with valid Ralph task IDs
    log("🔍 Filtering tasks with Ralph IDs...")
    
    valid_tasks = []
    task_id_pattern = re.compile(r'\b([A-Z]+-\d+)\b')
    
    for task in done_tasks:
        title = task.get("title", "")
        description = task.get("description", "")
        
        match = task_id_pattern.search(title + " " + description)
        if match:
            task["ralph_task_id"] = match.group(1)
            valid_tasks.append(task)
    
    if not valid_tasks:
        log("⚠️  No valid Ralph tasks found in done status")
        log("💡 Only tasks with IDs like TASK-001 are reviewed")
        return 0
    
    log(f"✅ Reviewing {len(valid_tasks)} Ralph tasks")
    
    # Step 3: Generate reviews using @task-review skill
    log("\n📝 Generating task reviews...")
    
    reviews = []
    failed_reviews = []
    
    for task in valid_tasks:
        ralph_id = task.get("ralph_task_id", "UNKNOWN")
        title = task.get("title", "Untitled")
        description = task.get("description", "")
        
        log(f"\n  Reviewing: [{ralph_id}] {title}")
        
        # Build prompt for @task-review skill
        review_prompt = f"""Review this completed task and generate a summary.

Task ID: {ralph_id}
Title: {title}

Description:
{description}

Generate a markdown summary with:
- Status: Completed
- Summary: Brief description of what was implemented
- Technical Decisions: Key technical choices made
- Challenges: Any challenges encountered
- Follow-ups: Any follow-up work needed

Output ONLY the markdown summary (no code fences, no extra text).
Start with: ### {ralph_id}: {title}"""
        
        try:
            # Use @task-review skill
            review_response = invoke_copilot("task-review", review_prompt, model=model)
            
            # Clean response
            review_cleaned = review_response.strip()
            if review_cleaned.startswith("```markdown"):
                review_cleaned = review_cleaned.split("```markdown", 1)[1]
            elif review_cleaned.startswith("```"):
                review_cleaned = review_cleaned.split("```", 1)[1]
            if review_cleaned.endswith("```"):
                review_cleaned = review_cleaned.rsplit("```", 1)[0]
            review_cleaned = review_cleaned.strip()
            
            reviews.append(review_cleaned)
            log(f"  ✅ Reviewed")
            
        except Exception as e:
            log(f"  ⚠️  Review failed: {e}")
            failed_reviews.append({"id": ralph_id, "title": title, "error": str(e)})
    
    if not reviews:
        log("\n❌ All reviews failed")
        return 1
    
    # Step 4: Append to docs/implementation-log.md
    log(f"\n💾 Appending {len(reviews)} reviews to implementation log...")
    
    log_path = Path(config.get("paths", {}).get("implementation_log", "docs/implementation-log.md"))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build log entry
    log_entry = f"\n## [{now_iso()}] Task Review\n\n"
    log_entry += "\n\n".join(reviews)
    log_entry += "\n"
    
    # Append to log
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
        log(f"✅ Appended to: {log_path}")
    except Exception as e:
        log(f"❌ Failed to append to log: {e}")
        return 1
    
    # Step 5: Report summary
    log("\n" + "="*60)
    log("📊 Review Summary")
    log("="*60)
    log(f"✅ Reviewed: {len(reviews)} tasks")
    
    if failed_reviews:
        log(f"⚠️  Failed: {len(failed_reviews)} tasks")
        for item in failed_reviews:
            log(f"   • [{item['id']}] {item['title']}")
    
    # Step 6: Auto-run cleanup unless --no-cleanup
    no_cleanup = getattr(args, 'no_cleanup', False)
    
    if no_cleanup:
        log("\n💡 Skipping cleanup (--no-cleanup flag)")
        log("   Run 'ralph cleanup' when ready")
    else:
        log("\n🧹 Auto-running cleanup...")
        log("="*60)
        cleanup_result = cmd_cleanup(args)
        if cleanup_result != 0:
            log("⚠️  Cleanup encountered errors")
            return 1
    
    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    """
    Handle 'ralph cleanup' command.
    
    Cleans up completed tasks that have already been reviewed.
    Only processes tasks that exist in implementation-log.md AND are in done status.
    """
    config = load_config()
    
    # Get project_id from config
    project_id = config.get("vibe_kanban", {}).get("project_id")
    if not project_id:
        log("❌ No project_id configured")
        log("💡 Set vibe_kanban.project_id in config/ralph.json")
        return 1
    
    log(f"🧹 Cleaning up reviewed tasks from Vibe Kanban project: {project_id}")
    
    # Step 1: Read implementation-log.md to get reviewed task IDs
    log("📖 Reading implementation log...")
    
    log_path = Path(config.get("paths", {}).get("implementation_log", "docs/implementation-log.md"))
    
    if not log_path.exists():
        log(f"⚠️  Implementation log not found: {log_path}")
        log("💡 Run 'ralph review' first to review tasks")
        return 0
    
    # Parse log to extract reviewed task IDs
    reviewed_task_ids = set()
    try:
        log_content = log_path.read_text(encoding="utf-8")
        
        # Extract task IDs from log (look for patterns like TASK-001, TASK-002)
        import re
        task_id_pattern = re.compile(r'\b([A-Z]+-\d+)\b')
        matches = task_id_pattern.findall(log_content)
        reviewed_task_ids = set(matches)
        
        if not reviewed_task_ids:
            log("⚠️  No reviewed tasks found in implementation log")
            log("💡 Run 'ralph review' first to review tasks")
            return 0
        
        log(f"✅ Found {len(reviewed_task_ids)} reviewed task IDs in log")
        
    except Exception as e:
        log(f"❌ Failed to read implementation log: {e}")
        return 1
    
    # Step 2: List tasks with status='done' from Vibe Kanban
    log("🔍 Fetching done tasks...")
    
    model = config.get("vibe_kanban", {}).get("model", "claude-sonnet-4.5")
    
    list_prompt = f"""Use the vibe_kanban-list_tasks MCP tool to get all tasks with status='done' from project {project_id}.

Return ONLY a JSON array of tasks with these fields:
[
  {{
    "task_id": "uuid",
    "title": "task title",
    "description": "task description"
  }},
  ...
]

Output ONLY the JSON array, no markdown fences, no extra text."""
    
    try:
        result = subprocess.run(
            ["copilot", "--model", model, "--no-color", "--stream", "off", "-p", list_prompt],
            capture_output=True,
            text=True,
            timeout=60,
            check=True
        )
        response = result.stdout.strip()
        
        # Clean and parse JSON
        import re
        response_cleaned = re.sub(r'\x1b\[[0-9;]*m', '', response)
        response_cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response_cleaned)
        
        if "```json" in response_cleaned:
            response_cleaned = response_cleaned.split("```json", 1)[1].split("```")[0]
        elif "```" in response_cleaned:
            response_cleaned = response_cleaned.split("```", 1)[1].split("```")[0]
        
        done_tasks = json.loads(response_cleaned.strip())
        
        if not done_tasks:
            log("✅ No tasks to cleanup (no done tasks)")
            return 0
        
        log(f"✅ Found {len(done_tasks)} done tasks")
        
    except Exception as e:
        log(f"❌ Failed to fetch done tasks: {e}")
        return 1
    
    # Step 3: Filter tasks with valid Ralph task IDs, only if reviewed
    log("\n📦 Filtering reviewed tasks...")
    
    archived_tasks = []
    skipped_tasks = []
    task_id_pattern = re.compile(r'\b([A-Z]+-\d+)\b')
    archive_dir = Path(config.get("paths", {}).get("archive_dir", "plans/done"))
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    for task in done_tasks:
        title = task.get("title", "")
        description = task.get("description", "")
        
        match = task_id_pattern.search(title + " " + description)
        if match:
            ralph_id = match.group(1)
            
            # Check if this task has been reviewed
            if ralph_id not in reviewed_task_ids:
                skipped_tasks.append({"id": ralph_id, "title": title, "reason": "Not reviewed yet"})
                log(f"  ⏭️  {ralph_id}: Not reviewed yet (skipping)")
                continue
            
            # Archive task data
            archive_data = {
                "id": ralph_id,
                "title": title,
                "description": description,
                "kanban_id": task.get("task_id"),
                "completed_at": now_iso(),
                "archived_at": now_iso()
            }
            
            archive_path = archive_dir / f"{ralph_id}.json"
            try:
                archive_path.write_text(
                    json.dumps(archive_data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8"
                )
                archived_tasks.append({"id": ralph_id, "title": title, "kanban_id": task.get("task_id")})
                log(f"  ✅ {ralph_id}: {title}")
            except Exception as e:
                log(f"  ❌ Failed to archive {ralph_id}: {e}")
    
    if not archived_tasks:
        if skipped_tasks:
            log(f"\n⚠️  No reviewed tasks ready for cleanup")
            log(f"💡 {len(skipped_tasks)} tasks not reviewed yet - run 'ralph review' first")
        else:
            log("⚠️  No Ralph tasks found to archive")
        return 0
    
    log(f"\n✅ Archived {len(archived_tasks)} tasks to {archive_dir}/")
    
    # Step 3: Update tasks.json dependencies
    log("\n🔗 Updating task dependencies...")
    
    tasks_path = Path(config.get("paths", {}).get("tasks", "plans/tasks.json"))
    
    if not tasks_path.exists():
        log(f"⚠️  tasks.json not found: {tasks_path}")
        log("   Skipping dependency update")
    else:
        try:
            tasks_data = json.loads(tasks_path.read_text(encoding="utf-8"))
            
            completed_ids = {t["id"] for t in archived_tasks}
            updated_tasks = []
            
            for task in tasks_data:
                task_id = task.get("id")
                dependencies = task.get("dependencies", [])
                
                if dependencies:
                    # Remove completed task IDs from dependencies
                    new_dependencies = [dep for dep in dependencies if dep not in completed_ids]
                    
                    if len(new_dependencies) < len(dependencies):
                        removed = [dep for dep in dependencies if dep in completed_ids]
                        task["dependencies"] = new_dependencies
                        updated_tasks.append({"id": task_id, "removed": removed})
                        log(f"  ✅ {task_id}: Removed {removed}")
            
            # Save updated tasks.json
            tasks_path.write_text(
                json.dumps(tasks_data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8"
            )
            
            if updated_tasks:
                log(f"\n✅ Updated {len(updated_tasks)} tasks in {tasks_path}")
            else:
                log("\n💡 No dependency updates needed")
                
        except Exception as e:
            log(f"❌ Failed to update dependencies: {e}")
            return 1
    
    # Step 4: Run cleanup-worktrees script
    log("\n🔧 Running git worktree cleanup...")
    
    cleanup_script = Path("scripts/cleanup-worktrees.sh")
    
    if not cleanup_script.exists():
        log(f"⚠️  Cleanup script not found: {cleanup_script}")
        log("   Skipping worktree cleanup")
        worktree_output = "Script not found"
    else:
        try:
            result = subprocess.run(
                ["bash", str(cleanup_script)],
                capture_output=True,
                text=True,
                timeout=60
            )
            worktree_output = result.stdout.strip()
            
            if result.returncode == 0:
                log(f"✅ Worktree cleanup completed")
                if worktree_output:
                    log(f"   {worktree_output}")
            else:
                log(f"⚠️  Worktree cleanup exited with code {result.returncode}")
                log(f"   {result.stderr}")
                
        except Exception as e:
            log(f"⚠️  Failed to run cleanup script: {e}")
            worktree_output = f"Error: {e}"
    
    # Step 5: Delete tasks from Vibe Kanban
    log("\n🗑️  Deleting tasks from Vibe Kanban...")
    
    deleted_tasks = []
    failed_deletes = []
    
    for task in archived_tasks:
        kanban_id = task["kanban_id"]
        ralph_id = task["id"]
        
        delete_prompt = f"""Use the vibe_kanban-delete_task MCP tool to delete task {kanban_id} from Vibe Kanban.

After deletion, return a JSON response:
{{
  "success": true,
  "task_id": "{kanban_id}"
}}

Or if failed:
{{
  "success": false,
  "task_id": "{kanban_id}",
  "error": "error message"
}}"""
        
        try:
            subprocess.run(
                ["copilot", "--model", model, "--no-color", "--stream", "off", "-p", delete_prompt],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            deleted_tasks.append(ralph_id)
            log(f"  ✅ Deleted [{ralph_id}]")
            
        except Exception as e:
            failed_deletes.append({"id": ralph_id, "error": str(e)})
            log(f"  ⚠️  Failed to delete [{ralph_id}]: {e}")
    
    # Step 6: Append to docs/cleanup-log.md
    log("\n💾 Appending cleanup summary to log...")
    
    cleanup_log_path = Path(config.get("paths", {}).get("cleanup_log", "docs/cleanup-log.md"))
    cleanup_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build log entry
    log_entry = f"\n## [{now_iso()}] Cleanup\n\n"
    
    log_entry += "### Tasks Archived\n"
    for task in archived_tasks:
        log_entry += f"- {task['id']}: {task['title']} → {archive_dir}/{task['id']}.json\n"
    log_entry += f"Total: {len(archived_tasks)} tasks archived\n\n"
    
    if updated_tasks:
        log_entry += "### Dependencies Updated\n"
        for item in updated_tasks:
            log_entry += f"- {item['id']}: Removed dependencies on {item['removed']}\n"
        log_entry += f"Total: {len(updated_tasks)} tasks updated\n\n"
    
    log_entry += "### Git Worktrees\n"
    log_entry += f"{worktree_output}\n\n"
    
    log_entry += "### Vibe Kanban\n"
    log_entry += f"- Deleted {len(deleted_tasks)} completed tasks from project\n"
    if failed_deletes:
        log_entry += f"- Failed to delete {len(failed_deletes)} tasks\n"
    log_entry += "\n"
    
    # Append to log
    try:
        with open(cleanup_log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)
        log(f"✅ Appended to: {cleanup_log_path}")
    except Exception as e:
        log(f"❌ Failed to append to cleanup log: {e}")
        return 1
    
    # Step 7: Report summary
    log("\n" + "="*60)
    log("📊 Cleanup Summary")
    log("="*60)
    log(f"📦 Archived: {len(archived_tasks)} tasks")
    
    if skipped_tasks:
        log(f"⏭️  Skipped: {len(skipped_tasks)} tasks (not reviewed yet)")
    
    log(f"🔗 Updated: {len(updated_tasks) if updated_tasks else 0} tasks (dependencies)")
    log(f"🔧 Worktrees: Cleaned")
    log(f"🗑️  Deleted: {len(deleted_tasks)} tasks from Vibe Kanban")
    
    if failed_deletes:
        log(f"\n⚠️  Failed to delete {len(failed_deletes)} tasks:")
        for item in failed_deletes:
            log(f"   • [{item['id']}] {item['error']}")
    
    log("\n✅ Cleanup complete!")
    
    return 0 if not failed_deletes else 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ralph SDLC Wrapper - Full workflow orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ralph brd-prd plans/brd.md                # Generate PRD from BRD
  ralph prd-tasks plans/prd.md              # Generate tasks from PRD
  ralph tasks-kanban plans/tasks.json       # Create tasks in Vibe Kanban
  ralph run                                 # Start tasks with no dependencies
  ralph review plans/tasks.json             # Review completed tasks
  ralph cleanup                             # Cleanup completed work

Full workflow:
  1. ralph brd-prd plans/brd.md → generates plans/generated-prd.md
  2. ralph prd-tasks plans/generated-prd.md → generates plans/tasks.json
  3. ralph tasks-kanban plans/tasks.json → creates tasks in Vibe Kanban
  4. ralph run → starts tasks with no dependencies
  5. (work on tasks in Vibe Kanban)
  6. ralph review → reviews completed tasks
  7. ralph cleanup → archives, adjusts dependencies, removes worktrees
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # ralph brd-prd
    brd_prd_parser = subparsers.add_parser(
        "brd-prd",
        help="Generate PRD from BRD"
    )
    brd_prd_parser.add_argument(
        "brd_file",
        help="Path to BRD markdown file (e.g., plans/brd.md)"
    )
    brd_prd_parser.add_argument(
        "-o", "--output",
        help="Output path for PRD markdown (default: plans/generated-prd.md)"
    )
    
    # ralph prd-tasks
    prd_tasks_parser = subparsers.add_parser(
        "prd-tasks",
        help="Generate tasks from PRD"
    )
    prd_tasks_parser.add_argument(
        "prd_file",
        help="Path to PRD markdown file (e.g., plans/prd.md)"
    )
    prd_tasks_parser.add_argument(
        "-o", "--output",
        help="Output path for tasks JSON (default: plans/tasks.json)"
    )
    
    # ralph tasks-kanban
    tasks_kanban_parser = subparsers.add_parser(
        "tasks-kanban",
        help="Create tasks in Vibe Kanban via MCP"
    )
    tasks_kanban_parser.add_argument(
        "tasks_file",
        nargs="?",
        help="Path to tasks JSON file (default: plans/tasks.json)"
    )
    
    # ralph run
    run_parser = subparsers.add_parser(
        "run",
        help="Start tasks with no dependencies in Vibe Kanban"
    )
    run_parser.add_argument(
        "--project-id",
        help="Optional project ID (uses config if not provided)"
    )
    
    # ralph review
    review_parser = subparsers.add_parser(
        "review",
        help="Review completed tasks"
    )
    review_parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Skip automatic cleanup after review"
    )
    
    # ralph cleanup
    cleanup_parser = subparsers.add_parser(
        "cleanup",
        help="Cleanup completed tasks"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handler
    if args.command == "brd-prd":
        return cmd_brd_prd(args)
    elif args.command == "prd-tasks":
        return cmd_prd_tasks(args)
    elif args.command == "tasks-kanban":
        return cmd_tasks_kanban(args)
    elif args.command == "run":
        return cmd_run(args)
    elif args.command == "review":
        return cmd_review(args)
    elif args.command == "cleanup":
        return cmd_cleanup(args)
    else:
        log(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
