# Phase 1 Decisions - mcp-gh-project v0.0.1

**Date:** 2025-10-02  
**Context:** Autonomous sprint to build GitHub project management MCP server filling gaps in reference implementation

## Decision 1: SDK Choice - FastMCP (Python)

**DECISION:** Use FastMCP (Python) framework for v0.0.1

**Rationale:**
1. **Simplicity:** Decorator-based API (`@mcp.tool()`) with auto-generated tool definitions from Python type hints
2. **Proven Pattern:** Official MCP documentation tutorial uses FastMCP weather server as primary example
3. **Type Safety:** Python type hints automatically generate JSON schemas for tools
4. **Rapid Development:** Less boilerplate than TypeScript SDK
5. **Familiar:** Agent already understands FastMCP from documentation research

**Example Pattern:**
```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("gh-project")

@mcp.tool()
async def list_projects(owner: str, org_type: str = "org") -> str:
    """List all GitHub Projects for an organization or user."""
    # implementation
    return json.dumps(result)
```

**Alternative Considered:** TypeScript SDK - More control but higher complexity for v0.0.1

## Decision 2: API Approach - GitHub GraphQL Projects API

**DECISION:** Use GitHub GraphQL Projects API directly (NOT wrapping gh CLI)

**Rationale:**
1. **Native Integration:** GraphQL is the official API for Projects v2
2. **Rich Feature Set:** Complete access to all project management operations
3. **Type Safety:** GraphQL schemas provide strong typing
4. **Performance:** Direct API calls avoid subprocess overhead
5. **MCP Philosophy:** MCP servers should expose native APIs, not wrap CLIs

**Required Operations (from GitHub docs):**
- **Queries:**
  - `organization(login).projectV2(number)` - Get project by number
  - `organization(login).projectsV2(first)` - List projects
  - `user(login).projectV2(number)` - Get user project
  - `node(id).items(first)` - Get project items
  - `node(id).fields(first)` - Get project fields

- **Mutations:**
  - `createProjectV2(input)` - Create project
  - `updateProjectV2(input)` - Update project settings
  - `addProjectV2ItemById(input)` - Add issue/PR to project
  - `addProjectV2DraftIssue(input)` - Add draft issue
  - `updateProjectV2ItemFieldValue(input)` - Update item field
  - `deleteProjectV2Item(input)` - Remove item from project

**Authentication:** PAT with `project` scope (read:project for read-only)

**Alternative Considered:** Wrap gh CLI commands - Rejected because duplicates existing proven pattern (github-execute-operation.js already does this), MCP should expose native APIs

## Decision 3: Template Strategy - Adapt Official Weather Server

**DECISION:** Use official FastMCP weather server as starting point template

**Rationale:**
1. **Proven Architecture:** Official template is battle-tested pattern
2. **Community Standard:** Following official patterns improves maintainability
3. **Clear Structure:** Weather server demonstrates proper FastMCP usage
4. **Documentation Reference:** Easy to reference official docs during development
5. **Rapid Start:** No need to design architecture from scratch

**Key Adaptations:**
- Replace weather API calls with GitHub GraphQL queries
- Adapt authentication from generic to GitHub PAT
- Modify tool definitions for project management instead of weather data
- Reuse error handling, logging, and stdio transport patterns

**Template Source:** https://modelcontextprotocol.io/docs/develop/build-server (weather server example)

## Implementation Plan Summary

**Architecture:**
```
mcp-gh-project/
├── src/
│   ├── __init__.py
│   ├── server.py           # FastMCP instance + tool definitions
│   ├── graphql_client.py   # GitHub GraphQL query execution
│   └── auth.py             # PAT token loading (from env)
├── scripts/
│   └── mcp-gh-project-wrapper.ps1  # Token injection wrapper
├── README.md
├── requirements.txt
└── package.json           # MCP server metadata
```

**Tool Categories:**
1. **Project Management:** list_projects, create_project, get_project_details, update_project_settings
2. **Item Management:** add_item_to_project, remove_item_from_project, list_project_items
3. **Field Management:** update_item_field_value, get_project_fields

**Security Model:** Reuse proven PowerShell wrapper pattern from github-miast0 MCP server

## Next Steps

1. Create project directory structure
2. Initialize Python virtual environment
3. Install FastMCP dependencies (`pip install "mcp[cli]"`)
4. Create basic FastMCP server with test tool
5. Test stdio protocol with simple echo command
6. Implement GraphQL client with authentication
7. Develop core project management tools
8. Create PowerShell wrapper script
9. Update workspace config
10. Test with VSCode MCP client

**Expected Completion:** 2-3 hours for v0.0.1 implementation

---
**Decision Log Complete** - Ready to proceed to Phase 2: Project Structure Creation
