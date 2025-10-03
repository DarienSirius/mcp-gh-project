# MCP Server Crash Detection - Autonomous Telemetry Design

## Problem Statement

**Blind Spot:** MCP server stdout/stderr goes to VSCode output panel, not accessible via MCP tools
**Impact:** Autonomous agents can't detect their own server crashes or debug startup failures
**User Experience:** User must manually report errors, breaking autonomous flow

## Proposed Solution: File-Based Telemetry

### Architecture

```
_/mcp-gh-project/
├── logs/
│   ├── startup.log          # Server initialization
│   ├── crash.log            # Fatal errors
│   └── operations.log       # Tool call audit trail
```

### Implementation Pattern

```python
# In src/server.py
import logging
from pathlib import Path

log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Startup logging
startup_log = log_dir / "startup.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Keep stderr for VSCode
        logging.FileHandler(startup_log)  # ADD file logging
    ]
)

# Crash detection
try:
    main()
except Exception as e:
    crash_log = log_dir / "crash.log"
    with open(crash_log, 'a') as f:
        f.write(f"{datetime.now()}: {e}\n{traceback.format_exc()}\n")
    raise
```

### Autonomous Detection Pattern

Agent can check for crashes via:
```bash
# Check if server started successfully
tail -1 logs/startup.log  # Should show "Server ready"

# Check for recent crashes
cat logs/crash.log | tail -10
```

### Benefits

1. **Autonomous Debugging:** Agent can read its own error logs
2. **Crash Recovery:** Detect crashes and trigger fixes
3. **Audit Trail:** Track tool usage patterns
4. **User Transparency:** Both agent and user see same logs

### Implementation Priority

**HIGH** - This is foundational for autonomous operation
- Add to v0.0.2 refactoring plan
- Include in all future MCP servers
- Establish as VGM9 MCP server pattern

## Open Question

Should crash logs be SP.CFN.AE compliant (dated directories)?
- `logs/2025/10/03/crash-13-19-24.log`
- Benefits: Historical analysis, clean organization
- Cost: Complexity in "latest crash" detection
