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
from .llm_clients.anthropic_client import AnthropicClient
from .llm_clients.google_client import GoogleClient
from .llm_clients.deepseek_client import DeepSeekClient
from .llm_clients.llama_client import LlamaClient


def get_review_prompt(paper_text: str, config_file: Optional[str] = None) -> str:
    """
    Generate the prompt for peer review.
    
    Args:
        paper_text: The text of the paper to review
        config_file: Optional path to a custom config file
    
    Returns:
        The formatted prompt string
    """
    prompt_template = get_prompt("review", config_file)
    if not prompt_template:
        # Fallback to hardcoded prompt if not found in config
        prompt_template = (
            "You are a neuroscientist and expert in brain imaging who has been asked to provide "
            "a peer review for a submitted research paper, which is attached here. "
            "Please provide a thorough and critical review of the paper. "
            "First provide a summary of the study and its results, and then provide "
            "a detailed point-by-point analysis of any flaws in the study.\n\n"
            "Here is the paper to review:\n\n{paper_text}"
        )
    
    return prompt_template.format(paper_text=paper_text)


def get_metareview_prompt(reviews: List[str], config_file: Optional[str] = None) -> str:
    """
    Generate the prompt for meta-review.
    
    Args:
        reviews: List of review texts
        config_file: Optional path to a custom config file
        
    Returns:
        The formatted meta-review prompt
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
        )
    
    return prompt_template.format(reviews_text=reviews_text)


def process_paper(pdf_path: str, models: List[str], config_file: Optional[str] = None) -> Dict[str, str]:
    """
    Process a paper and generate reviews using multiple LLMs.
    
    Args:
        pdf_path: Path to the PDF file to process
        models: List of model names to use for reviews
        config_file: Optional path to a custom config file
        
    Returns:
        Dictionary mapping model names to their review texts
    """
    # Extract text from PDF
    paper_text = extract_text_from_pdf(pdf_path)
    
    # Generate the review prompt
    prompt = get_review_prompt(paper_text, config_file)
    
    # Define client factories for each model
    client_factories = {
        "gpt4-o1": lambda: OpenAIClient(model="gpt-4o"),
        "gpt4-o3-mini": lambda: OpenAIClient(model="gpt-4o-mini"),
        "claude-3.7-sonnet": lambda: AnthropicClient(model="claude-3-sonnet-20240229"),
        "gemini-2.5-pro": lambda: GoogleClient(model="gemini-2.5-pro-preview-05-06"),
        "deepseek-r1": lambda: DeepSeekClient(model="deepseek-r1"),
        "llama-4-maverick": lambda: LlamaClient(model="llama-4-maverick")
    }
    
    # Get reviews from each LLM
    reviews = {}
    for model_name in models:
        if model_name in client_factories:
            # Only initialize the client if the model is requested
            client = client_factories[model_name]()
            reviews[model_name] = client.generate(prompt)
    
    return reviews


def extract_concerns_table(meta_review_text: str) -> Optional[Dict]:
    """Extract the JSON concerns table from the meta-review text."""
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
    Generate a meta-review of all reviews.
    
    Args:
        reviews: Dictionary mapping model names to their review texts
        config_file: Optional path to a custom config file
        
    Returns:
        Tuple of (meta-review text, NATO-to-model mapping)
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
    
    # Use Google Gemini for meta-review
    meta_reviewer = GoogleClient(model="gemini-2.5-pro-preview-05-06")
    meta_review_text = meta_reviewer.generate(prompt)
    
    # Filter out the CONCERNS_TABLE_DATA section from the meta-review
    clean_meta_review = re.sub(r'CONCERNS_TABLE_DATA.*', '', meta_review_text, flags=re.DOTALL)
    
    return clean_meta_review, nato_to_model


def save_concerns_as_csv(meta_review_text: str, output_path: Path) -> bool:
    """Extract concerns from meta-review and save as CSV."""
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