"""Logging configuration for the application."""

import logging
from typing import Optional


def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Set up a logger with the specified name and level.
    
    Args:
        name: Name for the logger
        level: Optional logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    logger.setLevel(level or logging.INFO)
    return logger 