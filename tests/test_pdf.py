import os
import pytest
from pathlib import Path

from ai_peer_review.utils.pdf import extract_text_from_pdf


class TestPDF:
    def test_extract_text_from_pdf(self):
        # Get the path to the test PDF
        test_dir = Path(__file__).parent
        test_pdf = test_dir / "test_data" / "sample_paper.pdf"
        
        # Extract text from the PDF
        text = extract_text_from_pdf(str(test_pdf))
        
        # Verify that we got some text
        assert len(text) > 0
        
        # Check for expected content in the text
        assert "mu-opioid" in text.lower()
        assert "music" in text.lower()
    
    def test_extract_text_from_nonexistent_pdf(self):
        # Try to extract text from a nonexistent PDF
        with pytest.raises(FileNotFoundError):
            extract_text_from_pdf("/nonexistent/path/to/file.pdf")
    
    def test_extract_text_from_invalid_pdf(self):
        # Create a temporary invalid PDF
        test_dir = Path(__file__).parent
        invalid_pdf = test_dir / "test_data" / "invalid.pdf"
        
        try:
            # Create an empty file
            with open(invalid_pdf, 'w') as f:
                f.write("This is not a PDF file")
            
            # Try to extract text from an invalid PDF
            with pytest.raises(Exception):
                extract_text_from_pdf(str(invalid_pdf))
        finally:
            # Clean up
            if os.path.exists(invalid_pdf):
                os.remove(invalid_pdf)