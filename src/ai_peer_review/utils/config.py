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
            "system": "您是一位学位与研究生教育领域的资深专家，具有丰富的学术评审经验。",
            "review": (
                "您是一位学位与研究生教育领域的资深专家和期刊审稿人，现需要对投稿至《学位与研究生教育》期刊的论文进行同行评审。\n\n"
                "请根据《学位与研究生教育》期刊的办刊宗旨和要求进行评审：\n\n"
                "【期刊定位与要求】\n"
                "- 本刊宗旨：为学位制度建设和研究生教育事业服务\n"
                "- 内容特色：集工作指导、理论研究、经验介绍和信息传播于一身\n"
                "- 主要栏目：专题研究、学术探索、导师论坛、研究生培养、研究生教学、研究生管理、研究生德育、招生与就业、评估与质量保障、学科建设与发展、比较与借鉴等\n\n"
                "【审稿评估标准】\n"
                "请从以下维度进行评审：\n\n"
                "1. **选题价值与期刊契合度**\n"
                "   - 是否围绕研究生教育和学位工作中迫切需要解决的问题\n"
                "   - 是否符合期刊服务学位制度建设和研究生教育事业的宗旨\n"
                "   - 选题是否具有理论意义和实践价值\n\n"
                "2. **学术质量与创新性**\n"
                "   - 理论联系实际程度如何\n"
                "   - 是否有鲜明的思想观点和新意\n"
                "   - 是否运用新思想、新理论和新方法研究现实问题\n"
                "   - 研究成果和经验的实用性\n\n"
                "3. **学术规范性**\n"
                "   - 是否遵守学术规范，无抄袭、一稿多投等问题\n"
                "   - 引用资料是否为第一手资料\n"
                "   - 数据、案例、引用资料及参考文献是否真实有效、路径清晰可查\n"
                "   - 参考文献格式是否符合GB/T7714-2015标准\n\n"
                "4. **写作质量与规范**\n"
                "   - 文风是否开门见山、简洁明快\n"
                "   - 篇幅是否控制在10000汉字以内\n"
                "   - 是否包含中文摘要（300-500字）、关键词（3-5个）、作者简介等必要要素\n"
                "   - 结构层次是否清晰\n\n"
                "5. **研究方法与论证**\n"
                "   - 研究方法是否科学合理\n"
                "   - 论证是否严密、逻辑清晰\n"
                "   - 结论是否有充分的论据支撑\n\n"
                "【评审要求】\n"
                "请提供详细的评审意见：\n"
                "1. 首先简要总结论文的研究主题、主要内容和结论\n"
                "2. 逐项分析论文在上述各维度的表现\n"
                "3. 指出论文的优点和创新之处\n"
                "4. 详细列出存在的问题和不足\n"
                "5. 提出具体的修改建议\n"
                "6. 给出明确的审稿结论建议（接受/修改后接受/修改后重审/拒稿）\n\n"
                "待评审论文如下：\n\n{paper_text}"
            ),
            "metareview": (
                "您是《学位与研究生教育》期刊的资深编辑，需要对一篇投稿论文的多份同行评审意见进行汇总分析，形成元评审报告。\n\n"
                "【元评审任务】\n"
                "请基于各位专家的评审意见，撰写综合性的元评审报告：\n\n"
                "1. **评审意见概述**\n"
                "   - 总结各评审专家的主要观点\n"
                "   - 突出评审专家普遍认同的观点\n"
                "   - 识别仅由部分评审专家提出的特定关注点\n\n"
                "2. **问题汇总分析**\n"
                "   - 系统梳理所有评审专家提出的主要问题\n"
                "   - 按问题的重要性和紧迫性进行分类\n"
                "   - 分析问题的共性和差异性\n\n"
                "3. **期刊标准对照**\n"
                "   根据《学位与研究生教育》期刊要求，重点关注：\n"
                "   - 是否符合期刊办刊宗旨和栏目定位\n"
                "   - 学术质量是否达到期刊标准\n"
                "   - 是否遵守学术规范\n"
                "   - 写作规范是否符合期刊要求\n\n"
                "4. **编辑决策建议**\n"
                "   基于综合分析，提出明确的编辑决策建议\n\n"
                "【格式要求】\n"
                "在元评审报告末尾，请添加标题为'CONCERNS_TABLE_DATA'的部分，提供JSON格式的关注问题汇总表：\n\n"
                "```json\n"
                "{{\n"
                "  \"concerns\": [\n"
                "    {{\n"
                "      \"concern\": \"具体关注问题的简要描述\",\n"
                "      \"alfa\": true/false,\n"
                "      \"bravo\": true/false,\n"
                "      \"charlie\": true/false,\n"
                "      \"delta\": true/false,\n"
                "      \"echo\": true/false\n"
                "    }}\n"
                "  ]\n"
                "}}\n"
                "```\n\n"
                "请在整份元评审中使用北约音标字母（alfa、bravo、charlie等）来指代各位评审专家。\n\n"
                "各评审专家的意见如下：\n\n"
                "{reviews_text}"
            ),
            "concerns_extraction": (
                "基于元评审报告，请提取《学位与研究生教育》期刊审稿中识别的所有主要关注问题。\n\n"
                "请创建一个JSON对象，包含'concerns'数组。每个关注问题对象应包含：\n"
                "1. 'concern'字段：问题的简要描述\n"
                "2. 各评审模型对应字段：{model_names}\n"
                "3. 每个模型字段为true（如果该模型识别了此问题）或false（如果未识别）\n\n"
                "示例结构：\n"
                "{{\n"
                "  \"concerns\": [\n"
                "    {{\n"
                "      \"concern\": \"问题1的简要描述\",\n"
                "      \"{first_model}\": true,\n"
                "      \"{second_model}\": false\n"
                "    }}\n"
                "  ]\n"
                "}}\n\n"
                "请仅返回有效的JSON格式，无需其他说明。\n\n"
                "元评审报告：\n{meta_review_text}\n\n"
                "模型名称映射（供参考）：\n{model_mapping}"
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