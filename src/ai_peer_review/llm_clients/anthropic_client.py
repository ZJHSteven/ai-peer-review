import os
from typing import Optional
from anthropic import Anthropic

from .base_client import BaseLLMClient
from ..utils.config import get_api_key, get_prompt


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic API."""
    
    def __init__(self, model: str, api_key: Optional[str] = None):
        """
        Initialize Anthropic client.
        
        Args:
            model: Model name
            api_key: Anthropic API key (optional, will use ANTHROPIC_API_KEY env var if not provided)
        """
        self.model = model
        self.api_key = api_key or get_api_key("anthropic")
        if not self.api_key:
            raise ValueError("Anthropic API key must be provided via the config command, API parameter, or ANTHROPIC_API_KEY environment variable")
        
        self.client = Anthropic(api_key=self.api_key)
    
    def generate(self, prompt: str) -> str:
        """
        Generate response from Anthropic model.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response
        """
        # Get system prompt from config
        system_prompt = get_prompt("system")
        if not system_prompt:
            system_prompt = "You are a neuroscientist and expert in brain imaging."
            
        response = self.client.messages.create(
            model=self.model,
            system=system_prompt,
            max_tokens=4000,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text