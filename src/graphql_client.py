"""GitHub GraphQL API client for project management operations."""
import os
import json
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GitHubGraphQLClient:
    """Client for GitHub GraphQL API operations."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize with GitHub personal access token."""
        self.token = token or os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
        if not self.token:
            raise ValueError("GITHUB_PERSONAL_ACCESS_TOKEN not found in environment")
        
        self.api_url = "https://api.github.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query and return the response."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        logger.info(f"Executing GraphQL query with variables: {variables}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            if "errors" in result:
                error_msg = json.dumps(result["errors"], indent=2)
                logger.error(f"GraphQL errors: {error_msg}")
                raise Exception(f"GraphQL query failed: {error_msg}")
            
            return result.get("data", {})
