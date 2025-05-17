import os
from typing import Optional
import google.generativeai as genai

from .base_client import BaseLLMClient
from ..utils.config import get_api_key, get_prompt


class GoogleClient(BaseLLMClient):
    """Client for Google Gemini API."""
    
    def __init__(self, model: str, api_key: Optional[str] = None):
        """
        Initialize Google Gemini client.
        
        Args:
            model: Model name
            api_key: Google API key (optional, will use GOOGLE_API_KEY env var if not provided)
        """
        self.model = model
        self.api_key = api_key or get_api_key("google")
        if not self.api_key:
            raise ValueError("Google API key must be provided via the config command, API parameter, or GOOGLE_API_KEY environment variable")
        
        genai.configure(api_key=self.api_key)
        self.model_obj = genai.GenerativeModel(self.model)
    
    def generate(self, prompt: str) -> str:
        """
        Generate response from Google Gemini model.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response
        """
        # Get system prompt from config
        system_instruction = get_prompt("system")
        if not system_instruction:
            system_instruction = "You are a neuroscientist and expert in brain imaging."
        
        response = self.model_obj.generate_content(
            [system_instruction, prompt],
            generation_config=genai.GenerationConfig(temperature=0.1)
        )
        
        return response.text