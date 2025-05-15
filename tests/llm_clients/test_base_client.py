import pytest
from abc import ABC, abstractmethod

from ai_peer_review.llm_clients.base_client import BaseLLMClient


class TestBaseLLMClient:
    def test_base_client_is_abstract(self):
        # Verify that BaseLLMClient is an abstract class
        assert issubclass(BaseLLMClient, ABC)
        
        # Verify that generate is an abstract method
        assert hasattr(BaseLLMClient, 'generate')
        assert getattr(BaseLLMClient.generate, '__isabstractmethod__', False)
        
        # Verify that we cannot instantiate the base class
        with pytest.raises(TypeError):
            BaseLLMClient()
    
    def test_base_client_subclass(self):
        # Create a concrete subclass for testing
        class ConcreteLLMClient(BaseLLMClient):
            def generate(self, prompt: str) -> str:
                return f"Response to: {prompt}"
        
        # Verify that we can instantiate the concrete subclass
        client = ConcreteLLMClient()
        
        # Verify that we can call the generate method
        response = client.generate("Hello")
        assert response == "Response to: Hello"