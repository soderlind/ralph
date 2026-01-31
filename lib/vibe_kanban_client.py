"""
Vibe-Kanban Prompt Generator

This module generates prompts for the coding agent to interact with vibe-kanban via MCP.
Instead of making direct MCP calls, it prepares instructions that the agent executes.
"""

from __future__ import annotations
import subprocess
import json
from typing import Any, Dict, List, Optional
from pathlib import Path


class VibeKanbanClient:
    """
    Prompt generator for vibe-kanban MCP interactions.
    
    Instead of making direct MCP calls, this generates prompts that
    the coding agent (via Copilot CLI) will execute using available MCP tools.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the vibe-kanban client.
        
        Args:
            config_path: Path to ralph.json config file
        """
        self.config_path = config_path or Path("config/ralph.json")
        self.config = self._load_config()
        self.project_id = self.config.get("vibe_kanban", {}).get("project_id")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from ralph.json."""
        if not self.config_path.exists():
            return {}
        return json.loads(self.config_path.read_text(encoding="utf-8"))
    
    def _save_config(self) -> None:
        """Save configuration back to ralph.json."""
        self.config_path.write_text(
            json.dumps(self.config, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )
    
    def check_installation(self) -> bool:
        """
        Check if vibe-kanban is installed and accessible.
        
        Returns:
            True if vibe-kanban is installed, False otherwise
        """
        check_cmd = self.config.get("mcp", {}).get("check_command", "npx vibe-kanban --version")
        try:
            result = subprocess.run(
                check_cmd.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def ensure_installed(self) -> None:
        """
        Ensure vibe-kanban is installed. Run npx vibe-kanban if not found.
        
        Raises:
            RuntimeError: If vibe-kanban cannot be installed or accessed
        """
        if self.check_installation():
            return
        
        print("📦 Installing vibe-kanban...")
        try:
            subprocess.run(
                ["npx", "-y", "vibe-kanban@latest", "--version"],
                capture_output=True,
                text=True,
                timeout=120,
                check=True
            )
            print("✅ vibe-kanban installed successfully")
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            raise RuntimeError(f"Failed to install vibe-kanban: {e}")
    
    def generate_list_projects_prompt(self) -> str:
        """
        Generate a prompt for the coding agent to list vibe-kanban projects.
        
        Returns:
            Prompt string that the agent will execute
        """
        return """Use the vibe_kanban-list_projects MCP tool to list all available projects.

Return the projects in this format:
```json
[
  {"id": "project-uuid-1", "name": "Project Name 1"},
  {"id": "project-uuid-2", "name": "Project Name 2"}
]
```"""
    
    def get_project_id(self) -> str:
        """
        Get the project ID, prompting user to select if not configured.
        
        Returns:
            Project ID string
            
        Raises:
            ValueError: If no projects are available or user cancels selection
        """
        if self.project_id:
            return self.project_id
        
        # List projects
        projects = self.list_projects()
        if not projects:
            raise ValueError(
                "No vibe-kanban projects found. "
                "Please create a project first or check MCP connection."
            )
        
        # Prompt user to select
        print("\n📋 Available Vibe-Kanban Projects:")
        for idx, project in enumerate(projects, 1):
            print(f"  {idx}. {project.get('name')} (ID: {project.get('id')})")
        
        while True:
            try:
                choice = input("\nSelect project number: ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(projects):
                    selected = projects[idx]
                    self.project_id = selected["id"]
                    
                    # Save to config
                    self.config.setdefault("vibe_kanban", {})["project_id"] = self.project_id
                    self._save_config()
                    
                    print(f"✅ Selected project: {selected['name']}")
                    return self.project_id
                else:
                    print("❌ Invalid selection. Try again.")
            except (ValueError, KeyError):
                print("❌ Invalid input. Enter a number.")
    
    def generate_create_task_prompt(
        self,
        title: str,
        description: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> str:
        """
        Generate a prompt for the coding agent to create a task in vibe-kanban.
        
        Args:
            title: Task title
            description: Optional task description
            project_id: Optional project ID (uses config default if not provided)
            
        Returns:
            Prompt string that the agent will execute
        """
        pid = project_id or self.project_id or "{PROJECT_ID_PLACEHOLDER}"
        desc = description or ""
        
        return f"""Use the vibe_kanban-create_task MCP tool to create a new task.

Parameters:
- project_id: {pid}
- title: {title}
- description: {desc}

Return the task ID from the response."""
    
    def generate_get_task_prompt(self, task_id: str) -> str:
        """Generate prompt to get task details."""
        return f"""Use the vibe_kanban-get_task MCP tool to get details for task ID: {task_id}

Return the task status, title, and description."""
    
    def generate_list_tasks_prompt(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> str:
        """Generate prompt to list tasks in a project."""
        pid = project_id or self.project_id or "{PROJECT_ID_PLACEHOLDER}"
        status_filter = f"status={status}" if status else "all statuses"
        
        return f"""Use the vibe_kanban-list_tasks MCP tool to list tasks.

Parameters:
- project_id: {pid}
- status: {status_filter}
- limit: {limit}

Return the list of tasks with their IDs, titles, and statuses."""
    
    def generate_update_task_prompt(self, task_id: str, status: str) -> str:
        """Generate prompt to update task status."""
        return f"""Use the vibe_kanban-update_task MCP tool to update the task.

Parameters:
- task_id: {task_id}
- status: {status}

Confirm the update was successful."""
    
    def generate_delete_task_prompt(self, task_id: str) -> str:
        """Generate prompt to delete a task."""
        return f"""Use the vibe_kanban-delete_task MCP tool to delete task ID: {task_id}

Confirm the task was deleted."""
    
    def generate_start_workspace_prompt(
        self,
        task_id: str,
        repos: List[Dict[str, str]],
        executor: Optional[str] = None,
        variant: Optional[str] = None
    ) -> str:
        """Generate prompt to start a workspace session."""
        executor = executor or self.config.get("vibe_kanban", {}).get("executor", "CLAUDE_CODE")
        variant_str = f", variant={variant}" if variant else ""
        
        repos_json = json.dumps(repos, indent=2)
        
        return f"""Use the vibe_kanban-start_workspace_session MCP tool to start a coding agent workspace.

Parameters:
- task_id: {task_id}
- executor: {executor}{variant_str}
- repos: {repos_json}

This will start the coding agent to work on the task. Return the workspace session ID."""
