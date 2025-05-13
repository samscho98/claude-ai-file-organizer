"""
Tests for token counter functionality.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.token_counter import (
    estimate_tokens,
    estimate_tokens_simple,
    estimate_file_tokens,
    estimate_filename_tokens,
    estimate_structure_tokens
)


class TestTokenCounter(unittest.TestCase):
    """Tests for the token counter functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Create test file
        self.test_file = os.path.join(self.test_dir, 'test_content.txt')
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write('This is a test file with some content for token counting.\n')
            f.write('It has multiple lines and some punctuation!\n')
            f.write('Testing 1, 2, 3...')
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test file
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_estimate_tokens_simple(self):
        """Test simple token estimation."""
        test_content = "This is a simple test sentence with 10 words."
        tokens = estimate_tokens_simple(test_content)
        
        # Simple approximation should give us roughly the word count plus some for punctuation
        self.assertGreaterEqual(tokens, 10)
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        test_content = "This is a test sentence."
        tokens = estimate_tokens(test_content)
        
        # Should return a positive number of tokens
        self.assertGreater(tokens, 0)
    
    def test_estimate_file_tokens(self):
        """Test file token estimation."""
        tokens = estimate_file_tokens(self.test_file)
        
        # File should have more than 10 tokens
        self.assertGreater(tokens, 10)
    
    def test_estimate_nonexistent_file(self):
        """Test estimation for nonexistent file."""
        tokens = estimate_file_tokens('nonexistent_file.txt')
        
        # Should return 0 for nonexistent file
        self.assertEqual(tokens, 0)
    
    def test_estimate_filename_tokens(self):
        """Test filename token estimation."""
        filename = "test_file_with_long_name.py"
        tokens = estimate_filename_tokens(filename)
        
        # Should be at least 1 and no more than 3
        self.assertGreaterEqual(tokens, 1)
        self.assertLessEqual(tokens, 3)
    
    def test_estimate_structure_tokens(self):
        """Test structure token estimation."""
        files_info = [
            {'path': 'file1.py'},
            {'path': 'dir/file2.py'},
            {'path': 'dir/subdir/file3.py'}
        ]
        
        tokens = estimate_structure_tokens(files_info)
        
        # Structure representation should have at least 3 tokens (one per file)
        self.assertGreaterEqual(tokens, 3)


if __name__ == '__main__':
    unittest.main()