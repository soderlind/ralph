# Contributing to Ralph

Thank you for your interest in contributing to Ralph! This document provides guidelines for contributing to the project.

---

## 🤝 How to Contribute

### Reporting Bugs

Found a bug? Help us fix it:

1. **Check existing issues** - Search [Issues](https://github.com/ans4175/ralph-copilot/issues) to avoid duplicates
2. **Create detailed report** - Include:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Ralph version (`./ralph.py --version`)
   - Environment (OS, Python version, Copilot CLI version)
   - Relevant logs or screenshots
3. **Use bug template** - Follow the issue template if available

**Example Bug Report:**
```
Title: ralph run fails with "Project not found" despite valid config

Description:
Running `ralph run` fails even though config/ralph.json has correct project name.

Steps to Reproduce:
1. Set project_name in config/ralph.json
2. Run `./ralph.py run`
3. Error appears

Expected: Tasks start executing
Actual: "Project 'my-project' not found"

Environment:
- Ralph version: 0.1.0
- OS: macOS 14.2
- Python: 3.11.5
- Copilot CLI: 1.2.0

Additional Context:
Project exists in Vibe-Kanban (check with `npm run vibe-kanban` at http://localhost:3000)
```

### Suggesting Features

Have an idea? We'd love to hear it:

1. **Check existing feature requests** - Review [Issues](https://github.com/ans4175/ralph-copilot/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
2. **Open feature request** - Include:
   - Clear use case
   - Why it matters
   - Proposed solution (if any)
   - Alternative approaches considered
3. **Discuss first for major changes** - Open an issue before spending time on implementation

**Example Feature Request:**
```
Title: Add support for GitHub Projects as alternative to Vibe-Kanban

Use Case:
Some teams use GitHub Projects instead of Vibe-Kanban. Would be great 
to support both.

Why It Matters:
- Reduces friction for GitHub-first teams
- Expands Ralph's reach
- Leverages existing tools

Proposed Solution:
Add adapter pattern for task management systems. Default to Vibe-Kanban, 
allow configuration for GitHub Projects.

Alternatives:
- Create separate fork for GitHub Projects
- Use webhook bridge between systems
```

---

## 🔧 Development Setup

### Prerequisites

- Python 3.8+
- Git
- Node.js 16+ (for Vibe-Kanban MCP)
- GitHub Copilot CLI
- GitHub Copilot subscription

### Clone and Setup

```bash
# Fork the repository on GitHub first

# Clone your fork
git clone https://github.com/YOUR-USERNAME/ralph-copilot.git
cd ralph-copilot

# Add upstream remote
git remote add upstream https://github.com/ans4175/ralph-copilot.git

# Make ralph.py executable
chmod +x ralph.py

# Test installation
./ralph.py --help
```

### Configure Development Environment

```bash
# Copy example config
cp config/ralph.json.example config/ralph.json

# Edit with your Vibe-Kanban project name
vim config/ralph.json

# Sync skills
./scripts/sync-skills.sh
```

---

## 📝 Making Changes

### Branch Naming Convention

- `feature/` - New features (`feature/github-projects-support`)
- `fix/` - Bug fixes (`fix/project-not-found-error`)
- `docs/` - Documentation updates (`docs/improve-quickstart`)
- `refactor/` - Code refactoring (`refactor/simplify-mcp-calls`)

### Workflow

```bash
# Create feature branch from main
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Test your changes (see Testing section)
./ralph.py --help
./scripts/sync-skills.sh

# Commit with clear message
git add .
git commit -m "feat: add support for GitHub Projects

- Add GitHub adapter
- Update configuration schema
- Add tests for GitHub integration"

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Format

Follow conventional commits:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat: add GitHub Projects adapter

fix: resolve project name resolution bug

docs: update QUICKSTART with troubleshooting

refactor: simplify MCP permission handling

test: add integration tests for ralph run
```

---

## 🧪 Testing

### Manual Testing

```bash
# Test basic functionality
./ralph.py --help
./ralph.py brd plans/example-brd.md
./ralph.py prd plans/generated-prd.md

# Test with Vibe-Kanban (prompt mode)
./ralph.py tasks-kanban plans/tasks.json
# Copy prompt and test in copilot

# Test execute mode (if permissions granted)
./ralph.py --execute tasks-kanban plans/tasks.json
```

### Test Checklist

Before submitting PR, verify:

- [ ] `./ralph.py --help` works
- [ ] All 6 commands work in prompt mode
- [ ] Skills sync correctly (`./scripts/sync-skills.sh`)
- [ ] Documentation is updated
- [ ] No broken links in markdown files
- [ ] Examples in docs work correctly
- [ ] Commit messages follow convention

### Testing New Skills

```bash
# Add skill to skills/ directory
mkdir skills/my-new-skill
vim skills/my-new-skill/SKILL.md

# Sync to project scope
./scripts/sync-skills.sh

# Test skill loads
copilot
> @my-new-skill --help
```

---

## 📚 Documentation

### What to Document

- New features (update USAGE-GUIDE.md)
- Configuration changes (update config examples)
- New skills (add SKILL.md in skills/ directory)
- Breaking changes (add migration guide)
- Design decisions (update docs/RFC.md if philosophical, docs/ARCHITECTURE.md if technical)

### Documentation Structure

```
ralph-copilot/
├── README.md              ← Brief intro, link to other docs
├── QUICKSTART.md          ← Installation and first success
├── USAGE-GUIDE.md         ← Complete usage reference
├── TEST-GUIDE.md          ← Validation testing
├── CONTRIBUTING.md        ← This file
├── docs/
│   ├── RFC.md             ← Design philosophy
│   └── ARCHITECTURE.md    ← Technical architecture
└── skills/
    └── skill-name/
        └── SKILL.md       ← Skill instructions
```

### Writing Style

- Use clear, simple language
- Provide examples for complex concepts
- Include code snippets with expected output
- Add troubleshooting sections where appropriate
- Use consistent terminology

---

## 🔍 Code Review

### What We Look For

- **Clarity**: Code is easy to understand
- **Consistency**: Follows existing patterns
- **Documentation**: Changes are documented
- **Testing**: Changes are tested
- **No breaking changes**: Or includes migration guide

### Review Process

1. Automated checks run (if configured)
2. Maintainer reviews code
3. Feedback provided
4. Iterate until approved
5. Merge to main

---

## 📤 Pull Request Process

### Before Submitting

1. **Update documentation** - README, USAGE-GUIDE, or relevant docs
2. **Test thoroughly** - Manual testing minimum
3. **Sync with upstream** - Rebase on latest main
4. **Clear commit history** - Squash if needed
5. **Fill PR template** - Provide context

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing Done
- [ ] Tested manually
- [ ] Added tests (if applicable)
- [ ] Documentation updated

## Related Issues
Fixes #123, Relates to #456

## Screenshots (if applicable)
Add screenshots for UI changes
```

### After Submitting

- Respond to feedback promptly
- Make requested changes
- Re-request review after updates
- Be patient and respectful

---

## 🎨 Coding Standards

### Python

- Follow PEP 8 style guide
- Use descriptive variable names
- Add docstrings to functions
- Keep functions focused and small
- Use type hints where appropriate

**Example:**
```python
def resolve_project_id(project_name: str) -> str:
    """
    Resolve project name to Vibe-Kanban project ID.
    
    Args:
        project_name: Human-readable project name
        
    Returns:
        UUID of the project
        
    Raises:
        ValueError: If project not found
    """
    # Implementation
    pass
```

### Markdown Skills

- Clear section headers
- Numbered steps for procedures
- Code examples with context
- Safety notes where appropriate

**Example:**
```markdown
## Step 1: Resolve Project Name

1. Use `vibe_kanban-list_projects` MCP tool
2. Find project where name matches
3. Extract project UUID
4. If not found: report error

**Safety Note:** Always verify project exists before operations.
```

---

## 🐛 Debugging

### Common Issues

**"MCP server not connected"**
```bash
# Check MCP config
cat ~/.copilot/mcp-config.json

# Restart Copilot
copilot -v
```

**"Permission denied"**
```bash
# Check permissions file
cat ~/.copilot/permissions.json

# Re-grant permissions
copilot
> Use vibe_kanban-list_projects to show all projects
> y
```

**"Skills not loading"**
```bash
# Re-sync skills
./scripts/sync-skills.sh

# Verify
ls .copilot/skills/
```

### Getting Help

- Open an issue with "question" label
- Join discussions in Issues tab
- Review existing documentation
- Check FAQ in USAGE-GUIDE.md

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## 🙏 Recognition

Contributors will be recognized in:
- CHANGELOG.md for their contributions
- GitHub contributors page
- Project README (for significant contributions)

---

## Questions?

- Open an issue with "question" label
- Review [USAGE-GUIDE.md](USAGE-GUIDE.md) for usage questions
- Check [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details
- Read [docs/RFC.md](docs/RFC.md) for design philosophy

**Thank you for contributing to Ralph!** 🎉
