"""
Structure visualization generation for Claude AI File Organizer.
"""

import os
import json
from pathlib import Path


def should_exclude_item(item_name, item_path=None, exclude_dirs=None):
    """
    Determine if an item should be excluded from the structure.
    
    Args:
        item_name (str): Name of the file or directory
        item_path (str, optional): Path to the item
        exclude_dirs (list, optional): List of directory patterns to exclude
        
    Returns:
        bool: True if the item should be excluded, False otherwise
    """
    if exclude_dirs is None:
        # Default exclusions
        exclude_dirs = [
            # Python related
            '__pycache__', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll',
            'venv', '.venv', 'env', '.env', 'virtualenv',
            'dist', 'build', 'eggs', 'parts', 'bin', 'var',
            'sdist', 'develop-eggs', '.installed.cfg', 'lib', 'lib64',
            
            # JavaScript/Node related
            'node_modules', 'bower_components', '.npm', '.yarn',
            
            # Version control
            '.git', '.hg', '.svn', '.cvs', '.bzr',
            
            # IDE and editors
            '.idea', '.vscode', '*.swp', '*.swo', '*.swn', '*.bak',
            
            # OS specific
            '.DS_Store', 'Thumbs.db', 'ehthumbs.db',
            
            # Project specific
            'output', 'logs', 'temp', 'tmp', 'cache',
            
            # Package directories
            'site-packages', '.pytest_cache'
        ]
    
    # Common directories to always exclude
    always_exclude = [
        '__pycache__', 'venv', '.venv', 'node_modules', '.git', 
        'dist', 'build', 'eggs', 'site-packages'
    ]
    
    # Always exclude these directories
    if item_name in always_exclude:
        return True
        
    # Check file extensions for files
    if '.' in item_name:
        excluded_extensions = ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe']
        _, ext = os.path.splitext(item_name)
        if ext.lower() in excluded_extensions:
            return True
            
    # Check against exclude patterns
    if item_path:
        full_path = os.path.join(item_path, item_name)
        return any(
            (exclude_pattern in full_path) or 
            (exclude_pattern in item_name) or
            (exclude_pattern == item_name)
            for exclude_pattern in exclude_dirs
        )
    
    return any(
        (exclude_pattern in item_name) or
        (exclude_pattern == item_name)
        for exclude_pattern in exclude_dirs
    )


def build_directory_structure(root_path, exclude_dirs=None):
    """
    Build a nested directory structure representation.
    
    Args:
        root_path (str): Root directory path
        exclude_dirs (list, optional): List of directory patterns to exclude
        
    Returns:
        dict: Nested directory structure
    """
    root_name = os.path.basename(os.path.normpath(root_path))
    structure = {
        "name": root_name,
        "type": "directory",
        "children": []
    }
    
    for item in sorted(os.listdir(root_path)):
        item_path = os.path.join(root_path, item)
        
        # Skip hidden files and directories (except .ignore)
        if item.startswith('.') and item != '.ignore':
            continue
            
        # Check if item should be excluded
        if should_exclude_item(item, root_path, exclude_dirs):
            continue
        
        if os.path.isdir(item_path):
            # Recursively process directory
            dir_structure = build_directory_structure(item_path, exclude_dirs)
            if dir_structure and dir_structure.get("children"):
                structure["children"].append(dir_structure)
        else:
            # Add file
            structure["children"].append({
                "name": item,
                "type": "file"
            })
    
    return structure


def add_file_content(structure, files_info):
    """
    Add file content to the structure for selected files.
    
    Args:
        structure (dict): Directory structure
        files_info (list): Selected files information
        
    Returns:
        dict: Updated directory structure
    """
    # Create a dictionary for quick lookup of file paths
    files_dict = {file_info['path'].replace('\\', '/'): file_info for file_info in files_info}
    
    def process_node(node, current_path=""):
        """Process a node in the structure tree."""
        if node["type"] == "directory":
            # Process directory
            dir_path = os.path.join(current_path, node["name"]) if current_path else node["name"]
            
            for child in node.get("children", []):
                process_node(child, dir_path)
        else:
            # Process file
            file_path = os.path.join(current_path, node["name"]).replace('\\', '/')
            
            if file_path in files_dict:
                # Add file content for selected files
                node["content"] = files_dict[file_path]["content"]
    
    # Make a deep copy of the structure to avoid modifying the original
    import copy
    structure_copy = copy.deepcopy(structure)
    
    # Process the structure
    process_node(structure_copy)
    
    return structure_copy


def generate_structure(root_path, selected_files, exclude_dirs=None):
    """
    Generate a JSON structure of the project with file content.
    
    Args:
        root_path (str): Root directory path
        selected_files (list): Selected files information
        exclude_dirs (list, optional): List of directory patterns to exclude
        
    Returns:
        str: JSON string of the structure
    """
    # Build directory structure
    structure = build_directory_structure(root_path, exclude_dirs)
    
    # Add file content for selected files
    structure_with_content = add_file_content(structure, selected_files)
    
    # Convert to JSON
    return json.dumps(structure_with_content, indent=2)


def save_structure(structure, output_path):
    """
    Save structure to a file.
    
    Args:
        structure (str): JSON structure string
        output_path (str): Output file path
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(structure)