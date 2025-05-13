"""
File scanning and path filtering logic for Claude AI File Organizer.
"""

import os
import fnmatch
import glob
from pathlib import Path
from src.utils.config import load_important_files


def load_ignore_patterns(ignore_file_path):
    """
    Load patterns to ignore from a .ignore file.
    
    Args:
        ignore_file_path (Path): Path to the ignore file
        
    Returns:
        list: List of patterns to ignore
    """
    patterns = []
    
    if ignore_file_path.exists():
        with open(ignore_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                patterns.append(line)
    
    return patterns


def should_ignore(path, ignore_patterns):
    """
    Check if a path should be ignored based on ignore patterns.
    
    Args:
        path (str): Path to check
        ignore_patterns (list): List of patterns to ignore
        
    Returns:
        bool: True if the path should be ignored, False otherwise
    """
    normalized_path = path.replace('\\', '/')
    
    for pattern in ignore_patterns:
        # Directory match - pattern ends with '/'
        if pattern.endswith('/'):
            dir_pattern = pattern[:-1]  # Remove trailing slash
            if fnmatch.fnmatch(normalized_path, f"*{dir_pattern}*"):
                return True
        # File match
        elif fnmatch.fnmatch(os.path.basename(normalized_path), pattern):
            return True
    
    return False


def calculate_importance(file_path, config):
    """
    Calculate importance score for a file based on config settings.
    
    Args:
        file_path (str): Path to the file
        config (dict): Configuration with importance settings
        
    Returns:
        int: Importance score (higher is more important)
    """
    importance = 0
    file_name = os.path.basename(file_path)
    file_ext = os.path.splitext(file_name)[1].lower()
    
    # Check if file extension is important
    important_formats = config['file_importance'].get('important_formats', '').split(',')
    if any(file_ext == ext.strip() for ext in important_formats):
        importance += 10
    
    # Check if file name is important
    important_files = config['file_importance'].get('important_files', '').split(',')
    if any(file_name == important_file.strip() for important_file in important_files):
        importance += 20
    
    # Check if file is in an important path
    important_paths = config['file_importance'].get('important_paths', '').split(',')
    normalized_path = file_path.replace('\\', '/')
    if any(path.strip() in normalized_path for path in important_paths if path.strip()):
        importance += 5
    
    # Check against important files list if config has the path
    important_files_path = config['settings'].get('important_files_path', 'important_files.txt')
    if important_files_path:
        try:
            important_patterns = load_important_files(important_files_path)
            
            # Check if the file matches any pattern in the important files list
            for pattern in important_patterns:
                # Check for recursive pattern with '**'
                if '**' in pattern:
                    # Convert pattern to glob pattern and check if file matches
                    # Replace single asterisks with glob patterns
                    root_dir = os.path.dirname(os.path.abspath(important_files_path))
                    glob_pattern = os.path.join(root_dir, pattern)
                    matching_files = glob.glob(glob_pattern, recursive=True)
                    
                    # Check if the file matches any of the globbed files
                    abs_file_path = os.path.abspath(file_path)
                    if any(os.path.samefile(abs_file_path, match) for match in matching_files if os.path.isfile(match)):
                        importance += 15
                        break
                # Standard pattern matching with fnmatch
                elif fnmatch.fnmatch(file_name, pattern) or fnmatch.fnmatch(normalized_path, pattern):
                    importance += 15
                    break
        except Exception as e:
            print(f"Warning: Error checking important files list: {e}")
    
    return importance


def scan_directory(root_path, config, ignore_file_path):
    """
    Scan directory and collect information about files.
    
    Args:
        root_path (str): Root directory to scan
        config (dict): Configuration dictionary
        ignore_file_path (Path): Path to the ignore file
        
    Returns:
        list: List of dictionaries with file information
    """
    files_info = []
    ignore_patterns = load_ignore_patterns(ignore_file_path)
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip ignored directories to improve performance
        dirnames[:] = [d for d in dirnames if not should_ignore(os.path.join(dirpath, d), ignore_patterns)]
        
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(file_path, root_path)
            
            # Skip ignored files
            if should_ignore(rel_path, ignore_patterns):
                continue
            
            try:
                # Get file size and calculate importance
                file_size = os.path.getsize(file_path)
                importance = calculate_importance(rel_path, config)
                
                # Check if file is readable as text
                is_text = False
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Try to read first few lines
                        for _ in range(5):
                            f.readline()
                        is_text = True
                except (UnicodeDecodeError, IOError):
                    is_text = False
                
                # Only include text files
                if is_text:
                    files_info.append({
                        'path': rel_path,
                        'abs_path': file_path,
                        'size': file_size,
                        'importance': importance
                    })
            except (IOError, OSError) as e:
                print(f"Warning: Error processing file {file_path}: {e}")
    
    return files_info