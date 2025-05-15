#!/usr/bin/env python3
"""
Main entry point for the Claude AI File Organizer.
"""

import json
import os
import sys
import argparse
import configparser
import shutil
import subprocess
from pathlib import Path
import logging

# Add the parent directory to the path if running as a script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import local modules
from utils.config import load_config
from utils.logger import setup_logger, log_exception
from core.file_scanner import scan_directory
from core.token_counter import estimate_tokens
from core.file_organizer import organize_files
from core.structure_generator import generate_structure
from core.readme_generator import generate_readme, save_readme
from api.extract_endpoints import extract_endpoints_from_file, group_endpoints_by_prefix


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Organize project files for optimal use with Claude AI"
    )
    parser.add_argument(
        "-c", "--config", 
        default="config.ini", 
        help="Path to configuration file"
    )
    parser.add_argument(
        "-p", "--path", 
        help="Project path to organize (overrides config file)"
    )
    parser.add_argument(
        "--max-tokens", 
        type=int, 
        help="Maximum token limit (overrides config file)"
    )
    parser.add_argument(
        "--no-open", 
        action="store_true",
        help="Don't open output folder after processing"
    )
    return parser.parse_args()


def open_folder(folder_path):
    """Open the folder in the system's file explorer."""
    if os.path.exists(folder_path):
        try:
            if sys.platform == 'win32':
                os.startfile(folder_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.call(['open', folder_path])
            else:  # Linux
                subprocess.call(['xdg-open', folder_path])
            return True
        except Exception as e:
            print(f"Warning: Could not open folder: {e}")
            return False
    else:
        print(f"Warning: Directory does not exist: {folder_path}")
        return False


def main():
    """Main application function."""
    # Setup logging
    logger = setup_logger()
    logger.info("Claude AI File Organizer started")
    
    print("Claude AI File Organizer")
    print("=======================")
    
    # Parse command line arguments
    args = parse_arguments()
    logger.info(f"Command line arguments: {args}")
    
    # Load configuration
    try:
        config = load_config(args.config)
        logger.info(f"Configuration loaded from {args.config}")
    except Exception as e:
        log_exception(logger, e, "loading configuration")
        print(f"Error loading configuration: {e}")
        return 1
    
    # Override configuration with command line arguments if provided
    if args.path:
        config['settings']['path'] = args.path
        logger.info(f"Path overridden from command line: {args.path}")
    if args.max_tokens:
        config['settings']['max_tokens'] = str(args.max_tokens)
        logger.info(f"Max tokens overridden from command line: {args.max_tokens}")
    
    # Validate essential configuration
    project_path = config['settings'].get('path')
    if not project_path:
        logger.error("Project path not specified in config or arguments")
        print("Error: Project path not specified in config or arguments")
        return 1
    
    # Ensure project path exists
    if not os.path.isdir(project_path):
        logger.error(f"Project path does not exist: {project_path}")
        print(f"Error: Project path does not exist: {project_path}")
        return 1
    
    print(f"Project path: {project_path}")
    logger.info(f"Project path: {project_path}")
    
    # Create output directory if it doesn't exist
    output_dir = config['settings'].get('output_dir', 'output')
    Path(output_dir).mkdir(exist_ok=True)
    logger.info(f"Output directory: {output_dir}")
    
    # Get project name from path
    project_name = os.path.basename(os.path.normpath(project_path))
    project_output_path = os.path.join(output_dir, project_name)
    
    # Create project output directory if it doesn't exist
    Path(project_output_path).mkdir(exist_ok=True)
    
    # Get maximum token limit
    max_tokens = int(config['settings'].get('max_tokens', '60000'))
    print(f"Maximum token limit: {max_tokens}")
    logger.info(f"Maximum token limit: {max_tokens}")
    
    # Store the most recent export folder path
    latest_export_folder = None
    
    # Scan the directory for files
    try:
        print("Scanning directory for files...")
        logger.info(f"Scanning directory: {project_path}")
        files_info = scan_directory(
            project_path, 
            config, 
            Path(config['settings'].get('ignore', '.ignore'))
        )
        logger.info(f"Found {len(files_info)} files")
    except Exception as e:
        log_exception(logger, e, "scanning directory")
        print(f"Error scanning directory: {e}")
        return 1
    
    # Organize files
    try:
        print("Organizing files by importance and token count...")
        logger.info("Organizing files by importance and token count...")
        organized_files, export_folder = organize_files(
            files_info, 
            max_tokens,
            config['settings'].getboolean('generate_structure', True),
            config['settings'].getboolean('generate_readme', True)
        )
        latest_export_folder = export_folder  # Store the export folder path
        logger.info(f"Selected {len(organized_files)} files")
        logger.info(f"Export folder: {export_folder}")
    except Exception as e:
        log_exception(logger, e, "organizing files")
        print(f"Error organizing files: {e}")
        return 1
    
    # Extract API endpoints if enabled
    if config['api_settings'].getboolean('extract_endpoints', False):
        try:
            print("Extracting API endpoints...")
            logger.info("Extracting API endpoints...")
            endpoints = []
            
            # Extract endpoints from each file
            for file_info in organized_files:
                file_path = file_info['abs_path']
                file_ext = os.path.splitext(file_path)[1].lower()
                
                # Only extract from relevant file types
                if file_ext in ['.py', '.js', '.ts', '.java', '.rb', '.php', '.go', '.yaml', '.yml', '.json']:
                    try:
                        file_endpoints = extract_endpoints_from_file(file_path, file_info.get('content', ''))
                        if file_endpoints:
                            print(f"Found {len(file_endpoints)} endpoints in {file_info['path']}")
                            logger.info(f"Found {len(file_endpoints)} endpoints in {file_info['path']}")
                            endpoints.extend(file_endpoints)
                    except Exception as e:
                        logger.warning(f"Error extracting endpoints from {file_path}: {e}")
                        print(f"Warning: Error extracting endpoints from {file_path}: {e}")
            
            # Remove duplicates
            unique_endpoints = list(set(endpoints))
            
            if unique_endpoints:
                print(f"Found {len(unique_endpoints)} unique endpoints.")
                logger.info(f"Found {len(unique_endpoints)} unique endpoints.")
                
                # Group endpoints by prefix
                grouped_endpoints = group_endpoints_by_prefix(unique_endpoints)
                
                # Save endpoints to JSON file in output directory
                endpoints_path = os.path.join(project_output_path, f"{project_name}_endpoints.json")
                with open(endpoints_path, 'w', encoding='utf-8') as f:
                    json.dump(grouped_endpoints, f, indent=2)
                
                print(f"Endpoints saved to {endpoints_path}")
                logger.info(f"Endpoints saved to {endpoints_path}")
            else:
                print("No API endpoints found.")
                logger.info("No API endpoints found.")
                
        except Exception as e:
            log_exception(logger, e, "extracting endpoints")
            print(f"Error extracting endpoints: {e}")
            # Don't return, continue with other operations
    
    print("Organization complete!")
    logger.info("Organization complete!")
    
    # Open folder if enabled and not disabled by command line
    should_open = not args.no_open and config['settings'].getboolean('open_output_folder', False)
    if should_open and latest_export_folder:
        print(f"Opening folder: {latest_export_folder}")
        open_folder(latest_export_folder)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        # Setup basic logger if it hasn't been setup yet
        logger = logging.getLogger("claude_ai_file_organizer")
        if not logger.handlers:
            handler = logging.StreamHandler()
            logger.addHandler(handler)
        
        log_exception(logger, e, "main execution")
        print(f"Unexpected error: {e}")
        print("See logs for more details.")
        sys.exit(1)