"""
README.md generation functionality for Claude AI File Organizer.
"""

import os
import json
from pathlib import Path


def analyze_project_structure(structure_data, exclude_dirs=None):
    """
    Analyze the project structure to extract useful information.
    
    Args:
        structure_data (dict): Project structure data
        exclude_dirs (list, optional): List of directory paths to exclude
        
    Returns:
        dict: Analysis results with file counts, key directories, etc.
    """
    if exclude_dirs is None:
        # Default exclusions
        exclude_dirs = ['__pycache__/', 'venv/', '.venv/', 'node_modules/', '.git/', 
                        'dist/', 'build/', 'eggs/', 'parts/', 'bin/', 'var/', 
                        'sdist/', 'develop-eggs/', '.installed.cfg', 'lib/', 'lib64/']
        
    analysis = {
        "total_files": 0,
        "file_types": {},
        "key_directories": [],
        "important_files": []
    }
    
    def should_exclude_dir(dir_name, path):
        """Check if a directory should be excluded."""
        # Common directories to always exclude
        always_exclude = ['__pycache__', 'venv', '.venv', 'node_modules', '.git', 
                          'dist', 'build', 'eggs', 'site-packages']
        
        # Check if the directory name is in the always exclude list
        if dir_name in always_exclude:
            return True
            
        # Check if the directory path contains any of the exclude patterns
        full_path = f"{path}/{dir_name}" if path else dir_name
        if any(excluded_dir in f"{full_path}/" for excluded_dir in exclude_dirs):
            return True
            
        return False
    
    def should_exclude_file(file_name):
        """Check if a file should be excluded."""
        # Common file extensions to exclude
        exclude_extensions = ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe']
        
        # Check file extension
        _, ext = os.path.splitext(file_name)
        if ext.lower() in exclude_extensions:
            return True
            
        # Check for other patterns
        if file_name.startswith('.'):
            return True
            
        return False
    
    def traverse_structure(node, path=""):
        """Recursively traverse the structure to gather statistics."""
        if node["type"] == "file":
            # Skip excluded file types
            if should_exclude_file(node["name"]):
                return
                
            analysis["total_files"] += 1
            
            # Count file types
            file_ext = os.path.splitext(node["name"])[1].lower()
            if file_ext:
                if file_ext not in analysis["file_types"]:
                    analysis["file_types"][file_ext] = 0
                analysis["file_types"][file_ext] += 1
            
            # Note important files
            important_filenames = ["readme.md", "setup.py", "requirements.txt", 
                                 "config.ini", "main.py", "package.json"]
            if node["name"].lower() in important_filenames:
                analysis["important_files"].append(path + "/" + node["name"])
        
        elif node["type"] == "directory":
            # Skip excluded directories
            if should_exclude_dir(node["name"], path):
                return
                
            current_path = path + "/" + node["name"] if path else node["name"]
            
            # Track key directories (those with multiple Python files)
            py_files = [
                child for child in node.get("children", []) 
                if child["type"] == "file" and child["name"].endswith(".py")
                and not should_exclude_file(child["name"])
            ]
            
            if len(py_files) >= 2:
                analysis["key_directories"].append(current_path)
            
            # Recursive traversal
            for child in node.get("children", []):
                traverse_structure(child, current_path)
    
    traverse_structure(structure_data)
    
    # Sort file types by frequency
    analysis["file_types"] = dict(sorted(
        analysis["file_types"].items(), 
        key=lambda item: item[1], 
        reverse=True
    ))
    
    return analysis


def extract_project_description(files_info):
    """
    Extract project description from README.md or other key files.
    
    Args:
        files_info (list): List of file information dictionaries
        
    Returns:
        str: Project description or empty string if not found
    """
    description = ""
    
    # First check for README.md
    readme_files = [f for f in files_info if f["path"].lower() == "readme.md"]
    if readme_files:
        readme_content = readme_files[0].get("content", "")
        # Extract first paragraph from README
        if readme_content:
            lines = readme_content.split('\n')
            # Skip title if present
            start_idx = 0
            if lines and lines[0].startswith('# '):
                start_idx = 1
            
            # Collect lines until empty line
            desc_lines = []
            for i in range(start_idx, len(lines)):
                if not lines[i].strip():
                    break
                desc_lines.append(lines[i])
            
            if desc_lines:
                description = ' '.join(desc_lines)
    
    # If no description found in README, check setup.py
    if not description:
        setup_files = [f for f in files_info if f["path"].lower() == "setup.py"]
        if setup_files:
            setup_content = setup_files[0].get("content", "")
            # Try to extract description from setup.py
            if "description=" in setup_content:
                start = setup_content.find("description=") + len("description=")
                end = setup_content.find(",", start)
                if end > start:
                    description = setup_content[start:end].strip('\'"')
    
    return description


def suggest_file_purpose(file_path):
    """
    Suggest the likely purpose of a file based on naming and location.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Suggested purpose
    """
    filename = os.path.basename(file_path)
    dirname = os.path.dirname(file_path)
    
    # Common patterns
    if filename == '__init__.py':
        return "Python module initialization"
    elif filename == 'main.py':
        return "Application entry point"
    elif 'test' in filename.lower() and filename.endswith('.py'):
        return "Unit/integration test"
    elif filename == 'setup.py':
        return "Package installation configuration"
    elif filename == 'requirements.txt':
        return "Python dependencies list"
    elif filename == 'config.ini':
        return "Application configuration"
    elif filename.startswith('README'):
        return "Project documentation"
    elif filename.endswith('.bat') or filename.endswith('.sh'):
        return "Execution script"
    elif 'utils' in dirname.lower() and filename.endswith('.py'):
        return "Utility functions"
    elif 'core' in dirname.lower() and filename.endswith('.py'):
        return "Core application logic"
    elif 'api' in dirname.lower() and filename.endswith('.py'):
        return "API implementation"
    elif 'gui' in dirname.lower() and filename.endswith('.py'):
        return "User interface component"
    
    # Default case
    if '.' in filename:
        ext = filename.split('.')[-1]
        if ext == 'py':
            return "Python module"
        elif ext == 'js':
            return "JavaScript module"
        elif ext in ['html', 'css']:
            return "Web interface component"
        elif ext in ['json', 'yaml', 'yml']:
            return "Data configuration"
    
    return "Project file"


def format_structure(node, indent=0, exclude_dirs=None):
    """
    Format structure node for display, excluding specified directories.
    
    Args:
        node (dict): Structure node
        indent (int): Current indentation level
        exclude_dirs (list): List of directory paths to exclude
        
    Returns:
        str: Formatted structure representation
    """
    if exclude_dirs is None:
        # Default exclusions if none provided
        exclude_dirs = ['__pycache__/', 'venv/', '.venv/', 'node_modules/']
    
    result = ""
    
    if node["type"] == "directory":
        # Get the full path of the current node
        node_path = node["name"] + "/"
        
        # Skip this directory and its children if:
        # 1. The directory name is in the exclude_dirs list
        # 2. The directory name starts with '__pycache__' or similar patterns
        if (any(excluded_dir in node_path for excluded_dir in exclude_dirs) or
            node["name"] == "__pycache__" or
            node["name"] == "venv" or
            node["name"] == ".venv" or
            node["name"] == "node_modules"):
            return ""
        
        result += " " * indent + node["name"] + "/\n"
        
        # Sort children: directories first, then files
        dirs = []
        files = []
        for child in node.get("children", []):
            if child["type"] == "directory":
                # Skip common directories that should be excluded
                if (child["name"] == "__pycache__" or
                    child["name"] == "venv" or
                    child["name"] == ".venv" or
                    child["name"] == "node_modules" or
                    any(excluded_dir in child["name"] for excluded_dir in exclude_dirs)):
                    continue
                dirs.append(child)
            else:
                files.append(child)
        
        # Process directories first (sorted by name)
        for child in sorted(dirs, key=lambda x: x["name"]):
            child_result = format_structure(child, indent + 2, exclude_dirs)
            # Only add the result if the child wasn't excluded
            if child_result:
                result += child_result
        
        # Then process files (show up to 5 per directory)
        for child in sorted(files, key=lambda x: x["name"])[:5]:
            result += format_structure(child, indent + 2, exclude_dirs)
        
        # If there are more files, indicate with ellipsis
        if len(files) > 5:
            result += " " * (indent + 2) + "...\n"
    else:
        # Skip common excluded file patterns like .pyc
        if node["name"].endswith(".pyc") or node["name"].endswith(".pyo"):
            return ""
        result += " " * indent + node["name"] + "\n"
    
    return result


def generate_readme(structure_data, files_info, project_name, exclude_dirs=None):
    """
    Generate a README.md for Claude AI with project overview.
    
    Args:
        structure_data (dict): Project structure data
        files_info (list): List of file information dictionaries
        project_name (str): Name of the project
        exclude_dirs (list, optional): List of directory paths to exclude
        
    Returns:
        str: README.md content
    """
    # Analyze project
    analysis = analyze_project_structure(structure_data, exclude_dirs)
    
    # Extract project description
    description = extract_project_description(files_info)
    if not description:
        description = f"{project_name} - Project prepared for Claude AI."
    
    # Identify main modules
    main_modules = []
    for dir_path in analysis["key_directories"]:
        if dir_path != project_name and not dir_path.startswith(project_name + "/output"):
            parts = dir_path.split('/')
            if len(parts) >= 2 and parts[1] in ['src', 'app', 'lib', 'core']:
                main_modules.append(dir_path)
    
    # Create the README content
    readme = f"""# {project_name}

{description}

## Project Overview

This is an organized snapshot of the "{project_name}" project prepared for Claude AI.

- **Total Files**: {analysis["total_files"]}
- **Main Language**: {next(iter(analysis["file_types"]), "Unknown").replace('.', '')}
- **Primary Modules**: {', '.join(main_modules) if main_modules else "No specific modules identified"}

## Key Files and Their Purpose

| File | Purpose |
|------|---------|
"""
    
    # Add important files table
    important_files = []
    for file_info in files_info:
        if file_info["importance"] >= 15:  # Files with higher importance scores
            important_files.append(file_info)
    
    # Sort by importance (descending)
    important_files = sorted(important_files, key=lambda x: x["importance"], reverse=True)
    
    # Limit to top 10 most important files
    for file_info in important_files[:10]:
        purpose = suggest_file_purpose(file_info["path"])
        readme += f"| `{file_info['path']}` | {purpose} |\n"
    
    # Add project structure section
    readme += """
## Project Structure

The project follows this structure (abbreviated):

```
"""
    
    # Add simplified structure representation with exclusions
    readme += format_structure(structure_data, exclude_dirs=exclude_dirs)
    readme += "```\n\n"
    
    # Add token information
    readme += f"""## Claude AI Information

This project snapshot has been prepared for Claude AI assistance:

- Files are prioritized by importance
- Total token count kept below 60,000 tokens
- File naming format preserves directory structure

Questions about specific files or functionalities are welcome!
"""
    
    return readme


def save_readme(readme_content, output_path):
    """
    Save README.md to the output directory.
    
    Args:
        readme_content (str): README.md content
        output_path (str): Output directory path
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)