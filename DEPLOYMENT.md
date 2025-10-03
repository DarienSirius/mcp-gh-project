# Deployment Guide - mcp-gh-project v0.0.1

## Prerequisites

1. **Python 3.8+** installed and in PATH
2. **GitHub Personal Access Token** with `project` scope
3. **VSCode** with GitHub Copilot Chat extension

## Installation Steps

### 1. Install Python Dependencies

```bash
cd /c/Users/victorb/code/.miast0/_/mcp-gh-project
pip install -r requirements.txt
```

Dependencies:
- `mcp[cli]` - FastMCP framework
- `httpx` - Async HTTP client for GraphQL
- `python-dotenv` - Environment variable loading

### 2. Verify .env.github Token

Ensure `.miast0/.env.github` contains your GitHub PAT:

```env
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
GITHUB_PERSONAL_USER_NAME=your_username
```

**Required Scopes:** `project` (or `read:project` for read-only)

### 3. Update VSCode Workspace Configuration

Add to `michael-as-stephen.code-workspace`:

```json
{
  "mcpServers": {
    "gh-project-miast0": {
      "command": "powershell.exe",
      "args": [
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File",
        "C:\\Users\\victorb\\code\\.miast0\\_\\mcp-gh-project\\scripts\\mcp-gh-project-wrapper.ps1"
      ]
    }
  }
}
```

### 4. Restart MCP Servers in VSCode

1. Open Command Palette (Ctrl+Shift+P)
2. Run: "MCP: Restart MCP Servers"
3. Check output for "Starting mcp-gh-project MCP server..."

## Verification

### Test 1: List GitHub Projects

In GitHub Copilot Chat, try:

```
@workspace List all projects for wordgarden-dev organization
```

Expected: JSON response with project list

### Test 2: Get Project Details

```
@workspace Get details for project #1 in wordgarden-dev
```

Expected: Project metadata with fields

### Test 3: Create Test Project (if desired)

```
@workspace Get owner ID for wordgarden-dev organization
```

Then:

```
@workspace Create project with owner_id <node-id> and title "MCP Test Project"
```

## Troubleshooting

### Server Not Starting

**Check PowerShell wrapper output:**
```powershell
C:\Users\victorb\code\.miast0\_\mcp-gh-project\scripts\mcp-gh-project-wrapper.ps1
```

**Common issues:**
- `.env.github` not found - Check path in wrapper script
- `GITHUB_PERSONAL_ACCESS_TOKEN` missing - Verify .env.github format
- Python not in PATH - Install Python or add to PATH
- `server.py` not found - Check file structure

### Authentication Errors

**GraphQL query failed: Unauthorized**

- Verify PAT has `project` scope
- Check token is not expired
- Ensure PAT loaded: `echo $env:GITHUB_PERSONAL_ACCESS_TOKEN` in PowerShell

### Import Errors

**ModuleNotFoundError: No module named 'mcp'**

```bash
pip install "mcp[cli]"
```

**ModuleNotFoundError: No module named 'httpx'**

```bash
pip install httpx python-dotenv
```

### Relative Import Errors

**ImportError: attempted relative import with no known parent package**

- Run server via wrapper script, not directly
- Wrapper uses absolute path to server.py

## Security Notes

✅ **Token never in workspace config** - Loaded at runtime  
✅ **Token in environment only** - Not passed as command arg  
✅ **Logging to stderr** - Stdout reserved for JSON-RPC  
✅ **Reuses proven pattern** - Same architecture as github-miast0 MCP server

## Tool Reference

All tools return JSON strings. Use in Chat with natural language:

**Project Management:**
- List projects for an organization
- Get details for project #N
- Create new project
- Update project settings

**Item Management:**
- Add issue #N to project
- Remove item from project
- List all items in project
- Update custom field values

**Utility:**
- Get owner ID for creating projects
- Get all fields in project

---
**Last Updated:** 2025-10-03 - v0.0.1 Release
