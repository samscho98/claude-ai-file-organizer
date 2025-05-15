# Claude AI File Organizer

<img src="https://img.shields.io/badge/python-3.13+-blue.svg" alt="Python Version">
<img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">

A specialized tool that organizes project files for optimal use with Claude AI, respecting token limits while preserving project structure.

## 🚀 Overview

Claude AI File Organizer helps developers prepare their codebases for analysis by Claude AI. It intelligently:

- Selects the most important files from a project based on configurable settings
- Estimates token usage to stay within Claude AI's limits (default: 60,000 tokens)
- Preserves the project's directory structure for context
- Generates structure visualization and documentation

Perfect for getting AI assistance with large codebases where the entire project would exceed token limits.


"*The context window and message limit of claude.ai's free open beta can vary depending on current demand.*
The **maximum length** of prompt that Claude can process is its context window. The context window for Claude Pro and our API is currently **200k+ tokens (about 500 pages of text or 100 images)**. " [Source - support.anthropic.com](https://support.anthropic.com/en/articles/7996856-what-is-the-maximum-prompt-length).

*It is advised to not go far above 25% of the token limit with project knowledge*.

## ✨ Features

![claude_organizer](https://github.com/user-attachments/assets/c744f932-d776-44bd-8462-ee77139dfdda)

- **Smart File Selection**: Prioritizes files based on importance settings
- **Token Management**: Estimates and limits token usage for Claude AI
- **Structure Preservation**: Files are organized while maintaining their relationship to the project structure
- **API Endpoint Extraction**: Automatically detects API endpoints from various frameworks (Flask, Express, Spring, etc.)
- **Documentation Generation**: Creates README files and structure visualizations
- **GUI Settings Manager**: Configure the tool through an intuitive interface
- **Integrated File Editors**: Edit `.ignore` and `important_files.txt` files directly in the GUI
- **Recursive Pattern Matching**: Support for `**` pattern to include files in subdirectories

## 📋 Requirements

- Python 3.13+ (should work with Python 3.8+)
- No mandatory external dependencies
- Optional: `tiktoken` for more accurate token counting

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-ai-file-organizer.git
cd claude-ai-file-organizer

# Optional: Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with additional dependencies (recommended)
pip install -e .[token_counting]

# Or basic installation
pip install -e .
```

## 💻 Usage

### Command Line

```bash
# Simple usage (uses settings from config.ini)
python src/main.py

# Specify a different config file
python src/main.py --config my_config.ini

# Override project path
python src/main.py --path /path/to/my/project

# Set maximum token limit
python src/main.py --max-tokens 100000

# Don't open output folder automatically
python src/main.py --no-open
```

### GUI Settings

For a more user-friendly experience, run the settings GUI:

```bash
# On Windows
scripts/run_settings_gui.bat

# On Unix/Linux/macOS
python src/gui/settings.py
```

The GUI offers several tabs:
- **General Settings**: Basic configuration options
- **File Importance**: Define priority for file types, names, and paths
- **API Settings**: Configure API endpoint extraction
- **File Editors**: Edit `.ignore` and `important_files.txt` files directly

## ⚙️ Configuration

The `config.ini` file controls the behavior of the organizer:

```ini
[settings]
path = /path/to/your/project
output_dir = output
ignore = .ignore
important_files_path = important_files.txt
generate_structure = true
max_tokens = 60000
open_output_folder = true

[file_importance]
important_formats = .py,.md,.txt,.json
important_files = README.md,setup.py,config.ini
important_paths = src/,docs/,scripts/

[api_settings]
extract_endpoints = false
```

### Ignore Files

The `.ignore` file uses a syntax similar to `.gitignore` to exclude files and directories:

```
# Directories to exclude (must end with '/')
.git/
__pycache__/
venv/

# Files to exclude
*.pyc
*.log
```

You can edit this file directly within the GUI through the **File Editors** tab.

### Important Files List

The `important_files.txt` file prioritizes specific files and patterns:

```
# Configuration files
config.ini
setup.py

# Documentation
README.md
docs/*.md

# Main entry points
main.py
src/main.py

# Using recursive patterns to include files in subdirectories
src/**/*.py       # All Python files in src and subdirectories
docs/**/*.md      # All Markdown files in docs and subdirectories
**/*.json         # All JSON files anywhere in the project
```

You can edit this file directly within the GUI through the **File Editors** tab.

#### Pattern Matching Guide

| Pattern | Description |
|---------|-------------|
| `folder/*` | Match files directly in the folder |
| `folder/**/*` | Match all files in the folder and all its subdirectories |
| `folder/**/*.py` | Match all Python files in the folder and all its subdirectories |
| `**/*.md` | Match all Markdown files in the entire project |

## 📂 Output Format

The tool generates organized output in:

```
output/
└── project_name/
    └── NNN_project_TIMESTAMP/
        ├── _SUMMARY.txt
        ├── project_name_README.md
        ├── project_name_structure.json
        ├── project_name_endpoints.json (if API extraction enabled)
        └── [flattened project files]
```

## 🧠 Using with Claude AI

1. Run the organizer on your project
2. The tool will automatically open the export folder with organized files
3. Either:
   - Upload the generated files to Claude AI directly
   - Copy the content of the `project_name_structure.json` file
   - Use the generated README to provide context

Claude will then have a token-optimized view of your project structure and most important files.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📇 About me

I'm Sam Schonenberg, I'm 26 years old and I'm autistic, I recenelty lost my job and it's difficult finding new work, because I have difficulties leaving the house, so I'm currently trying my hands on freelancing. I have been working on software projects since I'm 7 and I speak Dutch, German and English on a native level.

[LinkedIn Profile](https://www.linkedin.com/in/sams98/)  
📬 Email: [sam@schonenberg.dev](mailto:sam@schonenberg.dev)

I'm currently open to new opportunities, freelance projects, or collaborations.  
Feel free to reach out if you're interested in working together!