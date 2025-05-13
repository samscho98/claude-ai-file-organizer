"""
Configuration handling for Claude AI File Organizer.
"""

import os
import configparser
from pathlib import Path


def load_config(config_path='config.ini'):
    """
    Load configuration from config file.
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        configparser.ConfigParser: Configuration object
        
    Raises:
        FileNotFoundError: If the config file does not exist
        configparser.Error: If there's an error parsing the config file
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # Validate required sections and settings
    validate_config(config)
    
    return config


def validate_config(config):
    """
    Validate that all required configuration is present.
    
    Args:
        config (configparser.ConfigParser): Configuration object
        
    Raises:
        ValueError: If required configuration is missing
    """
    # Check required sections
    required_sections = ['settings', 'file_importance']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required section in config: {section}")
    
    # Check required settings
    if 'path' not in config['settings']:
        raise ValueError("Missing required setting: path in settings section")
    
    # Apply defaults for optional settings
    if 'output_dir' not in config['settings']:
        config['settings']['output_dir'] = 'output'
    
    if 'max_tokens' not in config['settings']:
        config['settings']['max_tokens'] = '60000'
    
    if 'ignore' not in config['settings']:
        config['settings']['ignore'] = '.ignore'
    
    if 'important_files_path' not in config['settings']:
        config['settings']['important_files_path'] = 'important_files.txt'
    
    if 'generate_structure' not in config['settings']:
        config['settings']['generate_structure'] = 'true'
    
    # Ensure file_importance section has default values
    if 'important_formats' not in config['file_importance']:
        config['file_importance']['important_formats'] = '.py,.md,.txt,.json'
    
    if 'important_files' not in config['file_importance']:
        config['file_importance']['important_files'] = 'README.md,requirements.txt,setup.py'
    
    if 'important_paths' not in config['file_importance']:
        config['file_importance']['important_paths'] = 'src/,docs/'


def load_important_files(important_files_path='important_files.txt'):
    """
    Load important files patterns from a file.
    
    Args:
        important_files_path (str): Path to the important files specification
        
    Returns:
        list: List of file patterns to prioritize
    """
    patterns = []
    
    # Create default if not exists
    if not os.path.exists(important_files_path):
        create_default_important_files(important_files_path)
    
    try:
        with open(important_files_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                patterns.append(line)
    except Exception as e:
        print(f"Warning: Could not load important files from {important_files_path}: {e}")
    
    return patterns


def create_default_important_files(important_files_path='important_files.txt'):
    """
    Create a default important files specification.
    
    Args:
        important_files_path (str): Path where to create the file
        
    Returns:
        bool: True if file was created, False if it already exists
    """
    if os.path.exists(important_files_path):
        return False
    
    default_content = """# Important Files for Claude AI File Organizer
# One file pattern per line. These will be prioritized during organization.
# Use glob patterns (e.g., *.py, src/*.md)
# Lines starting with # are comments

# Configuration files
config.ini
pyproject.toml
setup.py
package.json
.env.example

# Documentation
README.md
CONTRIBUTING.md
LICENSE
docs/*.md
docs/*.rst

# Main code entry points
main.py
src/main.py
app.py
index.js
manage.py

# Core functionality
src/core/*.py
src/utils/*.py
src/api/*.py
src/models/*.py
lib/*.py
lib/*.js

# Tests (prioritized lower)
tests/*.py
test_*.py
*_test.py
"""
    
    with open(important_files_path, 'w', encoding='utf-8') as f:
        f.write(default_content)
    
    return True


def create_default_config(config_path='config.ini'):
    """
    Create a default configuration file.
    
    Args:
        config_path (str): Path where to create the config file
        
    Returns:
        bool: True if file was created, False if it already exists
    """
    if os.path.exists(config_path):
        return False
    
    config = configparser.ConfigParser()
    
    # Default settings
    config['settings'] = {
        'path': os.getcwd(),
        'output_dir': 'output',
        'ignore': '.ignore',
        'important_files_path': 'important_files.txt',
        'generate_structure': 'true',
        'max_tokens': '60000'
    }
    
    # Default file importance
    config['file_importance'] = {
        'important_formats': '.py,.md,.txt,.ini,.json,.yaml,.yml,.toml,.cfg,.conf,.sh,.bat,.js,.jsx,.ts,.tsx,.html,.css,.scss,.sql,.rst',
        'important_files': 'README.md,requirements.txt,setup.py,pyproject.toml,package.json,config.ini,.env.example,Dockerfile,docker-compose.yml,Makefile,LICENSE',
        'important_paths': 'src/,docs/,scripts/,config/,templates/'
    }
    
    # API settings section if needed
    config['api_settings'] = {
        'extract_endpoints': 'false',
        'endpoint_path': ''
    }
    
    # Write the configuration to file
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    
    return True