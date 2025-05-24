import pytest
from unittest.mock import patch, MagicMock
import random

from ai_peer_review.review import (
    get_review_prompt,
    get_metareview_prompt,
    process_paper,
    generate_meta_review
)


class TestReview:
    def test_get_review_prompt(self):
        # Test with a sample paper text
        paper_text = "This is a sample paper about neuroscience."
        prompt = get_review_prompt(paper_text)
        
        # Check that the prompt contains the paper text
        assert paper_text in prompt
        
        # Check that the prompt contains the required instructions
        assert "neuroscientist and expert in brain imaging" in prompt
        assert "provide a thorough and critical review" in prompt
        assert "summary of the study" in prompt
        assert "point-by-point analysis" in prompt
    
    def test_get_metareview_prompt(self):
        # Test with sample reviews
        reviews = ["Review 1 content", "Review 2 content"]
        prompt = get_metareview_prompt(reviews)
        
        # Check that the prompt contains all reviews with NATO names
        assert "Review from alfa:\n\nReview 1 content" in prompt
        assert "Review from bravo:\n\nReview 2 content" in prompt
        
        # Check that the prompt contains the required instructions
        assert "meta-review" in prompt
        assert "common points" in prompt
        assert "specific concerns" in prompt
        assert "CONCERNS_TABLE_DATA" in prompt
    
    @patch('ai_peer_review.review.extract_text_from_pdf')
    @patch('ai_peer_review.review.OpenAIClient')
    @patch('ai_peer_review.review.AnthropicClient')
    def test_process_paper(self, mock_anthropic, mock_openai, mock_extract_text):
        # Mock the extract_text_from_pdf function
        mock_extract_text.return_value = "Paper content"
        
        # Mock the LLM clients
        mock_openai_instance = MagicMock()
        mock_openai_instance.generate.return_value = "OpenAI review"
        mock_openai.return_value = mock_openai_instance
        
        mock_anthropic_instance = MagicMock()
        mock_anthropic_instance.generate.return_value = "Anthropic review"
        mock_anthropic.return_value = mock_anthropic_instance
        
        # Test with a subset of models
        models = ["gpt4-o1", "claude-3.7-sonnet"]
        reviews = process_paper("test.pdf", models)
        
        # Check that the extract_text_from_pdf function was called
        mock_extract_text.assert_called_once_with("test.pdf")
        
        # Check that the OpenAI client was initialized with the correct model
        mock_openai.assert_called_once_with(model="gpt-4o")
        
        # Check that the Anthropic client was initialized with the correct model
        mock_anthropic.assert_called_once_with(model="claude-3-sonnet-20240229")
        
        # Check that the generate methods were called
        mock_openai_instance.generate.assert_called_once()
        mock_anthropic_instance.generate.assert_called_once()
        
        # Check that the reviews dictionary contains the expected models
        assert set(reviews.keys()) == {"gpt4-o1", "claude-3.7-sonnet"}
        assert reviews["gpt4-o1"] == "OpenAI review"
        assert reviews["claude-3.7-sonnet"] == "Anthropic review"
    
    @patch('ai_peer_review.review.GoogleClient')
    @patch('ai_peer_review.review.random.shuffle')
    def test_generate_meta_review(self, mock_shuffle, mock_google):
        # Mock the random.shuffle function to maintain order for predictable testing
        mock_shuffle.side_effect = lambda x: x
        
        # Mock the Google client
        mock_google_instance = MagicMock()
        mock_google_instance.generate.return_value = "Meta-review content"
        mock_google.return_value = mock_google_instance
        
        # Test with sample reviews
        reviews = {
            "model1": "Review 1 content",
            "model2": "Review 2 content"
        }
        
        meta_review, ratings = generate_meta_review(reviews)
        
        # Check that the Google client was initialized with the correct model
        mock_google.assert_called_once_with(model="gemini-2.5-pro-preview-05-06")
        
        # Check that the generate method was called
        mock_google_instance.generate.assert_called_once()
        
        # Check that the meta_review contains the expected content
        assert meta_review == "Meta-review content"
        
        # Check that NATO-to-model mapping was created
        assert len(ratings) == 2
        assert set(ratings.values()) == {"model1", "model2"}