"""Authentication helper for loading GitHub PAT."""
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def load_github_token() -> str:
    """Load GitHub PAT from environment variable."""
    token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    if not token:
        raise ValueError(
            "GITHUB_PERSONAL_ACCESS_TOKEN not found in environment. "
            "Ensure PowerShell wrapper script loads .env.github correctly."
        )
    logger.info("Successfully loaded GitHub PAT from environment")
    return token
