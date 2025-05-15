import pytest
from unittest.mock import patch, MagicMock

from ai_peer_review.llm_clients.anthropic_client import AnthropicClient
from ai_peer_review.llm_clients.base_client import BaseLLMClient


class TestAnthropicClient:
    def test_anthropic_client_inheritance(self):
        # Verify that AnthropicClient inherits from BaseLLMClient
        assert issubclass(AnthropicClient, BaseLLMClient)
    
    @patch('ai_peer_review.llm_clients.anthropic_client.get_api_key')
    @patch('ai_peer_review.llm_clients.anthropic_client.Anthropic')
    def test_init_with_provided_api_key(self, mock_anthropic, mock_get_api_key):
        # Test initialization with a provided API key
        client = AnthropicClient(model="claude-3", api_key="test-key")
        
        # Check that get_api_key was not called
        mock_get_api_key.assert_not_called()
        
        # Check that Anthropic was initialized with the correct API key
        mock_anthropic.assert_called_once_with(api_key="test-key")
        
        # Check that the model was set correctly
        assert client.model == "claude-3"
        assert client.api_key == "test-key"
    
    @patch('ai_peer_review.llm_clients.anthropic_client.get_api_key')
    @patch('ai_peer_review.llm_clients.anthropic_client.Anthropic')
    def test_init_with_config_api_key(self, mock_anthropic, mock_get_api_key):
        # Mock get_api_key to return a predefined key
        mock_get_api_key.return_value = "config-key"
        
        # Test initialization without an API key
        client = AnthropicClient(model="claude-3")
        
        # Check that get_api_key was called with the correct key name
        mock_get_api_key.assert_called_once_with("anthropic")
        
        # Check that Anthropic was initialized with the correct API key
        mock_anthropic.assert_called_once_with(api_key="config-key")
        
        # Check that the model was set correctly
        assert client.model == "claude-3"
        assert client.api_key == "config-key"
    
    @patch('ai_peer_review.llm_clients.anthropic_client.get_api_key')
    def test_init_without_api_key(self, mock_get_api_key):
        # Mock get_api_key to return None (no API key available)
        mock_get_api_key.return_value = None
        
        # Test initialization without an API key should raise ValueError
        with pytest.raises(ValueError):
            AnthropicClient(model="claude-3")
    
    @patch('ai_peer_review.llm_clients.anthropic_client.get_api_key')
    @patch('ai_peer_review.llm_clients.anthropic_client.Anthropic')
    def test_generate(self, mock_anthropic, mock_get_api_key):
        # Mock get_api_key to return a predefined key
        mock_get_api_key.return_value = "test-key"
        
        # Mock the Anthropic client and response
        mock_anthropic_instance = MagicMock()
        mock_messages = MagicMock()
        mock_anthropic_instance.messages.create = mock_messages
        
        # Set up the response
        mock_content = MagicMock()
        mock_content.text = "Generated response"
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_messages.return_value = mock_response
        
        # Set up the mock Anthropic class to return our mock instance
        mock_anthropic.return_value = mock_anthropic_instance
        
        # Create the client and generate a response
        client = AnthropicClient(model="claude-3")
        response = client.generate("Test prompt")
        
        # Check that messages.create was called with the correct arguments
        mock_messages.assert_called_once_with(
            model="claude-3",
            system="You are a neuroscientist and expert in brain imaging.",
            max_tokens=4000,
            temperature=0.1,
            messages=[
                {"role": "user", "content": "Test prompt"}
            ]
        )
        
        # Check that the response is correct
        assert response == "Generated response"