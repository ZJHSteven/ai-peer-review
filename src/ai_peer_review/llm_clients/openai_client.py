import os
from typing import Optional
from openai import OpenAI

from .base_client import BaseLLMClient
from ..utils.config import get_api_key


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI API."""
    
    def __init__(self, model: str, api_key: Optional[str] = None):
        """
        Initialize OpenAI client.
        
        Args:
            model: Model name
            api_key: OpenAI API key (optional, will use OPENAI_API_KEY env var if not provided)
        """
        self.model = model
        self.api_key = api_key or get_api_key("openai")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided via the config command, API parameter, or OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, prompt: str) -> str:
        """
        Generate response from OpenAI model.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a neuroscientist and expert in brain imaging."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        return response.choices[0].message.content.strip()