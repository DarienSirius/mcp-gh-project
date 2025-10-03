# Testing Strategy for MCP Server Development

**Critical Insight:** MCP server crashes are INVISIBLE - you only see missing tools, no error logs.

## Testing Philosophy

**NEVER** deploy untested code to live MCP server. Test in isolation first.

## Test Pyramid

### Level 1: Unit Tests (Python unittest)
- Test individual tool functions in isolation
- Mock GraphQL client responses
- Verify JSON output format
- Test error handling paths

### Level 2: Integration Tests (Manual Python)
- Run tool functions directly (not via MCP)
- Use real GitHub API with test repository
- Verify GraphQL queries are valid
- Check authentication works

### Level 3: MCP Protocol Tests (Manual)
- Start server in terminal (see stderr output)
- Use `mcp` CLI to list tools
- Invoke tools via CLI (not Copilot yet)
- Verify JSON-RPC responses

### Level 4: Live Deployment Tests (VSCode)
- Add to workspace config
- Restart MCP servers
- Test via Copilot Chat
- Monitor for missing tools (crash indicator)

## Testing Workflow for Refactoring

### Phase 1: Create Test Harness FIRST
```bash
tests/
├── unit/                        # Fast, isolated tests
│   ├── test_base_resource.py
│   ├── test_project_list.py
│   ├── test_project_get.py
│   └── ...
├── integration/                 # Real API calls
│   ├── test_graphql_queries.py
│   └── test_live_tools.py
├── fixtures/                    # Mock data
│   ├── list_projects_response.json
│   └── ...
└── run_tests.py                # Test runner
```

### Phase 2: Test Original Monolith
- Extract test cases from working v0.0.1
- Capture input/output pairs
- Document expected behavior
- Create regression test suite

### Phase 3: TDD Refactoring
1. Write test for new module
2. Extract code from monolith
3. Run test (should pass)
4. Commit atomically
5. Repeat for next module

### Phase 4: Integration Testing
- Test server startup (`python src/server.py`)
- Check stderr for errors
- Use `mcp` CLI to verify tools load
- Test each tool via CLI

### Phase 5: Manual MCP Testing
- Start server in dedicated terminal (see logs)
- Monitor stderr output
- Test tools one by one
- Document any crashes

## Test Commands

### Run Unit Tests
```bash
python -m pytest tests/unit/ -v
```

### Run Integration Tests
```bash
GITHUB_PERSONAL_ACCESS_TOKEN=<token> python -m pytest tests/integration/ -v
```

### Test Server Startup
```bash
cd /c/Users/victorb/code/.miast0/_/mcp-gh-project
export GITHUB_PERSONAL_ACCESS_TOKEN=$(grep GITHUB_PERSONAL_ACCESS_TOKEN ../../../DSSCC/.env.github | cut -d= -f2)
python src/server.py
# Should show: "MCP Server running..."
# Ctrl+C to stop
```

### Test via MCP CLI
```bash
# List available tools
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python src/server.py

# Invoke tool
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_projects","arguments":{"owner":"wordgarden-dev"}},"id":2}' | python src/server.py
```

## Crash Detection Patterns

### Symptom: Tool missing from MCP client
**Cause:** Server crashed during startup or tool registration

**Debug:**
1. Run server in terminal: `python src/server.py`
2. Check stderr for Python exceptions
3. Look for import errors, syntax errors
4. Check GraphQL query syntax

### Symptom: Tool appears but doesn't respond
**Cause:** Exception during tool execution

**Debug:**
1. Run tool function directly in Python REPL
2. Check GraphQL client error handling
3. Verify authentication token is valid
4. Test with minimal input

### Symptom: Tool returns empty/invalid JSON
**Cause:** JSON serialization error or missing return

**Debug:**
1. Check function returns proper JSON string
2. Verify all code paths have return statements
3. Test with various input combinations
4. Check for unhandled exceptions

## Development Cycle

**BEFORE refactoring:**
1. ✅ Create test harness
2. ✅ Extract test cases from working v0.0.1
3. ✅ Verify tests pass on current code

**DURING refactoring:**
1. ⚠️ Write test for new module
2. ⚠️ Extract code
3. ⚠️ Run test (must pass)
4. ⚠️ Commit atomically
5. ⚠️ Test server startup (catch import errors)

**AFTER refactoring:**
1. ✅ Run full test suite
2. ✅ Test server startup in terminal
3. ✅ Test via MCP CLI
4. ✅ Manual testing in VSCode
5. ✅ Monitor for crashes (missing tools)

## Git Workflow

### Atomic Commits
```bash
# Phase 1: Infrastructure
git add src/resources/ src/graphql/ src/lib/
git commit -m "chore: Create directory structure for refactoring"

# Phase 2: Extract GraphQL (per query)
git add src/graphql/queries/list_projects.graphql
git commit -m "refactor: Extract list_projects GraphQL query"

# Phase 3: Base class
git add src/resources/base.py tests/unit/test_base_resource.py
git commit -m "refactor: Add BaseResource with GraphQL loading"

# Phase 4: First resource (with tests)
git add src/resources/project/list.py tests/unit/test_project_list.py
git commit -m "refactor: Extract list_projects to resource module"

# Test after each commit
python -m pytest tests/unit/ -v
python src/server.py  # Check for crashes
```

## Rollback Strategy

If server crashes and tools disappear:
1. `git log --oneline` - Find last working commit
2. `git diff HEAD~1` - See what broke
3. `git checkout HEAD~1 -- src/` - Rollback code
4. Test again
5. Fix issue in smaller increments

## Success Metrics

✅ All tests pass  
✅ Server starts without errors  
✅ All 11 tools appear in MCP client  
✅ All tools respond to test inputs  
✅ No stderr exceptions during execution  
✅ JSON responses valid and complete

---

**Remember:** Invisible crashes are the enemy. Test everything before trusting MCP integration.
