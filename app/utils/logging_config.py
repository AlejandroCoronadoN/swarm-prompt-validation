"""Logging configuration for the application."""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(name):
    """Set up logger with console and file handlers."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all levels
    
    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create console handler with higher log level for normal operations
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Create debug console handler for detailed debug messages
    debug_console_handler = logging.StreamHandler(sys.stdout)
    debug_console_handler.setLevel(logging.DEBUG)
    # Only display DEBUG level messages
    debug_console_handler.addFilter(lambda record: record.levelno == logging.DEBUG)
    debug_formatter = logging.Formatter(
        '\033[36m%(asctime)s - %(name)s - DEBUG - %(message)s\033[0m'  # Cyan color for DEBUG
    )
    debug_console_handler.setFormatter(debug_formatter)
    logger.addHandler(debug_console_handler)
    
    # Create file handler for all messages
    file_handler = RotatingFileHandler(
        f"logs/{name}.log", 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Extra detailed file handler for swarm-specific messages
    if name.startswith("swarm") or name == "orchestrator" or name == "main_debug":
        swarm_file_handler = RotatingFileHandler(
            "logs/swarm_debug.log", 
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        swarm_file_handler.setLevel(logging.DEBUG)
        swarm_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        swarm_file_handler.setFormatter(swarm_formatter)
        logger.addHandler(swarm_file_handler)
    
    return logger 