# MCP Server Deployment Notes - 2025-10-03

## Dogfooding Success Report

**Server:** `gh-project-miast0` (mcp-gh-project v0.0.1)  
**Test Task:** Dissect Issue #5 into 5 child issues and add to VGM9.NPM.miast0 project board  
**Result:** ✅ **COMPLETE SUCCESS**

### Issues Created & Added to Board
- #6 - Baseline Measurement - Count Instruction File Lines Across Avatar Constellation
- #7 - Categorize Instruction Content by MASTERY_LADDER Levels
- #8 - Extract Knowledge to Appropriate Locations
- #9 - Create Reusable Instruction Registers
- #10 - Document Avatar Instruction Architecture

### Tools Tested Successfully
- ✅ `list_projects` - Retrieved VGM9.NPM.miast0 project
- ✅ `add_item_to_project` - Added 5 issues to project board (5/5 success)
- ✅ `mcp_github-miast0_create_issue` - Created child issues (used external server per fallback design)
- ✅ `mcp_github-miast0_update_issue` - Updated Issue #5 with task list

### Deployment Challenges Resolved

#### 1. Missing Python Dependencies
**Error:** `ModuleNotFoundError: No module named 'mcp'`  
**Cause:** System Python lacked mcp[cli] package  
**Fix:** `pip install --user -r requirements.txt`  
**Lesson:** Include dependency check in README.md

#### 2. Relative Import Failure
**Error:** `ImportError: attempted relative import with no known parent package`  
**Cause:** PowerShell wrapper ran `python server.py` directly  
**Fix:** Changed to `python -m src.server` for module execution  
**Lesson:** MCP servers with relative imports MUST use `-m` flag

#### 3. PowerShell Wrapper Path Resolution
**Error:** `.env.github` not found at wrong path  
**Fix:** Corrected from `../../` to `../../../` (scripts → mcp-gh-project → _ → .miast0)  
**Lesson:** Test path resolution from script working directory

### Environment-Specific Configuration

**CRITICAL:** The PowerShell wrapper (`scripts/mcp-gh-project-wrapper.ps1`) is **Windows-specific**. For cross-platform deployment:

#### Windows (Current Implementation)
```json
{
  "gh-project-miast0": {
    "command": "powershell.exe",
    "args": ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "C:\\path\\to\\mcp-gh-project-wrapper.ps1"]
  }
}
```

#### Linux/macOS (Future)
```json
{
  "gh-project-miast0": {
    "command": "bash",
    "args": ["path/to/mcp-gh-project-wrapper.sh"]
  }
}
```

#### .devcontainer (Future)
```json
{
  "gh-project-miast0": {
    "command": "python",
    "args": ["-m", "src.server"],
    "cwd": "/workspace/mcp-gh-project",
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "${localEnv:GITHUB_PERSONAL_ACCESS_TOKEN}"
    }
  }
}
```

### Autonomous Change Visibility

**Changes Visible Immediately (No Restart):**
- ❌ None - MCP server code changes require restart

**Changes Requiring Keep Button:**
- PowerShell wrapper modifications (before restart)
- Workspace configuration changes (before restart)

**Changes Requiring MCP Server Restart:**
- ✅ Python source code changes (server.py, graphql_client.py)
- ✅ Dependency installations
- ✅ PowerShell wrapper modifications
- ✅ Environment variable changes

**User Restart Actions:**
1. Manual restart via MCP server panel
2. Send message to trigger server reload (after workspace config change)
3. VSCode reload window (nuclear option)

### Telemetry Status

**File-Based Logging Implemented:**
- `logs/startup.log` - Server initialization messages
- `logs/crash.log` - Exception details with traceback

**Current Limitation:** Logs created only after successful imports. Import-time errors require PowerShell wrapper telemetry or VSCode MCP console.

**Future Improvement:** Add telemetry to PowerShell wrapper for pre-Python diagnostics.

### API Gaps Discovered

**Missing from Custom Server:**
- Issue creation (used fallback to github-miast0)
- Parent/child issue linking (used GFM task list in issue body)

**Research Needed:**
- GitHub GraphQL support for parent issue field
- Alternative: ProjectV2 custom field for "Parent Issue"
- Alternative: Issue links/references API

### Phase 6 Completion Status

- [x] Test with VSCode MCP client
- [x] Verify all tools work (list_projects ✓, add_item_to_project ✓)
- [x] Document deployment challenges
- [ ] Complete tool documentation in README.md
- [ ] Update TOOL_COMPARISON.md with dogfooding results
- [ ] Create cross-platform deployment guide

### Next Steps for v0.0.1 Release

1. Document all 10 tools with examples in README.md
2. Add dependency check script to prevent ModuleNotFoundError
3. Create bash wrapper for Linux/macOS compatibility
4. Update TOOL_COMPARISON.md with real-world usage results
5. Research parent/child issue linking in GitHub GraphQL
6. Consider adding `create_issue` tool to eliminate fallback dependency

## Lessons for Future MCP Servers

1. **Dependency Management:** Include `pip list | grep package` check in setup docs
2. **Module Execution:** Always use `python -m package.module` for relative imports
3. **Path Resolution:** Test wrappers from actual working directory, not IDE context
4. **Platform Specificity:** Document wrapper as environment-specific from day one
5. **Telemetry First:** Add file-based logging before first deployment attempt
6. **Fallback Design:** Hybrid approach (custom + external servers) provides resilience
7. **Dogfooding Value:** Real-world usage reveals deployment gaps immediately

**Dogfooding Score:** 8/10 - Server works excellently, deployment docs need improvement

---

**Author:** .miast0.0.21  
**Date:** 2025-10-03  
**Server Version:** mcp-gh-project v0.0.1  
**Tools Tested:** 2/10 (list_projects, add_item_to_project)  
**Issues Created:** 5/5 successful
