from abc import ABC, abstractmethod
import os
import json
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseLLMClient(ABC):
    """Base class for LLM clients."""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            model: Model name
            api_key: API key (will use environment variables if not provided)
            base_url: Base URL for API (will use environment variables if not provided)
        """
        self.model = model
        self.api_key = api_key or os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("BASE_URL") or os.getenv("OPENAI_BASE_URL", "https://yunwu.ai/v1")
        
        if not self.api_key:
            raise ValueError("API key must be provided via parameter or environment variable (API_KEY or OPENAI_API_KEY)")
            
        # Ensure base_url ends with /chat/completions for OpenAI format
        if not self.base_url.endswith("/chat/completions"):
            if self.base_url.endswith("/"):
                self.base_url += "chat/completions"
            else:
                self.base_url += "/chat/completions"
    
    def generate(self, prompt: str) -> str:
        """
        Generate response from LLM using OpenAI-compatible API format.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated response
        """
        system_prompt = "您是一位学位与研究生教育领域的资深专家，具有丰富的学术评审经验。"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid API response format: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse API response: {e}")
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the actual model name to use in API requests."""
        pass