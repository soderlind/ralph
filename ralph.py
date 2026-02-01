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


def detect_git_branch() -> Optional[str]:
    """Detect current git branch from repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path.cwd()
        )
        branch = result.stdout.strip()
        return branch if branch else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def print_prompt(skill_name: str, prompt_text: str, context: Optional[Dict[str, Any]] = None):
    """
    Display a formatted, copy-paste ready prompt for Copilot CLI.
    
    Args:
        skill_name: Name of the skill (e.g., 'ralph-tasks-kanban')
        prompt_text: The prompt to execute
        context: Optional dict of context info to display
    """
    log("")
    log("╭" + "─" * 70 + "╮")
    log("│ 📋 Copy this prompt into Copilot CLI:" + " " * 32 + "│")
    log("╰" + "─" * 70 + "╯")
    log("")
    
    # Format prompt nicely (replace multiple spaces/newlines with single space)
    formatted_prompt = " ".join(prompt_text.split())
    log(f"@{skill_name} {formatted_prompt}")
    
    log("")
    log("╭" + "─" * 70 + "╮")
    log("│ 💡 How to use:" + " " * 55 + "│")
    log("│   1. Run: copilot" + " " * 51 + "│")
    log("│   2. Paste the prompt above" + " " * 41 + "│")
    log("│   3. Approve permissions if asked" + " " * 35 + "│")
    log("╰" + "─" * 70 + "╯")
    
    if context:
        log("")
        log("📊 Context:")
        for key, value in context.items():
            log(f"  • {key}: {value}")
    
    log("")
    log("💡 Tip: Use --execute flag to run immediately (requires MCP permissions)")
    log("")


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
        skill_name: Name of skill folder (e.g., 'ralph-brd-to-prd')
        
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
    yolo: bool = False,
    **kwargs
) -> str:
    """
    Invoke GitHub Copilot CLI with skill reference.
    
    Coding agent will load skill from .copilot/skills/ or .claude/skills/.
    Output streams in real-time to terminal.
    
    Args:
        skill_name: Name of skill to use (e.g., 'ralph-brd-to-prd')
        task_prompt: The task/context for the skill to process
        model: Optional model override
        yolo: Enable non-interactive mode (auto-approve all permissions)
        
    Returns:
        Empty string (output streams directly to terminal)
    """
    config = load_config()
    
    # Get model from args or config
    if model is None:
        model = config.get("skills", {}).get("default_model", "claude-haiku-4.5")
    
    # Build prompt with skill reference (coding agent loads it)
    full_prompt = f"@{skill_name} {task_prompt}"
    
    cmd = [
        "copilot",
        "--model", model,
        "--no-color"
    ]
    
    # Add --yolo flag if non-interactive mode
    if yolo:
        cmd.append("--yolo")
    
    cmd.extend(["-p", full_prompt])
    
    log(f"🤖 Invoking Copilot with @{skill_name} (model: {model})...")
    log("━" * 60)
    
    try:
        # Run without capturing output - streams in real-time
        result = subprocess.run(
            cmd,
            timeout=300,  # 5 minutes
            check=True
        )
        log("━" * 60)
        return ""  # Output already displayed in terminal
    except subprocess.TimeoutExpired:
        log("\n⏱️  Copilot timed out (5 minutes)")
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
    
    Reads BRD markdown file, invokes ralph-brd-to-prd skill, saves PRD markdown.
    """
    brd_path = Path(args.brd_file)
    
    if not brd_path.exists():
        log(f"❌ BRD file not found: {brd_path}")
        return 1
    
    # Verify skill exists in project scope
    skill_name = "ralph-brd-to-prd"
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
    
    # Invoke Copilot (it loads @ralph-brd-to-prd from project scope)
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
    
    Reads PRD markdown file, invokes ralph-prd-to-tasks skill, saves tasks.json.
    """
    prd_path = Path(args.prd_file)
    
    if not prd_path.exists():
        log(f"❌ PRD file not found: {prd_path}")
        return 1
    
    # Verify skill exists in project scope
    skill_name = "ralph-prd-to-tasks"
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
    
    # Invoke Copilot (it loads @ralph-prd-to-tasks from project scope)
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
    log("  3. Create tasks in Vibe Kanban: ralph tasks-kanban")
    
    return 0


def cmd_tasks_kanban(args: argparse.Namespace) -> int:
    """
    Handle 'ralph tasks-kanban' command.
    
    Default: Shows copy-paste prompt for Copilot CLI
    With --execute: Creates tasks in Vibe Kanban immediately
    """
    config = load_config()
    tasks_path = Path(args.tasks_file or config["paths"]["tasks"])
    project_name = config.get("vibe_kanban", {}).get("project_name")
    
    if not project_name:
        log("❌ No project_name configured in config/ralph.json")
        log("💡 Set vibe_kanban.project_name in config/ralph.json")
        return 1
    
    # Verify skill exists
    skill_name = "ralph-tasks-kanban"
    if not verify_skill_exists(skill_name):
        return 1
    
    yolo_mode = getattr(args, 'yolo', False)
    execute_mode = getattr(args, 'execute', False)
    
    prompt = f"""Create tasks from {tasks_path} into vibe-kanban project "{project_name}".

Use @{skill_name} skill to:
1. Use vibe_kanban-list_projects MCP to find project ID for "{project_name}"
2. Read and validate tasks JSON file
3. Create each task in vibe-kanban with proper dependencies
4. Report summary of results

Tasks file: {tasks_path}
Project name: {project_name}
{'Non-interactive mode: Skip all confirmation prompts, auto-proceed with all operations.' if yolo_mode else ''}"""
    
    skill_config = config.get("skills", {}).get("tasks_kanban", {})
    model = skill_config.get("model", "claude-haiku-4.5")
    
    if execute_mode:
        # Execute immediately
        mode_label = "🚀 YOLO MODE" if yolo_mode else "🤖"
        log(f"{mode_label} Using @{skill_name} to create tasks from {tasks_path}")
        
        response = invoke_copilot(skill_name, prompt, model=model, yolo=yolo_mode)
        
        log("✅ Task creation complete")
        log(f"💡 View tasks in Vibe-Kanban UI: npm run vibe-kanban")
    else:
        # Show copy-paste prompt
        context = {
            "Command": "tasks-kanban",
            "Tasks file": str(tasks_path),
            "Project": project_name,
            "Skill": skill_name,
            "Model": model
        }
        print_prompt(skill_name, prompt, context)
    
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """
    Handle 'ralph run' command.
    
    Default: Shows copy-paste prompt for Copilot CLI
    With --execute: Starts ready tasks immediately
    """
    config = load_config()
    
    # Get project_name from args or config
    project_name = args.project_name if hasattr(args, 'project_name') and args.project_name else None
    if not project_name:
        project_name = config.get("vibe_kanban", {}).get("project_name")
    
    if not project_name:
        log("❌ No project_name configured")
        log("💡 Set vibe_kanban.project_name in config/ralph.json or use --project-name")
        return 1
    
    # Verify skill exists
    skill_name = "ralph-run"
    if not verify_skill_exists(skill_name):
        return 1
    
    yolo_mode = getattr(args, 'yolo', False)
    execute_mode = getattr(args, 'execute', False)
    
    # Get executor and repo config
    executor = config.get("vibe_kanban", {}).get("executor", "CLAUDE_CODE")
    variant = config.get("vibe_kanban", {}).get("variant")
    repo_config = config.get("vibe_kanban", {}).get("repo_config", {})
    
    # Detect current git branch (override config)
    detected_branch = detect_git_branch()
    if detected_branch:
        repo_config = repo_config.copy()  # Don't modify original
        repo_config["base_branch"] = detected_branch
    
    prompt = f"""Execute ready tasks from vibe-kanban project "{project_name}".

Use @{skill_name} skill to:
1. Use vibe_kanban-list_projects MCP to find project ID for "{project_name}"
2. Detect git repository context (URL, branch)
3. List tasks with status='todo' and no blocking dependencies
4. Start workspace session for each ready task
5. Report summary of started tasks

Project name: {project_name}
Executor: {executor}
{f"Variant: {variant}" if variant else ""}
Repository config: {json.dumps(repo_config, indent=2)}

Limit to first 3 tasks if many are ready (max_parallel_tasks).
{'Non-interactive mode: Skip all confirmation prompts, auto-start all ready tasks.' if yolo_mode else ''}"""
    
    skill_config = config.get("skills", {}).get("run", {})
    model = skill_config.get("model", "claude-haiku-4.5")
    
    if execute_mode:
        # Execute immediately
        mode_label = "🚀 YOLO MODE" if yolo_mode else "🚀"
        log(f"{mode_label} Starting ready tasks from project: {project_name}")
        log(f"🤖 Using @{skill_name} skill")
        
        response = invoke_copilot(skill_name, prompt, model=model, yolo=yolo_mode)
        
        log("\n✅ Run complete")
        log("💡 View workspace sessions in Vibe-Kanban UI: npm run vibe-kanban")
    else:
        # Show copy-paste prompt
        context = {
            "Command": "run",
            "Project": project_name,
            "Executor": executor,
            "Skill": skill_name,
            "Model": model
        }
        print_prompt(skill_name, prompt, context)
    
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    """
    Handle 'ralph review' command.
    
    Reviews completed tasks via @ralph-task-review skill.
    Auto-runs cleanup unless --no-cleanup flag is set.
    """
    config = load_config()
    
def cmd_review(args: argparse.Namespace) -> int:
    """
    Handle 'ralph review' command.
    
    Default: Shows copy-paste prompt for Copilot CLI
    With --execute: Reviews completed tasks immediately
    Auto-runs cleanup unless --no-cleanup flag is set.
    """
    config = load_config()
    
    # Get project_name from config
    project_name = config.get("vibe_kanban", {}).get("project_name")
    if not project_name:
        log("❌ No project_name configured")
        log("💡 Set vibe_kanban.project_name in config/ralph.json")
        return 1
    
    # Verify skill exists
    skill_name = "ralph-task-review"
    if not verify_skill_exists(skill_name):
        return 1
    
    yolo_mode = getattr(args, 'yolo', False)
    execute_mode = getattr(args, 'execute', False)
    no_cleanup = getattr(args, 'no_cleanup', False)
    
    prompt = f"""Review completed tasks from vibe-kanban project "{project_name}".

Use @{skill_name} skill to:
1. Use vibe_kanban-list_projects MCP to find project ID for "{project_name}"
2. List all tasks with status='done' from project
3. Filter tasks with valid Ralph IDs (TASK-XXX pattern)
4. Generate implementation summary for each task
5. Append summaries to docs/implementation-log.md
6. Report results
{'7. Trigger @ralph-cleanup-agent to archive reviewed tasks (auto-cleanup enabled)' if not no_cleanup else ''}

Project name: {project_name}
Implementation log: docs/implementation-log.md
Auto-cleanup: {'Yes' if not no_cleanup else 'No'}

Generate reviews with format:
- Task ID and title
- Implementation summary (150-300 words)
- Key technical decisions
- Tests/documentation updates
- Challenges overcome

{'Non-interactive mode: Skip all confirmation prompts, auto-proceed with review.' if yolo_mode else ''}"""
    
    skill_config = config.get("skills", {}).get("task_review", {})
    model = skill_config.get("model", "claude-haiku-4.5")
    
    if execute_mode:
        # Execute immediately
        mode_label = "🚀 YOLO MODE" if yolo_mode else "📋"
        log(f"{mode_label} Reviewing completed tasks from project: {project_name}")
        log(f"🤖 Using @{skill_name} skill")
        
        response = invoke_copilot(skill_name, prompt, model=model, yolo=yolo_mode)
        
        log("\n✅ Review complete")
        
        # Auto-run cleanup unless --no-cleanup
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
    else:
        # Show copy-paste prompt
        context = {
            "Command": "review",
            "Project": project_name,
            "Skill": skill_name,
            "Model": model,
            "Auto-cleanup": "No" if no_cleanup else "Yes"
        }
        print_prompt(skill_name, prompt, context)
    
    return 0



def cmd_cleanup(args: argparse.Namespace) -> int:
    """
    Handle 'ralph cleanup' command.
    
    Default: Shows copy-paste prompt for Copilot CLI
    With --execute: Archives reviewed tasks immediately
    Only processes tasks that exist in implementation-log.md AND are in done status.
    """
    config = load_config()
    
    # Get project_name from config
    project_name = config.get("vibe_kanban", {}).get("project_name")
    if not project_name:
        log("❌ No project_name configured")
        log("💡 Set vibe_kanban.project_name in config/ralph.json")
        return 1
    
    # Verify skill exists
    skill_name = "ralph-cleanup-agent"
    if not verify_skill_exists(skill_name):
        return 1
    
    yolo_mode = getattr(args, 'yolo', False)
    execute_mode = getattr(args, 'execute', False)
    
    # Get paths from config
    log_path = Path(config.get("paths", {}).get("implementation_log", "docs/implementation-log.md"))
    archive_dir = Path(config.get("paths", {}).get("archive_dir", "plans/done"))
    
    prompt = f"""Archive reviewed tasks from vibe-kanban project "{project_name}".

Use @{skill_name} skill to:
1. Use vibe_kanban-list_projects MCP to find project ID for "{project_name}"
2. Read docs/implementation-log.md to get reviewed task IDs
3. List tasks with status='done' from vibe-kanban
4. Cross-reference: only archive tasks that are BOTH done AND reviewed
5. For each matching task:
   - Archive task data to {archive_dir}/
6. Delete git worktrees and vk/* branches using: scripts/cleanup-worktrees.sh -f
7. Delete reviewed tasks from vibe-kanban (only those in implementation-log.md)
8. Append cleanup summary to docs/cleanup-log.md

Project name: {project_name}
Implementation log: {log_path}
Archive directory: {archive_dir}/
Cleanup log: docs/cleanup-log.md

Safety: Only archive/delete tasks that appear in implementation-log.md AND have 'done' status
{'Non-interactive mode: Skip all confirmation prompts, auto-proceed with cleanup and archival.' if yolo_mode else ''}"""
    
    skill_config = config.get("skills", {}).get("cleanup_agent", {})
    model = skill_config.get("model", "claude-haiku-4.5")
    
    if execute_mode:
        # Execute immediately
        mode_label = "🚀 YOLO MODE" if yolo_mode else "🧹"
        log(f"{mode_label} Cleaning up reviewed tasks from project: {project_name}")
        log(f"🤖 Using @{skill_name} skill")
        
        response = invoke_copilot(skill_name, prompt, model=model, yolo=yolo_mode)
        
        log("\n✅ Cleanup complete!")
    else:
        # Show copy-paste prompt
        context = {
            "Command": "cleanup",
            "Project": project_name,
            "Skill": skill_name,
            "Model": model,
            "Archive": str(archive_dir)
        }
        print_prompt(skill_name, prompt, context)
    
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ralph SDLC Wrapper - Full workflow orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show copy-paste prompts (default - solves permission issues!)
  ralph tasks-kanban plans/tasks.json       # Shows prompt for Copilot
  ralph run                                 # Shows prompt for running tasks
  ralph review                              # Shows prompt for review
  
  # Execute immediately (requires MCP permissions already granted)
  ralph --execute tasks-kanban plans/tasks.json
  ralph --execute run
  ralph --execute --yolo review             # Non-interactive + execute

  # Document generation (no MCP needed)
  ralph brd-prd plans/brd.md                # Generate PRD from BRD
  ralph prd-tasks plans/prd.md              # Generate tasks from PRD

Full workflow:
  1. ralph brd-prd plans/brd.md → generates plans/generated-prd.md
  2. ralph prd-tasks plans/generated-prd.md → generates plans/tasks.json
  3. ralph tasks-kanban plans/tasks.json → shows prompt to copy
  4. (paste into: copilot, approve permissions)
  5. ralph run → shows prompt to run ready tasks
  6. (work on tasks in Vibe Kanban workspaces)
  7. ralph review → shows prompt to review completed tasks
  8. ralph cleanup → shows prompt to archive

Prompt mode (default):
  Shows formatted prompts to copy-paste into Copilot CLI.
  Solves MCP permission issues by running in interactive mode.

Execute mode (--execute):
  Runs commands immediately. Requires MCP permissions already granted.
  Use for automation/CI/CD after initial setup.
        """
    )
    
    # Global flags
    parser.add_argument(
        "--yolo",
        action="store_true",
        help="Non-interactive mode: skip all confirmation prompts (auto-confirm everything)"
    )
    
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute immediately (requires MCP permissions). Default: show copy-paste prompt"
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
        "--project-name",
        help="Optional project name (uses config if not provided)"
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
