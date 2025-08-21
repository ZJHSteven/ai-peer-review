import os
from typing import Optional

from .base_client import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI API using direct JSON requests."""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            model: Model name
            api_key: OpenAI API key (optional, will use environment variables if not provided)
            base_url: Base URL for API (optional, will use environment variables if not provided)
        """
        super().__init__(model, api_key, base_url)
    
    def get_model_name(self) -> str:
        """Get the actual model name to use in API requests."""
        return self.model