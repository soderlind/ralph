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
    Handle 'ralph brd' command.
    
    Reads BRD markdown file, invokes brd-to-prd skill, saves PRD JSON.
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
    task_prompt = f"""Generate a PRD from this BRD file.

BRD File: {brd_path}

---

{brd_content}

---

Output ONLY the PRD JSON (no markdown fences, no extra text)."""
    
    # Invoke Copilot (it loads @brd-to-prd from project scope)
    config = load_config()
    skill_config = config.get("skills", {}).get("brd_to_prd", {})
    model = skill_config.get("model", "claude-sonnet-4.5")
    
    response = invoke_copilot(skill_name, task_prompt, model=model)
    
    # Parse and validate JSON
    # Strip markdown artifacts and leading characters
    response_cleaned = response.strip()
    # Remove leading bullets, asterisks, spaces
    import re
    response_cleaned = re.sub(r'^[●\*\-\s]+', '', response_cleaned, flags=re.MULTILINE)
    # Remove markdown code fences
    if "```json" in response_cleaned:
        response_cleaned = response_cleaned.split("```json", 1)[1]
    if response_cleaned.endswith("```"):
        response_cleaned = response_cleaned.rsplit("```", 1)[0]
    response_cleaned = response_cleaned.strip()
    
    try:
        prd_data = json.loads(response_cleaned)
    except json.JSONDecodeError as e:
        log(f"⚠️  Response is not valid JSON, saving as-is")
        log(f"Parse error: {e}")
        # Save raw response for debugging
        output_path = Path(args.output or "plans/generated-prd.txt")
        output_path.write_text(response, encoding="utf-8")
        log(f"💾 Saved raw response to: {output_path}")
        log("⚠️  Please manually convert to JSON or re-run")
        return 1
    
    # Save PRD
    output_path = Path(args.output or "plans/generated-prd.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(prd_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    
    log(f"✅ PRD generated successfully!")
    log(f"💾 Saved to: {output_path}")
    log("")
    log("📋 PRD Summary:")
    log(f"  - Project: {prd_data.get('project_name', 'Unknown')}")
    log(f"  - JTBD: {len(prd_data.get('jtbd', []))} statements")
    log(f"  - Acceptance Criteria: {len(prd_data.get('acceptance_criteria', []))}")
    log(f"  - User Flows: {len(prd_data.get('user_flows', []))}")
    log(f"  - Technical Constraints: {len(prd_data.get('technical_constraints', []))}")
    log("")
    log("👉 Next step: Review the PRD, then run:")
    log(f"   ralph prd {output_path}")
    
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
    Handle 'ralph tasks' command.
    
    Creates tasks in Vibe Kanban via MCP using coding agent.
    """
    config = load_config()
    tasks_path = Path(args.tasks_file or config["paths"]["tasks"])
    
    if not tasks_path.exists():
        log(f"❌ Tasks file not found: {tasks_path}")
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
    
    # Check if vibe-kanban is installed
    log("🔍 Checking vibe-kanban installation...")
    try:
        subprocess.run(
            ["npx", "vibe-kanban", "--version"],
            capture_output=True,
            check=True,
            timeout=10
        )
        log("✅ vibe-kanban is installed")
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        log("❌ vibe-kanban not found. Installing...")
        try:
            subprocess.run(
                ["npx", "-y", "vibe-kanban@latest", "--version"],
                capture_output=True,
                check=True,
                timeout=30
            )
            log("✅ vibe-kanban installed")
        except Exception as e:
            log(f"❌ Failed to install vibe-kanban: {e}")
            return 1
    
    # Get or select project_id
    project_id = config.get("vibe_kanban", {}).get("project_id")
    
    if not project_id:
        log("📋 No project_id configured. Fetching projects...")
        
        # Generate prompt to list projects
        from lib.vibe_kanban_client import VibeKanbanClient
        vk_client = VibeKanbanClient()
        list_prompt = vk_client.generate_list_projects_prompt()
        
        # Invoke coding agent to get projects
        log("🤖 Fetching Vibe Kanban projects via MCP...")
        model = config.get("vibe_kanban", {}).get("model", "claude-sonnet-4.5")
        
        # Build prompt for agent
        agent_prompt = f"""{list_prompt}

Return ONLY a JSON array of projects with id, name, and description.
Format: [{{"id": "uuid", "name": "project name", "description": "desc"}}, ...]"""
        
        try:
            result = subprocess.run(
                ["copilot", "--model", model, "--no-color", "--stream", "off", "-p", agent_prompt],
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
            
            projects = json.loads(response_cleaned.strip())
            
            if not projects:
                log("❌ No projects found in Vibe Kanban")
                return 1
            
            # Display projects for selection
            log("\n📋 Available projects:")
            for i, proj in enumerate(projects, 1):
                log(f"  {i}. {proj.get('name', 'Unnamed')} ({proj.get('id', 'N/A')})")
            
            # Prompt user to select
            log("\n👉 Please select a project by number:")
            try:
                selection = int(input("Enter number: ")) - 1
                if 0 <= selection < len(projects):
                    project_id = projects[selection]["id"]
                    log(f"✅ Selected: {projects[selection]['name']}")
                    
                    # Optionally save to config
                    log(f"\n💡 Tip: Save this to config/ralph.json under vibe_kanban.project_id")
                else:
                    log("❌ Invalid selection")
                    return 1
            except (ValueError, KeyError) as e:
                log(f"❌ Invalid input: {e}")
                return 1
                
        except Exception as e:
            log(f"❌ Failed to fetch projects: {e}")
            return 1
    
    log(f"\n📦 Creating {len(tasks_data)} tasks in Vibe Kanban (project: {project_id})...")
    
    # Generate prompt to create all tasks
    from lib.vibe_kanban_client import VibeKanbanClient
    vk_client = VibeKanbanClient()
    
    # Build comprehensive prompt for creating all tasks
    create_prompt = f"""Create {len(tasks_data)} tasks in Vibe Kanban project {project_id}.

For each task below, use the vibe_kanban-create_task MCP tool with:
- project_id: {project_id}
- title: [task description]
- description: [task details, steps, and acceptance criteria formatted as markdown]

Tasks to create:

"""
    
    for task in tasks_data:
        task_desc = f"""
**Task ID**: {task.get('id')}
**Title**: {task.get('description')}
**Category**: {task.get('category')}

**Details**:
{task.get('details', 'N/A')}

**Steps**:
{chr(10).join(f"- {step}" for step in task.get('steps', []))}

**Acceptance Criteria**:
{chr(10).join(f"- {ac}" for ac in task.get('acceptance', []))}

**Dependencies**: {', '.join(task.get('dependencies', [])) or 'None'}
**Priority**: {task.get('priority', 'medium')}

---
"""
        create_prompt += task_desc
    
    create_prompt += """
After creating each task, save its Vibe Kanban task ID back to the tasks.json file by updating the 'kanban_id' field.

Return a JSON summary:
{
  "created": [count],
  "tasks": [
    {"id": "TASK-001", "kanban_id": "uuid", "status": "created"},
    ...
  ]
}
"""
    
    # Save prompt to temp file for debugging
    prompt_file = Path("plans/vibe-kanban-create-prompt.txt")
    prompt_file.write_text(create_prompt, encoding="utf-8")
    log(f"💾 Saved creation prompt to: {prompt_file}")
    
    # Invoke coding agent to create tasks
    log("🤖 Invoking coding agent to create tasks via MCP...")
    log("⏳ This may take a few minutes...")
    
    model = config.get("vibe_kanban", {}).get("model", "claude-sonnet-4.5")
    
    try:
        result = subprocess.run(
            ["copilot", "--model", model, "--no-color", "--stream", "off", "-p", create_prompt],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes for creating multiple tasks
            check=True
        )
        response = result.stdout.strip()
        
        log("✅ Tasks created in Vibe Kanban!")
        log(f"\n📋 Response:\n{response[:500]}...")
        
        # Try to parse summary
        try:
            import re
            response_cleaned = re.sub(r'\x1b\[[0-9;]*m', '', response)
            response_cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', response_cleaned)
            
            if "```json" in response_cleaned:
                response_cleaned = response_cleaned.split("```json", 1)[1].split("```")[0]
            
            summary = json.loads(response_cleaned.strip())
            
            log(f"\n✨ Created {summary.get('created', 0)} tasks")
            
            # Update tasks.json with kanban_ids
            if "tasks" in summary:
                for task_summary in summary["tasks"]:
                    task_id = task_summary.get("id")
                    kanban_id = task_summary.get("kanban_id")
                    
                    if task_id and kanban_id:
                        for task in tasks_data:
                            if task.get("id") == task_id:
                                task["kanban_id"] = kanban_id
                                task["status"] = "todo"
                                break
                
                # Save updated tasks.json
                tasks_path.write_text(
                    json.dumps(tasks_data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8"
                )
                log(f"💾 Updated {tasks_path} with kanban_ids")
        except Exception as e:
            log(f"⚠️  Could not parse summary: {e}")
        
        log("")
        log("Next steps:")
        log("  1. View tasks in Vibe Kanban dashboard")
        log("  2. Start working on tasks: ralph run")
        
        return 0
        
    except subprocess.TimeoutExpired:
        log("❌ Task creation timed out (5 minutes)")
        return 1
    except subprocess.CalledProcessError as e:
        log(f"❌ Failed to create tasks: {e.stderr}")
        return 1
    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        return 1


def cmd_review(args: argparse.Namespace) -> int:
    """
    Handle 'ralph review' command.
    
    Reviews completed tasks, appends to implementation-log.md.
    """
    log("🚧 'ralph review' not yet implemented")
    return 1


def cmd_cleanup(args: argparse.Namespace) -> int:
    """
    Handle 'ralph cleanup' command.
    
    Cleans up completed tasks, adjusts dependencies, runs cleanup script.
    """
    log("🚧 'ralph cleanup' not yet implemented")
    return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ralph SDLC Wrapper - Full workflow orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ralph brd plans/brd.md                    # Generate PRD from BRD
  ralph prd plans/prd.md                    # Generate tasks from PRD
  ralph tasks plans/tasks.json              # Create tasks in Vibe Kanban
  ralph review plans/tasks.json             # Review completed tasks
  ralph cleanup                             # Cleanup completed work

Full workflow:
  1. ralph brd plans/brd.md → generates plans/generated-prd.md
  2. ralph prd plans/generated-prd.md → generates plans/tasks.json
  3. ralph tasks plans/tasks.json → creates tasks in Vibe Kanban
  4. (work on tasks in Vibe Kanban)
  5. ralph review plans/tasks.json → appends to docs/implementation-log.md
  6. ralph cleanup → archives, adjusts dependencies, removes worktrees
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # ralph brd
    brd_parser = subparsers.add_parser(
        "brd",
        help="Generate PRD from BRD"
    )
    brd_parser.add_argument(
        "brd_file",
        help="Path to BRD markdown file (e.g., plans/brd.md)"
    )
    brd_parser.add_argument(
        "-o", "--output",
        help="Output path for PRD JSON (default: plans/generated-prd.json)"
    )
    
    # ralph prd
    prd_parser = subparsers.add_parser(
        "prd",
        help="Generate tasks from PRD"
    )
    prd_parser.add_argument(
        "prd_file",
        help="Path to PRD JSON file (e.g., plans/prd.json)"
    )
    prd_parser.add_argument(
        "-o", "--output",
        help="Output path for tasks JSON (default: plans/tasks.json)"
    )
    
    # ralph tasks
    tasks_parser = subparsers.add_parser(
        "tasks",
        help="Create tasks in Vibe Kanban via MCP"
    )
    tasks_parser.add_argument(
        "tasks_file",
        nargs="?",
        help="Path to tasks JSON file (default: plans/tasks.json)"
    )
    
    # ralph review
    review_parser = subparsers.add_parser(
        "review",
        help="Review completed tasks"
    )
    review_parser.add_argument(
        "tasks_file",
        help="Path to tasks JSON file (e.g., plans/tasks.json)"
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
    if args.command == "brd":
        return cmd_brd(args)
    elif args.command == "prd":
        return cmd_prd(args)
    elif args.command == "tasks":
        return cmd_tasks(args)
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
