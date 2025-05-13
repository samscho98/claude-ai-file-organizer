"""
Ignore file handling for Claude AI File Organizer.
"""

import os
from pathlib import Path


def create_default_ignore(ignore_path='.ignore'):
    """
    Create a default .ignore file if it doesn't exist.
    
    Args:
        ignore_path (str): Path to the ignore file
        
    Returns:
        bool: True if file was created, False if it already exists
    """
    if os.path.exists(ignore_path):
        return False
    
    default_ignore = """# Directories to exclude (must end with '/')
.git/
.idea/
__pycache__/
venv/
node_modules/
build/
dist/
tmp/
cache/
logs/
.venv/
env/
.env/

# Files to exclude
*.pyc
*.pyo
*.pyd
.DS_Store
*.log
*.tmp
*.bak
*.swp
*.swo
.env
.env.*
config.local.js
*.class
*.jar
*.war
*.ear
*.bin
*.exe
*.dll
*.so
*.dylib

# Large media files
*.jpg
*.jpeg
*.png
*.gif
*.webp
*.mp3
*.mp4
*.avi
*.mov
*.wmv
*.flv
*.mkv

# Large data files
*.csv
*.sqlite
*.db
*.hdf5
*.h5
*.parquet
*.tar
*.zip
*.gz
*.7z
*.rar
"""
    
    with open(ignore_path, 'w', encoding='utf-8') as f:
        f.write(default_ignore)
    
    return True


def parse_ignore_file(ignore_path):
    """
    Parse an ignore file and return patterns.
    
    Args:
        ignore_path (str): Path to the ignore file
        
    Returns:
        tuple: (dir_patterns, file_patterns)
    """
    dir_patterns = []
    file_patterns = []
    
    # Create default ignore file if it doesn't exist
    if not os.path.exists(ignore_path):
        create_default_ignore(ignore_path)
    
    with open(ignore_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
                
            # Separate directory and file patterns
            if line.endswith('/'):
                dir_patterns.append(line[:-1])  # Remove trailing slash
            else:
                file_patterns.append(line)
    
    return dir_patterns, file_patterns