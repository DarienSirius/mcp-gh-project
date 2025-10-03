# mcp-gh-project v0.0.1

**GitHub Project Management MCP Server**

Fills the gap in GitHub's official MCP server by providing project board management tools.

## Installation

```bash
pip install "mcp[cli]" httpx python-dotenv
```

## Usage

### Windows (PowerShell)

Configure in VSCode workspace:

```json
{
  "gh-project-miast0": {
    "command": "powershell.exe",
    "args": ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "C:\\Users\\victorb\\code\\.miast0\\_\\mcp-gh-project\\scripts\\mcp-gh-project-wrapper.ps1"]
  }
}
```

**Note:** PowerShell wrapper loads `GITHUB_PERSONAL_ACCESS_TOKEN` from `.env.github` at runtime.

### Linux/macOS (Future)

Bash wrapper implementation needed. Server can run directly:

```json
{
  "gh-project-miast0": {
    "command": "python",
    "args": ["-m", "src.server"],
    "cwd": "/path/to/mcp-gh-project",
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${localEnv:GITHUB_PERSONAL_ACCESS_TOKEN}"
    }
  }
}
```

### .devcontainer (Future)

Same as Linux/macOS - direct Python module execution with environment variable passthrough.

## Available Tools

### Project Management
- `list_projects` - List all projects for org/user
- `create_project` - Create new project
- `get_project_details` - Get project metadata
- `update_project_settings` - Update project title/description/visibility

### Item Management  
- `add_item_to_project` - Add issue/PR to project
- `remove_item_from_project` - Remove item from project
- `list_project_items` - List all items in project
- `update_item_field_value` - Update custom field values

### Field Management
- `get_project_fields` - List all fields in project

## Security

Token loaded from `.env.github` at runtime via PowerShell wrapper. Never stored in workspace config.

## Architecture

Built with FastMCP (Python) using GitHub GraphQL Projects API directly.

## License

MIT
