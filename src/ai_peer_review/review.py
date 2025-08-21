import os
import re
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import json
import random
import pandas as pd

from .utils.pdf import extract_text_from_pdf
from .utils.config import get_prompt
from .llm_clients.openai_client import OpenAIClient


def get_review_prompt(paper_text: str, config_file: Optional[str] = None) -> str:
    """
    生成同行评审的提示词。
    
    Args:
        paper_text: 待评审论文的文本内容
        config_file: 可选的自定义配置文件路径
    
    Returns:
        格式化后的提示词字符串
    """
    prompt_template = get_prompt("review", config_file)
    if not prompt_template:
        # Fallback to hardcoded prompt if not found in config
        prompt_template = (
            "你是一位神经科学家和脑成像领域的专家，应邀对一篇提交的研究论文进行同行评审。"
            " 请对论文进行全面且批判性的评审。首先简要总结研究及其结果，" 
            "然后逐条详细分析研究中存在的任何缺陷或问题。\n\n"
            "待评审论文如下：\n\n{paper_text}"
        )
    
    return prompt_template.format(paper_text=paper_text)


def get_metareview_prompt(reviews: List[str], config_file: Optional[str] = None) -> str:
    """
    生成元评审的提示词。
    
    Args:
        reviews: 评审文本列表
        config_file: 可选的自定义配置文件路径
        
    Returns:
        格式化后的元评审提示词
    """
    # NATO phonetic alphabet for reviewers
    nato_names = ["alfa", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
    
    # Build reviews text with NATO phonetic names
    reviews_text = ""
    for i, review in enumerate(reviews):
        reviewer_name = nato_names[i] if i < len(nato_names) else f"reviewer_{i+1}"
        reviews_text += f"Review from {reviewer_name}:\n\n{review}\n\n"
    
    # Get prompt template from config
    prompt_template = get_prompt("metareview", config_file)
    if not prompt_template:
        # Fallback to hardcoded prompt if not found in config
        prompt_template = (
            "附带文件包含对一篇研究文章的多份同行评审。请将这些评审汇总为一份元评审（meta-review），" 
            "同时突出各评审者普遍提出的观点以及仅由部分评审者提出的具体担忧。在元评审中，列出任何评审者提出的所有主要问题。" 
            "完成元评审后，添加一个标题为 'CONCERNS_TABLE_DATA' 的部分，在该部分中提供一个 JSON 对象来表示关注问题的表格。" 
            "每一行应当表示一个独立的关注点，每一列对应一个评审者。请使用以下格式：\n\n"
            "```json\n"
            "{{\n"
            "  \"concerns\": [\n"
            "    {{\n"
            "      \"concern\": \"对关注点1的简要描述\",\n"
            "      \"alfa\": true/false,\n"
            "      \"bravo\": true/false,\n"
            "      ...\n"
            "    }},\n"
            "    ...\n"
            "  ]\n"
            "}}\n"
            "```\n\n"
            "在整份元评审中，请使用分配给评审者的北约音标名称引用他们（例如：alfa、bravo、charlie）。\n\n"
            "{reviews_text}"
        )
    
    return prompt_template.format(reviews_text=reviews_text)


def process_paper(pdf_path: str, models: List[str], config_file: Optional[str] = None) -> Dict[str, str]:
    """
    处理论文并使用多个大语言模型生成评审。
    
    Args:
        pdf_path: PDF文件路径
        models: 用于评审的模型名称列表
        config_file: 可选的自定义配置文件路径
        
    Returns:
        模型名称到评审文本的字典映射
    """
    # Extract text from PDF
    paper_text = extract_text_from_pdf(pdf_path)
    
    # Generate the review prompt
    prompt = get_review_prompt(paper_text, config_file)
    
    # Get reviews from each LLM
    reviews = {}
    for model_name in models:
        try:
            # Create a unified client that can handle any model
            client = OpenAIClient(model=model_name)
            reviews[model_name] = client.generate(prompt)
        except Exception as e:
            print(f"Error generating review with model {model_name}: {e}")
            reviews[model_name] = f"Error: Failed to generate review - {str(e)}"
    
    return reviews


def extract_concerns_table(meta_review_text: str) -> Optional[Dict]:
    """从元评审文本中提取JSON格式的关注问题表格。"""
    # Look for JSON data between CONCERNS_TABLE_DATA section and the end of a JSON block
    pattern = r'CONCERNS_TABLE_DATA.*?```json\s*(.*?)\s*```'
    match = re.search(pattern, meta_review_text, re.DOTALL)
    
    if not match:
        # Try without the json tag in case the model formatted it differently
        pattern = r'CONCERNS_TABLE_DATA.*?```\s*(.*?)\s*```'
        match = re.search(pattern, meta_review_text, re.DOTALL)
    
    if not match:
        # Try finding a JSON object with "concerns" key anywhere in the text
        pattern = r'\{\s*"concerns"\s*:\s*\[.*?\]\s*\}'
        match = re.search(pattern, meta_review_text, re.DOTALL)
    
    if match:
        try:
            json_str = match.group(1)
            # Remove the CONCERNS_TABLE_DATA header if it's still there
            json_str = re.sub(r'CONCERNS_TABLE_DATA.*?{', '{', json_str, flags=re.DOTALL)
            return json.loads(json_str)
        except json.JSONDecodeError:
            print("Error parsing JSON data from meta-review")
            return None
    return None


def generate_meta_review(reviews: Dict[str, str], config_file: Optional[str] = None) -> Tuple[str, Dict[str, str]]:
    """
    生成所有评审的元评审。
    
    Args:
        reviews: 模型名称到评审文本的字典映射
        config_file: 可选的自定义配置文件路径
        
    Returns:
        元评审文本和NATO代码到模型名称映射的元组
    """
    # NATO phonetic alphabet for reviewers
    nato_names = ["alfa", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet"]
    
    # Get list of models in a fixed order
    models_list = list(reviews.keys())
    
    # Remove LLM identifiers but maintain order for mapping
    anonymized_reviews = [reviews[model] for model in models_list]
    
    # Create mapping of NATO name to model name
    nato_to_model = {nato_names[i]: model for i, model in enumerate(models_list) if i < len(nato_names)}
    # Handle any extras if we have more than 10 models
    for i, model in enumerate(models_list[len(nato_names):], len(nato_names)):
        nato_to_model[f"reviewer_{i+1}"] = model
    
    # Generate meta-review prompt
    prompt = get_metareview_prompt(anonymized_reviews, config_file)
    
    # Use a unified client for meta-review (can use any model, defaulting to a good one)
    meta_reviewer = OpenAIClient(model="gpt-4o")  # You can change this to any model you prefer
    meta_review_text = meta_reviewer.generate(prompt)
    
    # Filter out the CONCERNS_TABLE_DATA section from the meta-review
    clean_meta_review = re.sub(r'CONCERNS_TABLE_DATA.*', '', meta_review_text, flags=re.DOTALL)
    
    return clean_meta_review, nato_to_model


def save_concerns_as_csv(meta_review_text: str, output_path: Path) -> bool:
    """从元评审中提取关注问题并保存为CSV格式。"""
    concerns_data = extract_concerns_table(meta_review_text)
    
    if not concerns_data or "concerns" not in concerns_data:
        print("No valid concerns table found in meta-review")
        return False
    
    # Convert to DataFrame
    df = pd.DataFrame(concerns_data["concerns"])
    
    # Save to CSV
    csv_path = output_path / "concerns_table.csv"
    df.to_csv(csv_path, index=False)
    print(f"Concerns table saved to {csv_path}")
    return True