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
        # 默认使用学位与研究生教育期刊的审稿标准
        prompt_template = (
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
        # 默认使用学位与研究生教育期刊的元评审标准
        prompt_template = (
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
            print(f"Generating review with model: {model_name}")
            # Create a unified client that can handle any model
            client = OpenAIClient(model=model_name)
            review_text = client.generate(prompt)
            
            # 检查生成的内容长度
            if len(review_text) < 100:
                print(f"Warning: Review from {model_name} is unusually short ({len(review_text)} characters)")
            
            # 检查是否被截断（简单的启发式检查）
            if not any(keyword in review_text.lower() for keyword in ['结论', '建议', '总结', '最终', '综上']):
                print(f"Warning: Review from {model_name} may be incomplete (no conclusion keywords found)")
            
            reviews[model_name] = review_text
            print(f"Successfully generated review with {model_name} ({len(review_text)} characters)")
            
        except Exception as e:
            error_msg = f"Error: Failed to generate review - {str(e)}"
            print(f"Error generating review with model {model_name}: {e}")
            reviews[model_name] = error_msg
    
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
    try:
        print("Generating meta-review...")
        meta_reviewer = OpenAIClient(model="gemini-2.5-pro")  # You can change this to any model you prefer
        meta_review_text = meta_reviewer.generate(prompt)
        
        # 检查meta-review的完整性
        if len(meta_review_text) < 200:
            print(f"Warning: Meta-review is unusually short ({len(meta_review_text)} characters)")
        
        print(f"Successfully generated meta-review ({len(meta_review_text)} characters)")
        
    except Exception as e:
        print(f"Error generating meta-review: {e}")
        meta_review_text = f"Error generating meta-review: {str(e)}"
    
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