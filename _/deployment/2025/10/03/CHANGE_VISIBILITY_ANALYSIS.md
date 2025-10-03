# Change Visibility Analysis - MCP Server Development

## Key Question
**Which changes can agents see autonomously vs. require Keep/Restart actions?**

## Shadow Copy Architecture (VSCode)

### read_file Behavior
- Returns VSCode's shadow copy, NOT filesystem state
- After MCP tool changes: Shows pending changes (not yet on disk)
- After terminal operations: May show old content until Keep pressed
- Mixed operations (MCP + terminal): Dangerous desync possible

### Keep/Undo Button Mechanics
**Keep Button:**
- `create_file`: Writes shadow content to disk
- `replace_string_in_file`: Updates file with changes
- **Effect:** Synchronizes shadow copy with filesystem

**Undo Button:**
- `create_file`: Creates 0-byte file (restores pre-creation state)
- `replace_string_in_file`: Restores original content from shadow history
- **Effect:** Can resurrect moved/deleted files from shadow copy

**Do Nothing:**
- Shadow copy permanently out of sync with filesystem
- `read_file` shows shadow | terminal commands work on actual files
- Mixed operations become unpredictable

## MCP Server Deployment: Autonomous Visibility

### Changes Visible Immediately (No Actions Required)
❌ **NONE** - MCP server code changes are never autonomously visible

### Changes Requiring Keep Button
- ✅ PowerShell wrapper modifications (before testing)
- ✅ Workspace configuration changes (before MCP server restart)
- ✅ Python source code edits (before restart)

**Agent Experience:** File appears changed in shadow copy but server runs old version from disk.

### Changes Requiring MCP Server Restart
- ✅ Python source code changes (`server.py`, `graphql_client.py`)
- ✅ Dependency installations (`pip install`)
- ✅ PowerShell wrapper modifications (after Keep)
- ✅ Environment variable changes (`.env.github`)

**Agent Experience:** Cannot directly trigger restart. Must request user action.

### User Restart Methods
1. **Manual restart** via MCP server panel in VSCode
2. **Send message** to trigger server reload (after workspace config change)
3. **VSCode reload window** (nuclear option)

**Agent Blindness:** Cannot see MCP server console output, cannot verify restart completion autonomously.

## Telemetry Solutions

### File-Based Logging (Implemented)
```python
log_dir = Path(__file__).parent.parent / "logs"
startup_log = log_dir / "startup.log"
crash_log = log_dir / "crash.log"
```

**Autonomous Visibility:**
- ✅ Agents can `read_file` on log files
- ✅ Detects startup success/failure
- ❌ Only works after successful Python imports

### Wrapper-Based Telemetry (Future)
```powershell
# Log before Python execution
Write-Output "$(Get-Date -Format 'o') Starting server..." | Out-File "$LogDir\wrapper.log" -Append
```

**Autonomous Visibility:**
- ✅ Captures pre-Python errors
- ✅ Records environment setup
- ❌ Requires user to persist wrapper changes (Keep button)

### CoCopilot Vision (Documented)
Proposed VSCode Extension + MCP Bridge for:
- `list_mcp_servers` - Check server status
- `restart_mcp_server` - Trigger restarts autonomously
- `get_mcp_server_logs` - Access stdout/stderr directly
- `get_tool_approval_state` - Understand autoApprove filters

**Impact:** Would eliminate Keep/Restart blindness entirely.

## Deployment Pipeline Visibility

### Phase 1: Code Changes
**Agent Actions:** `create_file`, `replace_string_in_file`  
**Visibility:** Shadow copy only (not disk)  
**Blocker:** Keep button required before testing

### Phase 2: Keep Button Press
**User Action:** Clicks Keep to persist changes  
**Visibility:** No system notification to agent  
**Workaround:** `read_file` to verify disk state

### Phase 3: MCP Server Restart
**User Action:** Manual restart via MCP panel  
**Visibility:** No completion notification to agent  
**Workaround:** Check file-based telemetry logs

### Phase 4: Testing
**Agent Actions:** Invoke MCP tools  
**Visibility:** Tool results visible immediately  
**Success:** Confirms deployment worked

## Recommendations for MCP Server Authors

1. **Implement file-based telemetry from day one**
   - Agents can monitor startup/crash logs autonomously
   - Eliminates blind debugging cycles

2. **Document Keep/Restart requirements clearly**
   - Set expectations for agent/human collaboration
   - Include "test that change worked" step after edits

3. **Use wrapper telemetry for pre-Python diagnostics**
   - Catches environment setup failures
   - Records token loading, path resolution

4. **Design for autonomous verification**
   - Return test data in tool responses
   - Log operation success/failure to files

5. **Request CoCopilot features from Microsoft/GitHub**
   - Self-aware MCP server management
   - Direct access to server stdout/stderr
   - Programmatic restart capability

## Real-World Example: gh-project-miast0 Deployment

**Iterations Required:** 3 restart cycles

**Cycle 1:**
- Agent: Fixed PowerShell path bug (`../../../.env.github`)
- Agent: Requested user restart
- User: Restarted server
- Result: `ModuleNotFoundError: No module named 'mcp'`

**Cycle 2:**
- Agent: Ran `pip install --user -r requirements.txt`
- Agent: Requested user restart
- User: Restarted server
- Result: `ImportError: attempted relative import with no known parent package`

**Cycle 3:**
- Agent: Changed wrapper to `python -m src.server`
- User: Pressed Keep button
- Agent: Requested user restart
- User: Restarted server
- Result: ✅ **10 tools discovered**

**Total Duration:** ~30 minutes  
**Agent Autonomy:** 40% (could fix issues, couldn't deploy/verify)  
**Human Interventions:** 6 (3 Keep buttons, 3 restarts)

---

**Conclusion:** MCP server development requires tight agent/human collaboration due to shadow copy architecture and deployment pipeline visibility gaps. File-based telemetry provides partial autonomy, but CoCopilot-style tooling would enable fully autonomous deployment cycles.

**Author:** .miast0.0.21  
**Date:** 2025-10-03  
**Context:** Dogfooding gh-project-miast0 deployment experience
