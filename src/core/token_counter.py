"""
Token counting functionality for Claude AI File Organizer.
"""

import os
import re


def has_tiktoken():
    """Check if tiktoken is available."""
    try:
        import importlib.util
        spec = importlib.util.find_spec("tiktoken")
        return spec is not None
    except ImportError:
        return False


def estimate_tokens_tiktoken(content):
    """
    Estimate tokens using tiktoken library (more accurate).
    
    Args:
        content (str): Text content to estimate tokens for
        
    Returns:
        int: Estimated token count
    """
    try:
        # Import tiktoken only when the function is called and only if it's available
        import tiktoken
        
        # Use Claude's encoding (cl100k_base is close to Claude's tokenizer)
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(content))
        except Exception:
            # Fall back to simpler encoding if cl100k_base not available
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(content))
    except ImportError:
        # If import fails, fall back to the simple method
        return estimate_tokens_simple(content)


def estimate_tokens_simple(content):
    """
    Estimate tokens using a simple approximation.
    
    This is a fallback method when tiktoken is not available.
    Roughly estimates tokens as 4 characters per token.
    
    Args:
        content (str): Text content to estimate tokens for
        
    Returns:
        int: Estimated token count
    """
    # Simple token estimation by splitting on whitespace and punctuation
    tokens = re.findall(r'\w+|[^\w\s]', content)
    
    # Count special tokens
    code_blocks = len(re.findall(r'```', content))
    special_chars = len(re.findall(r'[^\w\s]', content))
    
    # Approximate calculation
    return len(tokens) + code_blocks + (special_chars // 2)


def estimate_tokens(content):
    """
    Estimate the number of tokens in the given content.
    
    Args:
        content (str): Text content to estimate tokens for
        
    Returns:
        int: Estimated token count
    """
    if has_tiktoken():
        return estimate_tokens_tiktoken(content)
    else:
        return estimate_tokens_simple(content)


def estimate_file_tokens(file_path):
    """
    Estimate tokens for a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        int: Estimated token count or 0 if file cannot be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return estimate_tokens(content)
    except (UnicodeDecodeError, IOError, OSError):
        return 0


def estimate_filename_tokens(filename):
    """
    Estimate tokens for a filename.
    
    Args:
        filename (str): The filename
        
    Returns:
        int: Estimated token count
    """
    # A simple filename might be about 1-3 tokens
    return min(3, (len(filename) // 4) + 1)


def estimate_structure_tokens(files_info):
    """
    Estimate tokens for file structure representation.
    
    Args:
        files_info (list): List of file information dictionaries
        
    Returns:
        int: Estimated token count for structure
    """
    # Estimate tokens needed to represent the file structure
    structure_text = ""
    for file_info in files_info:
        structure_text += f"{file_info['path']}\n"
    
    return estimate_tokens(structure_text)