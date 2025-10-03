# Refactoring Design - v0.0.2 Architecture

**Status:** Design Phase  
**Goal:** Decompose 473-line server.py into resource-oriented architecture  
**Principle:** One function per file, resource/CRUD pattern, GraphQL as data

## Current State (v0.0.1)

```
src/
├── server.py          # 473 lines - MONOLITH
├── graphql_client.py  # 48 lines - Keep
├── auth.py           # 17 lines - Keep
└── __init__.py       # 2 lines - Keep
```

**Problem:** 11 tools in one file, GraphQL queries as strings, no separation of concerns

## Target Architecture (v0.0.2)

### Directory Structure

```
src/
├── server.py                    # ~50 lines: FastMCP app + tool registration
│
├── resources/                   # Resource-based organization
│   ├── __init__.py
│   ├── base.py                  # BaseResource class with shared patterns
│   │
│   ├── project/                 # Project resource (4 CRUD operations)
│   │   ├── __init__.py
│   │   ├── list.py             # list_projects
│   │   ├── get.py              # get_project_details
│   │   ├── create.py           # create_project
│   │   └── update.py           # update_project_settings
│   │
│   ├── item/                    # Item resource (4 operations)
│   │   ├── __init__.py
│   │   ├── add.py              # add_item_to_project
│   │   ├── remove.py           # remove_item_from_project
│   │   ├── list.py             # list_project_items
│   │   └── update.py           # update_item_field_value
│   │
│   ├── field/                   # Field resource (1 operation)
│   │   ├── __init__.py
│   │   └── get.py              # get_project_fields
│   │
│   └── owner/                   # Owner helper (1 operation)
│       ├── __init__.py
│       └── get_id.py           # get_owner_id
│
├── graphql/                     # GraphQL queries/mutations as .graphql files
│   ├── __init__.py
│   ├── queries/                 # Read operations
│   │   ├── list_projects.graphql
│   │   ├── get_project_details.graphql
│   │   ├── list_project_items.graphql
│   │   ├── get_project_fields.graphql
│   │   └── get_owner_id.graphql
│   │
│   └── mutations/               # Write operations
│       ├── create_project.graphql
│       ├── update_project.graphql
│       ├── add_item.graphql
│       ├── remove_item.graphql
│       └── update_field.graphql
│
├── lib/                         # Shared infrastructure (moved from src/)
│   ├── __init__.py
│   ├── graphql_client.py       # Existing GraphQL HTTP client
│   └── auth.py                 # Existing token loading
│
└── types/                       # Type definitions (future enhancement)
    └── github.py               # TypedDict for GraphQL responses
```

## Resource Pattern Analysis

### Resources Identified
1. **Project** - GitHub ProjectV2 board
2. **Item** - Issues/PRs/DraftIssues in project
3. **Field** - Custom columns/properties
4. **Owner** - Organization/User (helper for ID lookup)

### CRUD Operations per Resource

| Resource | Create | Read (Get) | Read (List) | Update | Delete/Remove |
|----------|--------|------------|-------------|--------|---------------|
| Project  | ✅ create | ✅ get | ✅ list | ✅ update | ❌ (future) |
| Item     | ✅ add | ❌ (future) | ✅ list | ✅ update_field | ✅ remove |
| Field    | ❌ (future) | ✅ get | ❌ (implicit in get) | ❌ (future) | ❌ (future) |
| Owner    | N/A | ✅ get_id | ❌ (future) | N/A | N/A |

**Total Tools:** 11 (v0.0.1) → Potential 20+ (v0.0.3+)

## Shared Patterns & Base Class

### BaseResource Class

```python
# resources/base.py
from pathlib import Path
from ..lib.graphql_client import GitHubGraphQLClient

class BaseResource:
    """Base class for all GitHub resource handlers"""
    
    def __init__(self, client: GitHubGraphQLClient):
        self.client = client
        self.graphql_dir = Path(__file__).parent.parent / "graphql"
    
    async def execute_query(self, query_file: str, variables: dict):
        """Load GraphQL from .graphql file and execute"""
        query = self._load_graphql(query_file)
        return await self.client.execute_query(query, variables)
    
    def _load_graphql(self, filename: str) -> str:
        """Load .graphql file from graphql/ directory"""
        query_path = self.graphql_dir / filename
        with open(query_path, 'r') as f:
            return f.read()
```

### Tool Registration Pattern

```python
# server.py
from mcp.server.fastmcp import FastMCP
from .resources.project import list as project_list
from .resources.project import get as project_get
# ... etc

mcp = FastMCP("gh-project")

# Register all tools
@mcp.tool()
async def list_projects(owner: str, owner_type: str = "organization", limit: int = 20) -> str:
    return await project_list.execute(owner, owner_type, limit)

# ... repeat for all 11 tools
```

## Migration Checklist

### Phase 1: Infrastructure Setup
- [ ] Create `design/` directory with this document
- [ ] Create `src/resources/` directory structure
- [ ] Create `src/graphql/queries/` directory
- [ ] Create `src/graphql/mutations/` directory
- [ ] Create `src/lib/` directory
- [ ] Create `src/types/` directory (optional)

### Phase 2: Extract GraphQL Queries
- [ ] Extract `list_projects` query → `graphql/queries/list_projects.graphql`
- [ ] Extract `get_project_details` query → `graphql/queries/get_project_details.graphql`
- [ ] Extract `create_project` mutation → `graphql/mutations/create_project.graphql`
- [ ] Extract `update_project_settings` mutation → `graphql/mutations/update_project.graphql`
- [ ] Extract `get_owner_id` query → `graphql/queries/get_owner_id.graphql`
- [ ] Extract `add_item_to_project` mutation → `graphql/mutations/add_item.graphql`
- [ ] Extract `remove_item_from_project` mutation → `graphql/mutations/remove_item.graphql`
- [ ] Extract `list_project_items` query → `graphql/queries/list_project_items.graphql`
- [ ] Extract `update_item_field_value` mutation → `graphql/mutations/update_field.graphql`
- [ ] Extract `get_project_fields` query → `graphql/queries/get_project_fields.graphql`

### Phase 3: Move Shared Infrastructure
- [ ] Move `src/graphql_client.py` → `src/lib/graphql_client.py`
- [ ] Move `src/auth.py` → `src/lib/auth.py`
- [ ] Update imports in server.py

### Phase 4: Create Base Resource Class
- [ ] Create `src/resources/base.py` with BaseResource class
- [ ] Implement `execute_query()` method
- [ ] Implement `_load_graphql()` method
- [ ] Add error handling and logging

### Phase 5: Extract Project Resource
- [ ] Create `src/resources/project/__init__.py`
- [ ] Create `src/resources/project/list.py` (list_projects)
- [ ] Create `src/resources/project/get.py` (get_project_details)
- [ ] Create `src/resources/project/create.py` (create_project)
- [ ] Create `src/resources/project/update.py` (update_project_settings)
- [ ] Update server.py to import and register project tools

### Phase 6: Extract Item Resource
- [ ] Create `src/resources/item/__init__.py`
- [ ] Create `src/resources/item/add.py` (add_item_to_project)
- [ ] Create `src/resources/item/remove.py` (remove_item_from_project)
- [ ] Create `src/resources/item/list.py` (list_project_items)
- [ ] Create `src/resources/item/update.py` (update_item_field_value)
- [ ] Update server.py to import and register item tools

### Phase 7: Extract Field Resource
- [ ] Create `src/resources/field/__init__.py`
- [ ] Create `src/resources/field/get.py` (get_project_fields)
- [ ] Update server.py to import and register field tools

### Phase 8: Extract Owner Resource
- [ ] Create `src/resources/owner/__init__.py`
- [ ] Create `src/resources/owner/get_id.py` (get_owner_id)
- [ ] Update server.py to import and register owner tools

### Phase 9: Refactor server.py
- [ ] Remove all tool implementations (keep only @mcp.tool() wrappers)
- [ ] Update all imports to use new resource structure
- [ ] Verify server.py is <100 lines
- [ ] Update logging configuration

### Phase 10: Testing & Validation
- [ ] Test all 11 tools still work (no functional changes)
- [ ] Verify GraphQL files load correctly
- [ ] Check error handling works
- [ ] Validate type hints and docstrings
- [ ] Run linter on all new files

### Phase 11: Documentation
- [ ] Update README.md with new architecture section
- [ ] Document BaseResource pattern
- [ ] Add developer guide for adding new resources
- [ ] Update SPRINT_LOG.md with refactoring notes

### Phase 12: Git Commit
- [ ] Commit refactoring: "refactor: Decompose monolith into resource/CRUD architecture"
- [ ] Update version to v0.0.2 in package.json
- [ ] Tag commit as v0.0.2

## Success Criteria

✅ **File Size:** No Python file >100 lines  
✅ **Separation:** GraphQL queries in .graphql files (not strings)  
✅ **DRY:** Shared patterns in BaseResource class  
✅ **Scalability:** Easy to add new resources (milestone/, draft/)  
✅ **Functionality:** All 11 tools work identically to v0.0.1  
✅ **Type Safety:** Type hints on all functions  
✅ **Documentation:** Architecture documented in README.md

## Benefits

1. **Maintainability:** Find any tool in 5 seconds (resource/operation path)
2. **Testability:** Unit test individual tools in isolation
3. **Scalability:** Add milestone resource = 4 new files (not 200 lines in monolith)
4. **Readability:** Each file does ONE thing (SRP compliance)
5. **Reusability:** BaseResource pattern works for any GitHub resource
6. **Debuggability:** Stack traces show exact file/function
7. **Collaboration:** Multiple devs can work on different resources without conflicts

## Risk Mitigation

**Risk:** Breaking existing functionality during refactoring  
**Mitigation:** Test each tool after migration, commit atomically per resource

**Risk:** Import path complexity  
**Mitigation:** Use relative imports, clear __init__.py exports

**Risk:** GraphQL file loading overhead  
**Mitigation:** Consider caching loaded queries in BaseResource (v0.0.3)

**Risk:** Over-engineering for 11 tools  
**Mitigation:** This architecture scales to 50+ tools (GitHub has 100+ resource types)

---

**Next Steps:**
1. Review this design document
2. Get approval for architecture
3. Execute Phase 1-12 systematically
4. Track progress with checkboxes above
