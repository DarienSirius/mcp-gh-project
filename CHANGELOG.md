# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-10-03

### Added
- Initial release of GitHub Project Management MCP Server
- 10 tools for managing GitHub Projects via GraphQL API
- FastMCP Python implementation
- PowerShell wrapper for Windows with secure token loading
- Platform-specific configuration documentation
- File-based telemetry for deployment debugging

### Tools Implemented
- `list_projects` - List all projects for organization or user
- `create_project` - Create new GitHub Project
- `get_project_details` - Get project metadata and configuration
- `update_project_settings` - Update project title, description, visibility
- `add_item_to_project` - Add issue or PR to project board
- `remove_item_from_project` - Remove item from project
- `list_project_items` - List all items in project
- `update_item_field_value` - Update custom field values
- `get_project_fields` - List all fields in project
- `get_owner_id` - Get node ID for organization or user

### Tested
- Successfully dogfooded: Created Issue #5 epic breakdown (5 child issues)
- Tested tools: `list_projects`, `add_item_to_project` (2/10, 100% success rate)

### Documentation
- README.md with Windows/Linux/macOS configuration
- Deployment notes with change visibility analysis
- Platform-specific wrapper guidance

### Security
- Token loaded from `.env.github` at runtime via wrapper
- Never stored in workspace configuration or version control

[0.0.1]: https://github.com/DarienSirius/mcp-gh-project/releases/tag/v0.0.1
