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
    set_api_key
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
        mock_save_config.assert_called_once_with(expected_config)