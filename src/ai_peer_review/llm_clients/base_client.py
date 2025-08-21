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
    
    def generate(self, prompt: str, max_retries: int = 3) -> str:
        """
        Generate response from LLM using OpenAI-compatible API format.
        
        Args:
            prompt: Input prompt
            max_retries: Maximum number of retry attempts for network errors
            
        Returns:
            Generated response
        """
        system_prompt = "您是一位学位与研究生教育领域的资深专家，具有丰富的学术评审经验。"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 不同模型的特殊配置
        temperature = 0.1
        max_tokens = 8000
        
        # 对某些模型使用默认temperature
        if any(model_name in self.model.lower() for model_name in ['gpt-5', 'o3']):
            temperature = 1.0  # 这些模型可能不支持0.1
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.post(self.base_url, headers=headers, json=data, timeout=300)
                response.raise_for_status()
                
                result = response.json()
                
                # 更详细的响应检查
                if "choices" not in result:
                    raise Exception(f"API response missing 'choices' field: {result}")
                
                if not result["choices"]:
                    raise Exception(f"API response has empty 'choices' array: {result}")
                
                if "message" not in result["choices"][0]:
                    raise Exception(f"API response missing 'message' field in choice: {result['choices'][0]}")
                
                if "content" not in result["choices"][0]["message"]:
                    raise Exception(f"API response missing 'content' field in message: {result['choices'][0]['message']}")
                
                content = result["choices"][0]["message"]["content"]
                if not content:
                    raise Exception("API response returned empty content")
                    
                # 检查是否因为max_tokens限制被截断
                if "finish_reason" in result["choices"][0]:
                    finish_reason = result["choices"][0]["finish_reason"]
                    if finish_reason == "length":
                        print(f"Warning: Response was truncated due to max_tokens limit for model {self.model}")
                    elif finish_reason != "stop":
                        print(f"Warning: Response finished with reason '{finish_reason}' for model {self.model}")
                
                return content.strip()
                
            except requests.exceptions.Timeout as e:
                last_error = f"API request timed out after 300 seconds: {e}"
                if attempt < max_retries - 1:
                    print(f"Timeout error for {self.model}, retrying... (attempt {attempt + 1}/{max_retries})")
                    continue
            except (requests.exceptions.ConnectionError, requests.exceptions.SSLError) as e:
                last_error = f"API connection/SSL failed: {e}"
                if attempt < max_retries - 1:
                    print(f"Connection/SSL error for {self.model}, retrying... (attempt {attempt + 1}/{max_retries})")
                    import time
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
            except requests.exceptions.HTTPError as e:
                last_error = f"API HTTP error: {e}, Response: {response.text if 'response' in locals() else 'No response'}"
                # HTTP错误通常不需要重试
                break
            except requests.exceptions.RequestException as e:
                last_error = f"API request failed: {e}"
                if attempt < max_retries - 1:
                    print(f"Request error for {self.model}, retrying... (attempt {attempt + 1}/{max_retries})")
                    continue
            except (KeyError, IndexError) as e:
                last_error = f"Invalid API response format: {e}, Response: {result if 'result' in locals() else 'No parsed result'}"
                break
            except json.JSONDecodeError as e:
                last_error = f"Failed to parse API response as JSON: {e}, Raw response: {response.text if 'response' in locals() else 'No response'}"
                break
        
        # 如果所有重试都失败了，抛出最后一个错误
        raise Exception(last_error)
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the actual model name to use in API requests."""
        pass