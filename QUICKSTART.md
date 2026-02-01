# Ralph Quickstart Guide

Get Ralph running in 5-10 minutes with this step-by-step guide.

---

## 📋 Prerequisites

Before starting, ensure you have the following installed and configured:

### Required

#### 1. Python 3.8 or Higher
```bash
# Check version
python3 --version  # Should show 3.8 or higher

# If not installed:
# macOS: brew install python3
# Ubuntu: sudo apt install python3
# Windows: Download from python.org
```

#### 2. Git
```bash
# Check if installed
git --version

# If not installed:
# macOS: brew install git
# Ubuntu: sudo apt install git
# Windows: Download from git-scm.com
```

#### 3. Node.js 16+ (includes npm and npx)
```bash
# Check version
node --version  # Should show v16 or higher
npx --version

# If not installed:
# macOS: brew install node
# Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
#         sudo apt-get install -y nodejs
# Windows: Download from nodejs.org
```

#### 4. GitHub Copilot CLI
```bash
# Install globally
npm install -g @githubnext/github-copilot-cli

# Verify installation
copilot --version

# Login (if first time)
copilot auth login
```

**Note:** Requires GitHub Copilot subscription (Individual or Business plan)

#### 5. Vibe-Kanban (Local Setup)
- Run locally: `npx vibe-kanban` or `npm run vibe-kanban`
- Opens at designated URL
- Create a project (you'll need the project name later)
- Note: No cloud account needed - runs entirely locally

---

## 🚀 Installation

### Step 1: Clone Ralph Repository

```bash
# Clone the repository
git clone https://github.com/ans4175/ralph-copilot.git
cd ralph-copilot

# Make ralph.py executable
chmod +x ralph.py

# Test installation
./ralph.py --help
```

**Expected output:**
```
usage: ralph.py [-h] [--execute] [--yolo] {brd,prd,tasks-kanban,run,review,cleanup} ...

Ralph: SDLC Wrapper for Product Development
...
```

### Step 2: Configure Vibe-Kanban MCP Server

Ralph uses Vibe-Kanban MCP for task management. Configure it once:

#### 2.1 Create MCP Configuration Directory

```bash
# For GitHub Copilot CLI
mkdir -p ~/.copilot

# For Claude Desktop (optional, if you use it)
mkdir -p ~/.claude
```

#### 2.2 Create MCP Config File

**Option A: Using the provided template**
```bash
# Copy the template
cp config/mcp-config.json ~/.copilot/mcp-config.json
```

**Option B: Create manually**

Create `~/.copilot/mcp-config.json` with this content:

```json
{
  "mcpServers": {
    "vibe-kanban": {
      "command": "npx",
      "args": ["-y", "vibe-kanban@latest", "--mcp"],
      "env": {}
    }
  }
}
```

**If you already have other MCP servers**, add the `vibe-kanban` entry to your existing `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "vibe-kanban": {
      "command": "npx",
      "args": ["-y", "vibe-kanban@latest", "--mcp"],
      "env": {}
    }
  }
}
```

#### 2.3 Verify MCP Server Connection

```bash
# Test MCP server loads
copilot -v

# Look for:
# ✓ MCP server "vibe-kanban" connected
```

### Step 3: Grant MCP Permissions (CRITICAL!)

**This is a ONE-TIME setup that MUST be done before Ralph can work!**

MCP tools require explicit permission for security. This can ONLY be granted in interactive Copilot mode.

#### 3.1 Start Interactive Copilot

```bash
copilot
```

#### 3.2 Request Permission

In the Copilot chat, type exactly:

```
Use vibe_kanban-list_projects to show all my projects
```

#### 3.3 Approve Permission

You'll see a prompt like:
```
vibe-kanban wants to use vibe_kanban-list_projects. Allow? (y/n)
```

Type: `y` and press Enter

**What happens:**
- Permission is saved permanently in `~/.copilot/permissions.json`
- You should see your Vibe-Kanban projects listed
- This grants permission for ALL vibe_kanban-* tools

#### 3.4 Exit Copilot

```
exit
```

**Troubleshooting:**

| Problem | Solution |
|---------|----------|
| No permission prompt | Check MCP config in Step 2.2 |
| "MCP server not found" | Run `npm install -g vibe-kanban` |
| Permission denied | Manually edit `~/.copilot/permissions.json` |
| No projects listed | Start Vibe-Kanban UI: `npm run vibe-kanban` and create a project |

### Step 4: Configure Ralph for Your Project

Edit `config/ralph.json` in the ralph-copilot directory:

```json
{
  "project_name": "ralph-sdlc-wrapper",
  "version": "0.1.0",
  "vibe_kanban": {
    "project_name": "YOUR-PROJECT-NAME",  // ← CHANGE THIS
    "executor": "COPILOT",                // Coding agent
    "model": "claude-sonnet-4.5"          // Default model
  },
  "repo_config": {
    "base_branch": "main",               // Will be auto-detected
    "setup_script": "",
    "cleanup_script": "",
    "dev_server_script": ""
  },
  "paths": {
    "brd": "plans/brd.md",
    "prd": "plans/generated-prd.md",
    "tasks": "plans/tasks.json",
    "implementation_log": "docs/implementation-log.md",
    "cleanup_log": "docs/cleanup-log.md",
    "archive_dir": "archive/tasks"
  }
}
```

**To find your Vibe-Kanban project name:**

```bash
# Method 1: Using Copilot
copilot -p "Use vibe_kanban-list_projects to show all projects"

# Method 2: Start Vibe-Kanban UI
npm run vibe-kanban
# Opens at http://localhost:3000 - check your projects there
```

Copy the exact project name from Vibe-Kanban into `config/ralph.json`.

### Step 5: Sync Ralph Skills

Ralph uses agentic skills that need to be available to Copilot:

```bash
# Run the sync script
./scripts/sync-skills.sh

# Or using npm
npm run sync-skills
```

**Expected output:**
```
✨ Skills synced successfully!
  - ralph-brd-to-prd
  - ralph-prd-to-tasks
  - ralph-tasks-kanban
  - ralph-run
  - ralph-task-review
  - ralph-cleanup-agent
```

**What this does:**
- Copies `skills/` to `.copilot/skills/` (for Copilot CLI)
- Copies `skills/` to `.claude/skills/` (for Claude Desktop)

**Note:** Re-run this script whenever you update skill files.

---

## ✅ Verify Installation

Let's test that everything works:

### Test 1: Ralph Help

```bash
./ralph.py --help
```

**Expected:** Shows usage information with available commands.

### Test 2: Prompt Generator (Default Mode)

```bash
./ralph.py tasks-kanban plans/example-tasks.json
```

**Expected:** Shows a formatted prompt in a box:
```
╭──────────────────────────────────────────────╮
│ 📋 Copy this prompt into Copilot CLI:       │
╰──────────────────────────────────────────────╯

@ralph-tasks-kanban create tasks from...
```

### Test 3: Interactive Copilot with Skills

```bash
# Start Copilot
copilot

# In the chat, test a skill:
@ralph-brd-to-prd --help
```

**Expected:** Skill description and instructions appear.

### Test 4: MCP Permissions Work

```bash
copilot -p "Use vibe_kanban-list_projects to show all my projects"
```

**Expected:** Your Vibe-Kanban projects are listed (no permission prompt if Step 3 was done).

---

## 🎯 First Success: Create Your First Task

Now let's create a real task in Vibe-Kanban:

### 1. Generate Prompt

```bash
./ralph.py tasks-kanban plans/example-tasks.json
```

### 2. Copy the Output

Copy everything after the box, starting with `@ralph-tasks-kanban...`

### 3. Paste into Copilot

```bash
copilot
# Paste the prompt
# Press Enter
```

### 4. Verify in Vibe-Kanban

Start the Vibe-Kanban UI and check your project:

```bash
npm run vibe-kanban
# Opens at http://localhost:3000
```

You should see your new tasks in the project!

---

## 🚀 What's Next?

Now that Ralph is installed and working, learn how to use it:

- **[USAGE-GUIDE.md](USAGE-GUIDE.md)** - Complete workflow guide (BRD → PRD → Tasks → Run)
- **[TEST-GUIDE.md](TEST-GUIDE.md)** - Validate your setup with full dry-run tests
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Understand how Ralph works internally
- **[docs/RFC.md](docs/RFC.md)** - Learn why Ralph was built this way

---

## 💡 Optional: Set Up Alias

For convenience, add Ralph to your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'alias ralph="python3 /path/to/ralph-copilot/ralph.py"' >> ~/.bashrc
source ~/.bashrc

# Now you can use:
ralph --help
ralph brd plans/my-idea.md
```

---

## 🐛 Troubleshooting

### "MCP server not connected"

**Solution:**
```bash
# Check MCP config exists
cat ~/.copilot/mcp-config.json

# Verify Node.js/npx installed
npx --version

# Test MCP server manually
npx -y vibe-kanban@latest --mcp
```

### "Permission denied" for MCP tools

**Solution:**
- Repeat Step 3 (Grant MCP Permissions)
- Or manually edit `~/.copilot/permissions.json` to add vibe-kanban permissions

### "Project not found" when running ralph.py

**Solution:**
```bash
# Verify project name in config
cat config/ralph.json | grep project_name

# List available projects
copilot -p "Use vibe_kanban-list_projects to show all projects"

# Update config/ralph.json with exact project name
```

### Skills not loading

**Solution:**
```bash
# Re-sync skills
./scripts/sync-skills.sh

# Verify skills directory exists
ls -la .copilot/skills/
```

---

## 📚 Additional Resources

- **GitHub Copilot CLI Docs**: https://docs.github.com/en/copilot/github-copilot-in-the-cli
- **Vibe-Kanban**: Run locally with `npx vibe-kanban` (http://localhost:3000)
- **Ralph Issues**: https://github.com/ans4175/ralph-copilot/issues

---

**🎉 Congratulations!** Ralph is now set up and ready to use. Head to [USAGE-GUIDE.md](USAGE-GUIDE.md) to learn the complete workflow.
