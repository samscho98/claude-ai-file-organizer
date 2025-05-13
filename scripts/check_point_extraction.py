#!/usr/bin/env python3
"""
Check if API endpoint extraction is enabled and run it if needed.

This script checks the config.ini file to see if API endpoint extraction
is enabled, and if so, runs the extraction process.
"""

import os
import sys
import configparser
from pathlib import Path

# Add the parent directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

from src.utils.config import load_config
from src.api.extract_endpoints import extract_endpoints_from_file, group_endpoints_by_prefix, save_endpoints


def check_endpoint_extraction():
    """Check if endpoint extraction is enabled and run it if needed."""
    print("Checking API endpoint extraction settings...")
    
    try:
        # Load configuration
        config = load_config()
        
        # Check if endpoint extraction is enabled
        if not config['api_settings'].getboolean('extract_endpoints', False):
            print("API endpoint extraction is disabled.")
            return False
        
        # Get project path
        project_path = config['settings'].get('path')
        if not project_path:
            print("Project path not specified.")
            return False
        
        # Get output directory
        output_dir = config['settings'].get('output_dir', 'output')
        
        print(f"API endpoint extraction is enabled.")
        print(f"Project path: {project_path}")
        print(f"Output directory: {output_dir}")
        
        return True
    
    except Exception as e:
        print(f"Error checking endpoint extraction: {e}")
        return False


def extract_endpoints(project_path, output_dir):
    """
    Extract API endpoints from project files.
    
    Args:
        project_path (str): Path to the project
        output_dir (str): Output directory path
    """
    print("Extracting API endpoints...")
    
    # Get project name from path
    project_name = os.path.basename(os.path.normpath(project_path))
    
    # Create output directory for this project
    output_path = os.path.join(output_dir, project_name)
    Path(output_path).mkdir(exist_ok=True)
    
    endpoints = []
    
    # Walk through project files
    for root, _, files in os.walk(project_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip binary files and non-relevant extensions
            ext = os.path.splitext(file)[1].lower()
            if ext in ['.py', '.js', '.ts', '.java', '.rb', '.php', '.go', '.yaml', '.yml', '.json']:
                try:
                    file_endpoints = extract_endpoints_from_file(file_path)
                    if file_endpoints:
                        print(f"Found {len(file_endpoints)} endpoints in {file_path}")
                        endpoints.extend(file_endpoints)
                except Exception as e:
                    print(f"Error extracting endpoints from {file_path}: {e}")
    
    # Remove duplicates
    unique_endpoints = list(set(endpoints))
    print(f"Found {len(unique_endpoints)} unique endpoints.")
    
    # Group endpoints by prefix
    grouped_endpoints = group_endpoints_by_prefix(unique_endpoints)
    
    # Save endpoints
    endpoints_path = os.path.join(output_path, f"{project_name}_endpoints.json")
    
    # Save endpoints to JSON file
    with open(endpoints_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(grouped_endpoints, f, indent=2)
    
    print(f"Saved endpoints to {endpoints_path}")


def main():
    """Main function."""
    if check_endpoint_extraction():
        config = load_config()
        project_path = config['settings'].get('path')
        output_dir = config['settings'].get('output_dir', 'output')
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(exist_ok=True)
        
        # Extract endpoints
        extract_endpoints(project_path, output_dir)
        return 0
    
    return 1


if __name__ == "__main__":
    sys.exit(main())