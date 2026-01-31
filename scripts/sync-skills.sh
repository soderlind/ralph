#!/bin/bash
# Sync skills from skills/ to .copilot/skills/ and .claude/skills/

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "🔄 Syncing skills to project scope folders..."

# Create directories if they don't exist
mkdir -p .copilot/skills .claude/skills

# Sync each skill
for skill in skills/*/; do
  if [ -d "$skill" ]; then
    skill_name=$(basename "$skill")
    
    # Skip if not a skill folder (check for SKILL.md or skill.md)
    if [ ! -f "$skill/SKILL.md" ] && [ ! -f "$skill/skill.md" ]; then
      echo "⚠️  Skipping $skill_name (no SKILL.md or skill.md found)"
      continue
    fi
    
    echo "  📦 Syncing $skill_name..."
    
    # Copy to .copilot/skills
    rm -rf ".copilot/skills/$skill_name"
    cp -r "$skill" ".copilot/skills/$skill_name"
    
    # Copy to .claude/skills
    rm -rf ".claude/skills/$skill_name"
    cp -r "$skill" ".claude/skills/$skill_name"
    
    echo "  ✅ $skill_name synced"
  fi
done

echo ""
echo "✨ Skills synced successfully!"
echo ""
echo "Available skills:"
echo "  - ralph-brd-to-prd"
echo "  - ralph-prd-to-tasks"
echo "  - ralph-task-review"
echo "  - ralph-cleanup-agent"
echo "  - ralph-tasks-kanban"
echo "  - ralph-run"
echo "  - ralph-review"
echo "  - ralph-cleanup"
echo ""
echo "Use in Copilot CLI: copilot -p '@ralph-brd-to-prd ...'"
echo "Use in Claude: @ralph-brd-to-prd ..."
echo "Use in Ralph: ./ralph.py brd <file>"
