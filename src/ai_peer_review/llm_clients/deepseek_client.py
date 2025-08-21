import os
from typing import Optional

from .base_client import BaseLLMClient


class DeepSeekClient(BaseLLMClient):
    """Client for DeepSeek models using OpenAI-compatible API format."""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize DeepSeek client.
        
        Args:
            model: Model name
            api_key: API key (optional, will use environment variables if not provided)
            base_url: Base URL for API (optional, will use environment variables if not provided)
        """
        super().__init__(model, api_key, base_url)
    
    def get_model_name(self) -> str:
        """Get the actual model name to use in API requests."""
        return self.model