"""
Improved file_organizer.py with modifications to create a single numbered export folder,
maintain consistent project naming, and track excluded files.
"""

import os
import shutil
import datetime
from pathlib import Path
import json

from src.core.token_counter import estimate_file_tokens, estimate_structure_tokens


def get_file_content(file_path):
    """
    Get the content of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: File content or empty string if can't be read
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except (UnicodeDecodeError, IOError, OSError):
        try:
            # Try reading as binary if text reading fails
            with open(file_path, 'rb') as f:
                content = f.read()
                # Try to decode with a more lenient approach
                return content.decode('utf-8', errors='replace')
        except Exception:
            return ""


def prioritize_files(files_info):
    """
    Sort files by importance and size.
    
    Args:
        files_info (list): List of dictionaries with file information
        
    Returns:
        list: Sorted list of file information
    """
    # Sort by importance (descending) and then by size (ascending)
    return sorted(files_info, key=lambda x: (-x['importance'], x['size']))


def get_project_name(root_path):
    """
    Get the project name from the root path.
    
    Args:
        root_path (str): Root directory path
        
    Returns:
        str: Project name
    """
    return os.path.basename(os.path.normpath(root_path))


def create_numbered_export_folder(output_dir, project_name):
    """
    Create a numbered export folder with project prefix.
    
    Args:
        output_dir (str): Base output directory
        project_name (str): Name of the project
        
    Returns:
        str: Path to the created folder
    """
    # Create project directory if it doesn't exist
    project_dir = os.path.join(output_dir, project_name)
    Path(project_dir).mkdir(parents=True, exist_ok=True)
    
    # Get timestamp and prefix (first few letters of project name)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = project_name[:5] if len(project_name) > 5 else project_name
    
    # Count existing export folders to get the next number
    existing_folders = [f for f in os.listdir(project_dir) 
                        if os.path.isdir(os.path.join(project_dir, f))]
    next_number = 1
    if existing_folders:
        folder_numbers = []
        for folder in existing_folders:
            try:
                if '_' in folder:
                    number = int(folder.split('_')[0])
                    folder_numbers.append(number)
            except ValueError:
                continue
        if folder_numbers:
            next_number = max(folder_numbers) + 1
    
    # Create the new folder
    export_folder_name = f"{next_number:03d}_{prefix}_{timestamp}"
    export_folder_path = os.path.join(project_dir, export_folder_name)
    Path(export_folder_path).mkdir(exist_ok=True)
    
    return export_folder_path


def normalize_filename(path):
    """
    Normalize filename to be used in the output directory.
    Keeps underscores as separators.
    
    Args:
        path (str): Original file path
        
    Returns:
        str: Normalized filename
    """
    # Replace directory separators with underscores
    normalized = path.replace('/', '_').replace('\\', '_')
    return normalized


def organize_files(files_info, max_tokens, generate_structure=True, generate_readme=True):
    """
    Organize files based on importance and token count.
    
    Args:
        files_info (list): List of dictionaries with file information
        max_tokens (int): Maximum token limit
        
    Returns:
        list: List of organized files with token information
    """
    # Prioritize files
    prioritized_files = prioritize_files(files_info)
    
    # Calculate tokens for each file
    for file_info in prioritized_files:
        file_info['tokens'] = estimate_file_tokens(file_info['abs_path'])
        file_info['content'] = get_file_content(file_info['abs_path'])
    
    # Estimate structure tokens
    structure_tokens = estimate_structure_tokens(prioritized_files)
    
    # Allocate tokens for files, respecting the maximum limit
    selected_files = []
    excluded_files = []  # Track excluded files
    current_tokens = structure_tokens  # Start with tokens for structure
    
    for file_info in prioritized_files:
        # Check if adding this file would exceed the token limit
        if current_tokens + file_info['tokens'] <= max_tokens:
            selected_files.append(file_info)
            current_tokens += file_info['tokens']
        else:
            # If we've already selected high-priority files and this one would exceed the limit,
            # skip it and try the next one (which might be smaller)
            file_info['reason'] = "Token limit exceeded"
            excluded_files.append(file_info)
            continue
    
    if not selected_files:
        print("No files selected - token limit may be too low or no files match criteria")
        return []
    
    # Get project root path from config
    # Instead of using different paths from each file, use a single project path
    root_path = os.path.commonpath([file_info['abs_path'] for file_info in selected_files])
    project_name = get_project_name(root_path)
    
    # Create a single output directory for the project
    output_dir = 'output'
    project_dir = os.path.join(output_dir, project_name)
    
    # Create project directory if it doesn't exist
    Path(project_dir).mkdir(parents=True, exist_ok=True)
    
    # Create export folder for copied files
    export_folder = create_numbered_export_folder(output_dir, project_name)
    
    # Copy files to output directory
    copy_files_to_output(selected_files, export_folder)
    
    # Create a summary file in the export folder
    create_summary_file(selected_files, current_tokens, max_tokens, export_folder, project_name)
    
    # Generate file report in the project directory (not in the export folder)
    try:
        from src.utils.file_tracker import generate_file_report
        report_path = generate_file_report(
            project_name, 
            root_path, 
            selected_files, 
            excluded_files,
            project_dir  # Save to project directory, not the export folder
        )
        print(f"File report generated at: {report_path}")
    except ImportError as e:
        print(f"Warning: File tracker module not found, report not generated: {e}")
        
    # Generate structure if enabled
    structure = None
    if generate_structure:
        try:
            from src.core.structure_generator import generate_structure as gen_structure
            
            # Default exclusions for structure
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
            
            # Generate structure with exclusions
            structure_json = gen_structure(root_path, selected_files, exclude_dirs)
            
            # Save structure to a file in the export folder
            structure_path = os.path.join(export_folder, f"{project_name}_structure.json")
            with open(structure_path, 'w') as f:
                f.write(structure_json)
                
            structure = structure_json
            print(f"Structure saved to {structure_path}")
        except Exception as e:
            print(f"Error generating structure: {e}")

    # Generate README if enabled and structure is available
    if generate_readme and structure:
        try:
            from src.core.readme_generator import generate_readme, save_readme
            import json
            
            # Default exclusions for README
            exclude_dirs = [
                # Python related
                '__pycache__/', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll',
                'venv/', '.venv/', 'env/', '.env/', 'virtualenv/',
                'dist/', 'build/', 'eggs/', 'parts/', 'bin/', 'var/',
                'sdist/', 'develop-eggs/', '.installed.cfg', 'lib/', 'lib64/',
                
                # JavaScript/Node related
                'node_modules/', 'bower_components/', '.npm/', '.yarn/',
                
                # Version control
                '.git/', '.hg/', '.svn/', '.cvs/', '.bzr/',
                
                # IDE and editors
                '.idea/', '.vscode/', '*.swp', '*.swo', '*.swn', '*.bak',
                
                # OS specific
                '.DS_Store/', 'Thumbs.db/', 'ehthumbs.db/',
                
                # Project specific
                'output/', 'logs/', 'temp/', 'tmp/', 'cache/',
                
                # Package directories
                'site-packages/', '.pytest_cache/'
            ]
            
            # Generate README
            readme_content = generate_readme(
                json.loads(structure), 
                selected_files, 
                project_name,
                exclude_dirs=exclude_dirs
            )
            
            # Save README to the export folder
            readme_path = os.path.join(export_folder, f"{project_name}_README.md")
            save_readme(readme_content, readme_path)
            print(f"README saved to {readme_path}")
        except Exception as e:
            print(f"Error generating README: {e}")

    print(f"Selected {len(selected_files)} out of {len(files_info)} files")
    print(f"Total tokens: {current_tokens} / {max_tokens}")
    print(f"Files exported to: {export_folder}")
    
    return selected_files


def copy_files_to_output(selected_files, export_folder):
    """
    Copy selected files to the output directory.
    
    Args:
        selected_files (list): List of selected file information
        export_folder (str): Output directory path
    """
    for file_info in selected_files:
        # Create normalized filename
        output_filename = normalize_filename(file_info['path'])
        output_path = os.path.join(export_folder, output_filename)
        
        # Copy file content
        with open(output_path, 'w', encoding='utf-8', errors='replace') as f:
            f.write(file_info['content'])


def create_summary_file(selected_files, total_tokens, max_tokens, export_folder, project_name):
    """
    Create a summary file with information about the export.
    
    Args:
        selected_files (list): List of selected file information
        total_tokens (int): Total token count
        max_tokens (int): Maximum token limit
        export_folder (str): Path to the export folder
        project_name (str): Name of the project
    """
    summary_path = os.path.join(export_folder, "_SUMMARY.txt")
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"Claude AI File Organizer Summary\n")
        f.write(f"===============================\n\n")
        f.write(f"Project: {project_name}\n")
        f.write(f"Export Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Files: {len(selected_files)}\n")
        f.write(f"Total Tokens: {total_tokens} / {max_tokens} ({total_tokens/max_tokens*100:.1f}%)\n\n")
        
        f.write(f"Files by Importance:\n")
        f.write(f"------------------\n")
        
        # Group files by importance
        importance_groups = {}
        for file_info in selected_files:
            importance = file_info['importance']
            if importance not in importance_groups:
                importance_groups[importance] = []
            importance_groups[importance].append(file_info)
        
        # Write files sorted by importance
        for importance in sorted(importance_groups.keys(), reverse=True):
            f.write(f"\nImportance Level: {importance}\n")
            for file_info in importance_groups[importance]:
                f.write(f"  - {file_info['path']} ({file_info['tokens']} tokens)\n")