"""
Logging functionality for Claude AI File Organizer.
"""

import os
import logging
import datetime
from pathlib import Path


def setup_logger(log_dir="logs", log_level=logging.INFO):
    """
    Set up logging for the application.
    
    Args:
        log_dir (str): Directory to store log files
        log_level (int): Logging level (e.g., logging.INFO, logging.DEBUG)
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"organizer_{timestamp}.log"
    
    # Configure logger
    logger = logging.getLogger("claude_ai_file_organizer")
    logger.setLevel(log_level)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger


def log_exception(logger, e, context=""):
    """
    Log exception with detailed information.
    
    Args:
        logger (logging.Logger): Logger instance
        e (Exception): Exception to log
        context (str): Context description where the exception occurred
    """
    if context:
        logger.error(f"Error in {context}: {str(e)}", exc_info=True)
    else:
        logger.error(f"Error: {str(e)}", exc_info=True)