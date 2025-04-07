"""Logger utility module for the PDF processing system."""

import logging
import os
from typing import Optional


def setup_logger(name: str, log_level: Optional[int] = None) -> logging.Logger:
    """Set up a logger with the specified name and log level.
    
    Args:
        name: The name of the logger
        log_level: The logging level (defaults to INFO if not specified)
        
    Returns:
        logging.Logger: The configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set log level
    if log_level is None:
        log_level = logging.INFO
    logger.setLevel(log_level)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger 