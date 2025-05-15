import pytest
from unittest.mock import patch, MagicMock

from ai_peer_review.llm_clients.openai_client import OpenAIClient
from ai_peer_review.llm_clients.base_client import BaseLLMClient


class TestOpenAIClient:
    def test_openai_client_inheritance(self):
        # Verify that OpenAIClient inherits from BaseLLMClient
        assert issubclass(OpenAIClient, BaseLLMClient)
    
    @patch('ai_peer_review.llm_clients.openai_client.get_api_key')
    @patch('ai_peer_review.llm_clients.openai_client.OpenAI')
    def test_init_with_provided_api_key(self, mock_openai, mock_get_api_key):
        # Test initialization with a provided API key
        client = OpenAIClient(model="gpt-4o", api_key="test-key")
        
        # Check that get_api_key was not called
        mock_get_api_key.assert_not_called()
        
        # Check that OpenAI was initialized with the correct API key
        mock_openai.assert_called_once_with(api_key="test-key")
        
        # Check that the model was set correctly
        assert client.model == "gpt-4o"
        assert client.api_key == "test-key"
    
    @patch('ai_peer_review.llm_clients.openai_client.get_api_key')
    @patch('ai_peer_review.llm_clients.openai_client.OpenAI')
    def test_init_with_config_api_key(self, mock_openai, mock_get_api_key):
        # Mock get_api_key to return a predefined key
        mock_get_api_key.return_value = "config-key"
        
        # Test initialization without an API key
        client = OpenAIClient(model="gpt-4o")
        
        # Check that get_api_key was called with the correct key name
        mock_get_api_key.assert_called_once_with("openai")
        
        # Check that OpenAI was initialized with the correct API key
        mock_openai.assert_called_once_with(api_key="config-key")
        
        # Check that the model was set correctly
        assert client.model == "gpt-4o"
        assert client.api_key == "config-key"
    
    @patch('ai_peer_review.llm_clients.openai_client.get_api_key')
    def test_init_without_api_key(self, mock_get_api_key):
        # Mock get_api_key to return None (no API key available)
        mock_get_api_key.return_value = None
        
        # Test initialization without an API key should raise ValueError
        with pytest.raises(ValueError):
            OpenAIClient(model="gpt-4o")
    
    @patch('ai_peer_review.llm_clients.openai_client.get_api_key')
    @patch('ai_peer_review.llm_clients.openai_client.OpenAI')
    def test_generate(self, mock_openai, mock_get_api_key):
        # Mock get_api_key to return a predefined key
        mock_get_api_key.return_value = "test-key"
        
        # Mock the OpenAI client and response
        mock_openai_instance = MagicMock()
        mock_chat = MagicMock()
        mock_completions = MagicMock()
        mock_create = MagicMock()
        
        mock_openai_instance.chat = mock_chat
        mock_chat.completions = mock_completions
        mock_completions.create = mock_create
        
        # Mock the response
        mock_message = MagicMock()
        mock_message.content = "Generated response"
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        
        mock_create.return_value = mock_response
        
        # Set up the mock OpenAI class to return our mock instance
        mock_openai.return_value = mock_openai_instance
        
        # Create the client and generate a response
        client = OpenAIClient(model="gpt-4o")
        response = client.generate("Test prompt")
        
        # Check that completions.create was called with the correct arguments
        mock_create.assert_called_once_with(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a neuroscientist and expert in brain imaging."},
                {"role": "user", "content": "Test prompt"}
            ],
            temperature=0.1,
        )
        
        # Check that the response is correct
        assert response == "Generated response"