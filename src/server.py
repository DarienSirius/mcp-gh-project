"""
MCP Server for GitHub Project Management

Provides tools for managing GitHub Projects via GraphQL API.
"""
import json
import logging
from mcp.server.fastmcp import FastMCP
from .graphql_client import GitHubGraphQLClient
from .auth import load_github_token

# Configure logging to stderr (never stdout - corrupts JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("gh-project")

# Initialize GitHub client (will be set in main())
github_client: GitHubGraphQLClient = None

@mcp.tool()
async def list_projects(owner: str, owner_type: str = "organization", limit: int = 20) -> str:
    """
    List GitHub Projects for an organization or user.
    
    Args:
        owner: Organization or user login name
        owner_type: Either "organization" or "user"
        limit: Maximum number of projects to return (default: 20)
    
    Returns:
        JSON string with list of projects (id, title, number, url)
    """
    logger.info(f"list_projects called for {owner_type} '{owner}' with limit {limit}")
    
    query = """
    query($owner: String!, $limit: Int!) {
      %s(login: $owner) {
        projectsV2(first: $limit) {
          nodes {
            id
            title
            number
            url
            shortDescription
            public
          }
        }
      }
    }
    """ % owner_type
    
    result = await github_client.execute_query(query, {"owner": owner, "limit": limit})
    projects = result.get(owner_type, {}).get("projectsV2", {}).get("nodes", [])
    
    return json.dumps({"projects": projects}, indent=2)

@mcp.tool()
async def get_project_details(owner: str, project_number: int, owner_type: str = "organization") -> str:
    """
    Get detailed information about a specific GitHub Project.
    
    Args:
        owner: Organization or user login name
        project_number: Project number (from URL)
        owner_type: Either "organization" or "user"
    
    Returns:
        JSON string with project details (id, title, description, fields, etc.)
    """
    logger.info(f"get_project_details called for {owner_type} '{owner}' project #{project_number}")
    
    query = """
    query($owner: String!, $number: Int!) {
      %s(login: $owner) {
        projectV2(number: $number) {
          id
          title
          number
          url
          shortDescription
          readme
          public
          closed
          createdAt
          updatedAt
          fields(first: 20) {
            nodes {
              ... on ProjectV2FieldCommon {
                id
                name
              }
            }
          }
        }
      }
    }
    """ % owner_type
    
    result = await github_client.execute_query(query, {"owner": owner, "number": project_number})
    project = result.get(owner_type, {}).get("projectV2", {})
    
    if not project:
        return json.dumps({"error": f"Project #{project_number} not found for {owner}"})
    
    return json.dumps({"project": project}, indent=2)

@mcp.tool()
async def create_project(owner_id: str, title: str, description: str = "") -> str:
    """
    Create a new GitHub Project.
    
    Args:
        owner_id: Node ID of the organization or user (use get_owner_id tool to find)
        title: Project title
        description: Project short description (optional)
    
    Returns:
        JSON string with created project details (id, title, url)
    """
    logger.info(f"create_project called with title '{title}'")
    
    mutation = """
    mutation($ownerId: ID!, $title: String!, $description: String) {
      createProjectV2(input: {ownerId: $ownerId, title: $title, shortDescription: $description}) {
        projectV2 {
          id
          title
          number
          url
          shortDescription
        }
      }
    }
    """
    
    result = await github_client.execute_query(
        mutation, 
        {"ownerId": owner_id, "title": title, "description": description}
    )
    project = result.get("createProjectV2", {}).get("projectV2", {})
    
    return json.dumps({"project": project}, indent=2)

@mcp.tool()
async def update_project_settings(project_id: str, title: str = None, description: str = None, 
                                  readme: str = None, public: bool = None) -> str:
    """
    Update GitHub Project settings.
    
    Args:
        project_id: Project node ID
        title: New project title (optional)
        description: New short description (optional)
        readme: New README content (optional)
        public: Set project visibility (optional)
    
    Returns:
        JSON string with updated project details
    """
    logger.info(f"update_project_settings called for project {project_id}")
    
    # Build input object dynamically
    input_fields = {"projectId": project_id}
    if title: input_fields["title"] = title
    if description: input_fields["shortDescription"] = description
    if readme: input_fields["readme"] = readme
    if public is not None: input_fields["public"] = public
    
    mutation = """
    mutation($projectId: ID!, $title: String, $shortDescription: String, $readme: String, $public: Boolean) {
      updateProjectV2(input: {projectId: $projectId, title: $title, shortDescription: $shortDescription, readme: $readme, public: $public}) {
        projectV2 {
          id
          title
          number
          url
          shortDescription
          readme
          public
        }
      }
    }
    """
    
    result = await github_client.execute_query(mutation, input_fields)
    project = result.get("updateProjectV2", {}).get("projectV2", {})
    
    return json.dumps({"project": project}, indent=2)

@mcp.tool()
async def get_owner_id(owner: str, owner_type: str = "organization") -> str:
    """
    Get the node ID for an organization or user (needed for create_project).
    
    Args:
        owner: Organization or user login name
        owner_type: Either "organization" or "user"
    
    Returns:
        JSON string with owner node ID
    """
    logger.info(f"get_owner_id called for {owner_type} '{owner}'")
    
    query = """
    query($owner: String!) {
      %s(login: $owner) {
        id
        login
      }
    }
    """ % owner_type
    
    result = await github_client.execute_query(query, {"owner": owner})
    owner_data = result.get(owner_type, {})
    
    if not owner_data:
        return json.dumps({"error": f"{owner_type.capitalize()} '{owner}' not found"})
    
    return json.dumps({"owner_id": owner_data.get("id"), "login": owner_data.get("login")}, indent=2)

@mcp.tool()
async def add_item_to_project(project_id: str, content_id: str) -> str:
    """
    Add an issue or pull request to a GitHub Project.
    
    Args:
        project_id: Project node ID
        content_id: Issue or PR node ID
    
    Returns:
        JSON string with created project item details
    """
    logger.info(f"add_item_to_project called for project {project_id}, content {content_id}")
    
    mutation = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
          id
          content {
            ... on Issue {
              title
              number
              url
            }
            ... on PullRequest {
              title
              number
              url
            }
          }
        }
      }
    }
    """
    
    result = await github_client.execute_query(mutation, {"projectId": project_id, "contentId": content_id})
    item = result.get("addProjectV2ItemById", {}).get("item", {})
    
    return json.dumps({"item": item}, indent=2)

@mcp.tool()
async def remove_item_from_project(project_id: str, item_id: str) -> str:
    """
    Remove an item from a GitHub Project.
    
    Args:
        project_id: Project node ID
        item_id: Project item node ID
    
    Returns:
        JSON string with deleted item ID
    """
    logger.info(f"remove_item_from_project called for project {project_id}, item {item_id}")
    
    mutation = """
    mutation($projectId: ID!, $itemId: ID!) {
      deleteProjectV2Item(input: {projectId: $projectId, itemId: $itemId}) {
        deletedItemId
      }
    }
    """
    
    result = await github_client.execute_query(mutation, {"projectId": project_id, "itemId": item_id})
    deleted_id = result.get("deleteProjectV2Item", {}).get("deletedItemId")
    
    return json.dumps({"deleted_item_id": deleted_id}, indent=2)

@mcp.tool()
async def list_project_items(project_id: str, limit: int = 20) -> str:
    """
    List all items in a GitHub Project.
    
    Args:
        project_id: Project node ID
        limit: Maximum number of items to return (default: 20)
    
    Returns:
        JSON string with list of project items (issues, PRs, draft issues)
    """
    logger.info(f"list_project_items called for project {project_id} with limit {limit}")
    
    query = """
    query($projectId: ID!, $limit: Int!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: $limit) {
            nodes {
              id
              content {
                ... on Issue {
                  title
                  number
                  url
                  state
                }
                ... on PullRequest {
                  title
                  number
                  url
                  state
                }
                ... on DraftIssue {
                  title
                  body
                }
              }
            }
          }
        }
      }
    }
    """
    
    result = await github_client.execute_query(query, {"projectId": project_id, "limit": limit})
    items = result.get("node", {}).get("items", {}).get("nodes", [])
    
    return json.dumps({"items": items}, indent=2)

@mcp.tool()
async def update_item_field_value(project_id: str, item_id: str, field_id: str, 
                                  value_text: str = None, value_number: float = None,
                                  value_date: str = None, value_option_id: str = None) -> str:
    """
    Update a custom field value for a project item.
    
    Args:
        project_id: Project node ID
        item_id: Project item node ID
        field_id: Field node ID
        value_text: Text value (for text fields)
        value_number: Number value (for number fields)
        value_date: Date value in YYYY-MM-DD format (for date fields)
        value_option_id: Option ID (for single select fields)
    
    Returns:
        JSON string with updated project item
    """
    logger.info(f"update_item_field_value called for project {project_id}, item {item_id}, field {field_id}")
    
    # Build value object based on provided parameters
    value_obj = {}
    if value_text is not None:
        value_obj = {"text": value_text}
    elif value_number is not None:
        value_obj = {"number": value_number}
    elif value_date is not None:
        value_obj = {"date": value_date}
    elif value_option_id is not None:
        value_obj = {"singleSelectOptionId": value_option_id}
    else:
        return json.dumps({"error": "No value provided. Specify one of: value_text, value_number, value_date, value_option_id"})
    
    mutation = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
      updateProjectV2ItemFieldValue(
        input: {projectId: $projectId, itemId: $itemId, fieldId: $fieldId, value: $value}
      ) {
        projectV2Item {
          id
        }
      }
    }
    """
    
    result = await github_client.execute_query(
        mutation,
        {"projectId": project_id, "itemId": item_id, "fieldId": field_id, "value": value_obj}
    )
    item = result.get("updateProjectV2ItemFieldValue", {}).get("projectV2Item", {})
    
    return json.dumps({"item": item}, indent=2)

@mcp.tool()
async def get_project_fields(project_id: str) -> str:
    """
    Get all fields configured for a GitHub Project.
    
    Args:
        project_id: Project node ID
    
    Returns:
        JSON string with list of fields (id, name, type, options for single select)
    """
    logger.info(f"get_project_fields called for project {project_id}")
    
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 50) {
            nodes {
              ... on ProjectV2FieldCommon {
                id
                name
              }
              ... on ProjectV2SingleSelectField {
                id
                name
                options {
                  id
                  name
                }
              }
              ... on ProjectV2IterationField {
                id
                name
                configuration {
                  iterations {
                    id
                    title
                    startDate
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    
    result = await github_client.execute_query(query, {"projectId": project_id})
    fields = result.get("node", {}).get("fields", {}).get("nodes", [])
    
    return json.dumps({"fields": fields}, indent=2)

def main():
    """Run the MCP server using stdio transport."""
    global github_client
    
    logger.info("Starting GitHub Project Management MCP Server v0.0.1")
    
    # Initialize GitHub client with token from environment
    try:
        token = load_github_token()
        github_client = GitHubGraphQLClient(token)
        logger.info("GitHub client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize GitHub client: {e}")
        raise
    
    # Run MCP server with stdio transport
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
