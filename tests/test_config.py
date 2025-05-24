import os
import json
import tempfile
from unittest.mock import patch
import pytest
from pathlib import Path

from ai_peer_review.utils.config import (
    get_config_path, 
    load_config, 
    save_config, 
    get_api_key, 
    set_api_key,
    get_prompt,
    get_default_config
)


class TestConfig:
    @patch('ai_peer_review.utils.config.get_config_path')
    def test_load_config_existing(self, mock_get_config_path):
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump({"api_keys": {"openai": "test-key"}}, temp_file)
            temp_path = temp_file.name
        
        # Mock the config path to return our temporary file
        mock_get_config_path.return_value = Path(temp_path)
        
        # Load the config
        config = load_config()
        
        # Verify the config was loaded correctly
        assert config["api_keys"]["openai"] == "test-key"
        
        # Clean up
        os.unlink(temp_path)
    
    @patch('ai_peer_review.utils.config.get_config_path')
    def test_load_config_nonexistent(self, mock_get_config_path):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a path for a nonexistent file in the temporary directory
            temp_path = Path(temp_dir) / "config.json"
            
            # Mock the config path to return our nonexistent path
            mock_get_config_path.return_value = temp_path
            
            # Load the config, which should create a default config
            config = load_config()
            
            # Verify the default config was created
            assert "api_keys" in config
            assert isinstance(config["api_keys"], dict)
            
            # Verify the file was created
            assert os.path.exists(temp_path)
    
    @patch('ai_peer_review.utils.config.get_config_path')
    def test_save_config(self, mock_get_config_path):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a path for a config file in the temporary directory
            temp_path = Path(temp_dir) / "config.json"
            
            # Mock the config path to return our temporary path
            mock_get_config_path.return_value = temp_path
            
            # Create a config to save
            config = {"api_keys": {"openai": "test-key"}}
            
            # Save the config
            save_config(config)
            
            # Verify the config was saved correctly
            with open(temp_path, 'r') as f:
                saved_config = json.load(f)
            
            assert saved_config["api_keys"]["openai"] == "test-key"
    
    @patch('ai_peer_review.utils.config.load_config')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"})
    def test_get_api_key_from_env(self, mock_load_config):
        # Mock the load_config to return an empty config
        mock_load_config.return_value = {"api_keys": {}}
        
        # Get the API key
        key = get_api_key("openai")
        
        # Verify the key was retrieved from the environment
        assert key == "env-key"
    
    @patch('ai_peer_review.utils.config.load_config')
    @patch('ai_peer_review.utils.config.load_dotenv_file')
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_from_config(self, mock_load_dotenv, mock_load_config):
        # Mock the load_config to return a config with a key
        mock_load_config.return_value = {"api_keys": {"openai": "config-key"}}
        
        # Get the API key
        key = get_api_key("openai")
        
        # Verify the key was retrieved from the config
        assert key == "config-key"
    
    @patch('ai_peer_review.utils.config.load_config')
    @patch('ai_peer_review.utils.config.save_config')
    @patch.dict(os.environ, {}, clear=True)
    def test_set_api_key(self, mock_save_config, mock_load_config):
        # Mock the load_config to return an empty config
        mock_load_config.return_value = {"api_keys": {}}
        
        # Set the API key
        set_api_key("openai", "new-key")
        
        # Verify the save_config was called with the updated config
        expected_config = {"api_keys": {"openai": "new-key"}}
        # save_config is called with config and config_path
        mock_save_config.assert_called_once()
    
    def test_get_default_config(self):
        """Test that the default configuration contains expected sections and values."""
        default_config = get_default_config()
        
        # Check the structure of the default config
        assert "api_keys" in default_config
        assert "prompts" in default_config
        
        # Check that the prompts section contains expected prompts
        prompts = default_config["prompts"]
        assert "system" in prompts
        assert "review" in prompts
        assert "metareview" in prompts
        assert "concerns_extraction" in prompts
        
        # Check the content of a specific prompt
        assert "neuroscientist and expert in brain imaging" in prompts["system"]
        assert "{paper_text}" in prompts["review"]
    
    @patch('ai_peer_review.utils.config.load_config')
    def test_get_prompt_existing(self, mock_load_config):
        """Test getting an existing prompt."""
        # Mock the load_config to return a config with prompts
        mock_load_config.return_value = {
            "prompts": {
                "system": "Test system prompt",
                "review": "Test review prompt"
            }
        }
        
        # Get an existing prompt
        prompt = get_prompt("system")
        
        # Verify the prompt was retrieved correctly
        assert prompt == "Test system prompt"
    
    @patch('ai_peer_review.utils.config.load_config')
    def test_get_prompt_nonexistent(self, mock_load_config):
        """Test getting a nonexistent prompt."""
        # Mock the load_config to return a config with prompts
        mock_load_config.return_value = {
            "prompts": {
                "system": "Test system prompt"
            }
        }
        
        # Get a nonexistent prompt
        prompt = get_prompt("nonexistent")
        
        # Verify an empty string is returned
        assert prompt == ""
    
    @patch('ai_peer_review.utils.config.load_config')
    def test_get_prompt_no_prompts_section(self, mock_load_config):
        """Test getting a prompt when the prompts section doesn't exist."""
        # Mock the load_config to return a config without prompts
        mock_load_config.return_value = {"api_keys": {}}
        
        # Get a prompt
        prompt = get_prompt("system")
        
        # Verify an empty string is returned
        assert prompt == ""
        
    def test_get_config_path_with_custom_path(self):
        """Test that get_config_path returns the custom path when provided."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = os.path.join(temp_dir, "custom_config.json")
            
            # Get the config path with the custom path
            config_path = get_config_path(custom_path)
            
            # Verify the config path is the custom path
            assert str(config_path) == custom_path
            
            # Verify that the parent directory was created
            assert os.path.exists(os.path.dirname(custom_path))
    
    def test_load_config_with_custom_path(self):
        """Test loading config from a custom path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a custom config file
            custom_path = os.path.join(temp_dir, "custom_config.json")
            custom_config = {
                "api_keys": {"test_service": "test_key"},
                "prompts": {"test_prompt": "This is a test prompt"}
            }
            
            with open(custom_path, "w") as f:
                json.dump(custom_config, f)
            
            # Load the config from the custom path
            config = load_config(custom_path)
            
            # Verify the config was loaded correctly
            assert config["api_keys"]["test_service"] == "test_key"
            assert config["prompts"]["test_prompt"] == "This is a test prompt"
    
    def test_get_prompt_with_custom_path(self):
        """Test getting a prompt from a custom config path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a custom config file
            custom_path = os.path.join(temp_dir, "custom_config.json")
            custom_config = {
                "prompts": {"custom_prompt": "This is a custom prompt"}
            }
            
            with open(custom_path, "w") as f:
                json.dump(custom_config, f)
            
            # Get the prompt from the custom config path
            prompt = get_prompt("custom_prompt", custom_path)
            
            # Verify the prompt was retrieved correctly
            assert prompt == "This is a custom prompt"