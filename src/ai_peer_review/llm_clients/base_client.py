from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    """Base class for LLM clients."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from LLM."""
        pass