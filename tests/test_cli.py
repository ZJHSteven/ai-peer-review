import pytest
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from click.testing import CliRunner

from ai_peer_review.cli import cli, config, review, main
import ai_peer_review.review


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()
    
    def test_cli_version(self):
        # Test that the CLI version option works
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()
    
    @patch('ai_peer_review.cli.set_api_key')
    def test_config_command(self, mock_set_api_key):
        # Test the config command
        result = self.runner.invoke(cli, ["config", "openai", "test-key"])
        
        # Check that the command exited successfully
        assert result.exit_code == 0
        
        # Check that set_api_key was called with the correct arguments
        mock_set_api_key.assert_called_once_with("openai", "test-key")
        
        # Check that the output message is correct
        assert "API key for openai has been set successfully" in result.output
    
    @patch('ai_peer_review.review.extract_text_from_pdf')
    @patch('ai_peer_review.review.OpenAIClient')
    @patch('ai_peer_review.review.AnthropicClient')
    def test_review_command_no_meta(self, mock_anthropic, mock_openai, mock_extract_text):
        # Mock extract_text_from_pdf to return a dummy text
        mock_extract_text.return_value = "Dummy PDF content"
        
        # Mock the clients to return review content
        mock_client = MagicMock()
        mock_client.generate.return_value = "Review content"
        mock_openai.return_value = mock_client
        mock_anthropic.return_value = mock_client
            
        # Test the review command with --no-meta-review option
        with self.runner.isolated_filesystem():
            # Create a dummy PDF file
            with open("test.pdf", "w") as f:
                f.write("Dummy PDF content")
            
            # Run the command
            result = self.runner.invoke(cli, [
                "review", 
                "test.pdf", 
                "--no-meta-review",
                "--models", 
                "gpt4-o1,claude-3.7-sonnet"
            ])
            
            # Check that the command exited successfully
            assert result.exit_code == 0
            
            # Check that the output message contains expected information
            assert "Processing paper: test.pdf" in result.output
            assert "Selected models: gpt4-o1, claude-3.7-sonnet" in result.output
                
            # Check that the output directory "papers/test" was created
            assert os.path.exists("papers/test")
            
            # Check that the meta-review was not generated
            assert "Generating meta-review" not in result.output
            assert not os.path.exists("papers/test/meta_review.md")
            assert not os.path.exists("papers/test/results.json")
    
    @patch('ai_peer_review.review.extract_text_from_pdf')
    @patch('ai_peer_review.review.OpenAIClient')
    @patch('ai_peer_review.review.AnthropicClient')
    @patch('ai_peer_review.review.GoogleClient')
    def test_review_command_with_meta(self, mock_google, mock_anthropic, mock_openai, mock_extract_text):
        # Mock extract_text_from_pdf to return a dummy text
        mock_extract_text.return_value = "Dummy PDF content"
        
        # Mock the clients to return review content
        mock_client = MagicMock()
        mock_client.generate.return_value = "Review content"
        mock_openai.return_value = mock_client
        mock_anthropic.return_value = mock_client
        
        # Mock the meta-review client
        mock_meta_client = MagicMock()
        mock_meta_client.generate.return_value = "Meta-review content"
        mock_google.return_value = mock_meta_client
        
        # Test the review command with meta-review option
        with self.runner.isolated_filesystem():
            # Create a dummy PDF file
            with open("test.pdf", "w") as f:
                f.write("Dummy PDF content")
            
            # Run the command
            result = self.runner.invoke(cli, [
                "review", 
                "test.pdf",
                "--models", 
                "gpt4-o1,claude-3.7-sonnet"
            ])
            
            # Check that the command exited successfully
            assert result.exit_code == 0
            
            # Check that the output message contains expected information
            assert "Processing paper: test.pdf" in result.output
            assert "Selected models: gpt4-o1, claude-3.7-sonnet" in result.output
            assert "Generating meta-review" in result.output
            
            # Check that the output directory "papers/test" was created
            assert os.path.exists("papers/test")
            
            # Check that the review files and meta-review files were created
            assert os.path.exists("papers/test/meta_review.md")
            assert os.path.exists("papers/test/results.json")
            
            # Check the content of the results.json file
            with open("papers/test/results.json", "r") as f:
                results = json.load(f)
                assert "individual_reviews" in results
                assert "meta_review" in results
                assert "reviewer_to_model" in results
    
    def test_review_command_invalid_models(self):
        # Test the review command with invalid models
        with self.runner.isolated_filesystem():
            # Create a dummy PDF file
            with open("test.pdf", "w") as f:
                f.write("Dummy PDF content")
            
            # Run the command
            result = self.runner.invoke(cli, [
                "review", 
                "test.pdf", 
                "--models", 
                "invalid-model1,invalid-model2"
            ])
            
            # Check that the command exited successfully
            assert result.exit_code == 0
            
            # Check that the output message contains the expected error
            assert "No valid models specified" in result.output
    
    @patch('ai_peer_review.cli.cli')
    def test_main(self, mock_cli):
        # Test the main function
        main()
        
        # Check that cli was called
        mock_cli.assert_called_once()