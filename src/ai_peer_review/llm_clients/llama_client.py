import os
from typing import Optional
import requests
import json

from .base_client import BaseLLMClient
from ..utils.config import get_api_key, get_prompt


class LlamaClient(BaseLLMClient):
    """Client for Llama models via Together.ai."""

    def __init__(self, model: str, api_key: Optional[str] = None):
        """
        Initialize Llama client using Together.ai API.

        Args:
            model: Model name (used for identification only)
            api_key: Together.ai API key (optional, will use TOGETHER_API_KEY env var if not provided)
        """
        self.model = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"  # Together.ai model name for Llama 4 Maverick
        self.api_key = api_key or get_api_key("together")
        if not self.api_key:
            raise ValueError("Together.ai API key must be provided via the config command, API parameter, or TOGETHER_API_KEY environment variable")

        self.api_url = "https://api.together.xyz/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def generate(self, prompt: str) -> str:
        """
        Generate response from Llama model via Together.ai.

        Args:
            prompt: Input prompt

        Returns:
            Generated response
        """
        # Get system prompt from config
        system_prompt = get_prompt("system")
        if not system_prompt:
            system_prompt = "You are a neuroscientist and expert in brain imaging."
            
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }

        response = requests.post(self.api_url, headers=self.headers, data=json.dumps(payload))

        if response.status_code != 200:
            raise RuntimeError(f"Error from Together.ai API: {response.text}")

        return response.json()["choices"][0]["message"]["content"]