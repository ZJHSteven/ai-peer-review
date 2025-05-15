import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_dotenv_file() -> None:
    """Load environment variables from .env file."""
    # Load from .env file in the current directory
    load_dotenv()
    
    # Also try loading from config directory
    config_dir = Path.home() / ".ai-peer-review"
    env_path = config_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    config_dir = Path.home() / ".ai-peer-review"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def load_config() -> Dict[str, Any]:
    """Load configuration from file, or create default if it doesn't exist."""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            # If config file is invalid, return default config
            return {"api_keys": {}}
    else:
        # Create default config
        default_config = {"api_keys": {}}
        save_config(default_config)
        return default_config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key(key_name: str) -> Optional[str]:
    """
    Get API key from .env file, environment variable, or configuration file.
    
    Args:
        key_name: Name of the API key (e.g., 'openai', 'anthropic')
        
    Returns:
        API key if found, None otherwise
    """
    # Make sure .env variables are loaded
    load_dotenv_file()
    
    # Try environment variable
    env_var_name = f"{key_name.upper()}_API_KEY"
    if env_var_name in os.environ:
        return os.environ[env_var_name]
    
    # Then try config file
    config = load_config()
    return config.get("api_keys", {}).get(key_name)


def set_api_key(key_name: str, api_key: str) -> None:
    """
    Set API key in configuration file.
    
    Args:
        key_name: Name of the API key (e.g., 'openai', 'anthropic')
        api_key: API key value
    """
    config = load_config()
    
    if "api_keys" not in config:
        config["api_keys"] = {}
    
    config["api_keys"][key_name] = api_key
    save_config(config)