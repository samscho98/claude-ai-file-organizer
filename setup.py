from setuptools import setup, find_packages

setup(
    name="claude-ai-file-organizer",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # No hard dependencies for core functionality
        "setuptools>=42.0.0",  # Required for installation
    ],
    extras_require={
        "token_counting": ["tiktoken>=0.3.0"],
        "api_extraction": ["PyYAML>=6.0"],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
        ],
        "all": [
            "tiktoken>=0.3.0",
            "PyYAML>=6.0",
        ],
    },
)