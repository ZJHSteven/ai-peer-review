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


def get_config_path(custom_path: Optional[str] = None) -> Path:
    """
    Get the path to the configuration file.
    
    Args:
        custom_path: Optional custom path to the config file
        
    Returns:
        Path to the configuration file
    """
    if custom_path:
        config_path = Path(custom_path)
        # Create parent directory if it doesn't exist
        config_path.parent.mkdir(exist_ok=True, parents=True)
        return config_path
    
    # Default path
    config_dir = Path.home() / ".ai-peer-review"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"


def get_default_config() -> Dict[str, Any]:
    """Return the default configuration."""
    return {
        "api_keys": {},
        "prompts": {
            "system": "You are a neuroscientist and expert in brain imaging.",
            "review": (
                "You are a neuroscientist and expert in brain imaging who has been asked to provide "
                "a peer review for a submitted research paper, which is attached here. "
                "Please provide a thorough and critical review of the paper. "
                "First provide a summary of the study and its results, and then provide "
                "a detailed point-by-point analysis of any flaws in the study.\n\n"
                "Here is the paper to review:\n\n{paper_text}"
            ),
            "metareview": (
                "The attached files contain peer reviews of a research article. "
                "Please summarize these into a meta-review, highlighting both the common points "
                "raised across reviewers as well as any specific concerns that were only raised "
                "by some reviewers. In your meta-review, identify all major concerns raised by any reviewer. "
                "After your meta-review, include a section titled 'CONCERNS_TABLE_DATA' where you provide a JSON object "
                "representing a table of concerns. Each row should be a distinct concern, with columns for each reviewer. "
                "Use the following format: \n\n"
                "```json\n"
                "{{\n"
                "  \"concerns\": [\n"
                "    {{\n"
                "      \"concern\": \"Brief description of concern 1\",\n"
                "      \"alfa\": true/false,\n"
                "      \"bravo\": true/false,\n"
                "      ...\n"
                "    }},\n"
                "    ...\n"
                "  ]\n"
                "}}\n"
                "```\n\n"
                "Refer to each of the reviewers using their assigned NATO phonetic alphabet name "
                "(e.g., alfa, bravo, charlie) throughout your meta-review.\n\n"
                "{reviews_text}"
            ),
            "concerns_extraction": (
                "Based on the meta-review, extract all major concerns identified by reviewers.\n\n"
                "Create a JSON object with a 'concerns' array. Each concern object should have:\n"
                "1. A 'concern' field with a brief description\n"
                "2. One field for each model: {model_names}\n"
                "3. Each model field should be true if that model identified the concern, false otherwise\n\n"
                "Example structure:\n"
                "{{\n"
                "  \"concerns\": [\n"
                "    {{\n"
                "      \"concern\": \"Brief description of concern 1\",\n"
                "      \"{first_model}\": true,\n"
                "      \"{second_model}\": false,\n"
                "      ...\n"
                "    }},\n"
                "    ...\n"
                "  ]\n"
                "}}\n\n"
                "Return only valid JSON without any explanation.\n\n"
                "Meta-review:\n{meta_review_text}\n\n"
                "Model name mapping (for reference):\n{model_mapping}"
            )
        }
    }

def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file, or create default if it doesn't exist.
    
    Args:
        config_file: Optional path to a custom config file
        
    Returns:
        The loaded configuration dictionary
    """
    config_path = get_config_path(config_file)
    
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            
            # Update with any missing default sections
            default_config = get_default_config()
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            
            return config
        except json.JSONDecodeError:
            # If config file is invalid, return default config
            return get_default_config()
    else:
        # Create default config
        default_config = get_default_config()
        save_config(default_config, config_path)
        return default_config


def save_config(config: Dict[str, Any], config_path: Optional[Path] = None) -> None:
    """
    Save configuration to file.
    
    Args:
        config: The configuration dictionary to save
        config_path: Optional explicit path to save to (otherwise uses default path)
    """
    if config_path is None:
        config_path = get_config_path()
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key(key_name: str, config_file: Optional[str] = None) -> Optional[str]:
    """
    Get API key from .env file, environment variable, or configuration file.
    
    Args:
        key_name: Name of the API key (e.g., 'openai', 'anthropic')
        config_file: Optional path to a custom config file
        
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
    config = load_config(config_file)
    return config.get("api_keys", {}).get(key_name)


def set_api_key(key_name: str, api_key: str, config_file: Optional[str] = None) -> None:
    """
    Set API key in configuration file.
    
    Args:
        key_name: Name of the API key (e.g., 'openai', 'anthropic')
        api_key: API key value
        config_file: Optional path to a custom config file
    """
    config = load_config(config_file)
    config_path = get_config_path(config_file)
    
    if "api_keys" not in config:
        config["api_keys"] = {}
    
    config["api_keys"][key_name] = api_key
    save_config(config, config_path)


def get_prompt(prompt_name: str, config_file: Optional[str] = None) -> str:
    """
    Get a prompt from the configuration file.
    
    Args:
        prompt_name: Name of the prompt (e.g., 'system', 'review', 'metareview')
        config_file: Optional path to a custom config file
        
    Returns:
        Prompt template string if found, empty string otherwise
    """
    config = load_config(config_file)
    return config.get("prompts", {}).get(prompt_name, "")