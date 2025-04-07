"""Main entry point for PDF processing system."""

import logging
from typing import Any, Dict

from .orchestrator import Orchestrator
from .utils.logging_config import setup_logger

logger = setup_logger("main")

def process_document(pdf_text: str, user_prompt: str) -> Dict[str, Any]:
    """Process a PDF document using the Swarm system.
    
    Args:
        pdf_text: The PDF content to process
        user_prompt: The user's processing request
        
    Returns:
        Dict[str, Any]: Processing results and metadata
    """
    try:
        # Initialize orchestrator
        orchestrator = Orchestrator()
        
        # Process the PDF
        result = orchestrator.process_pdf(pdf_text, user_prompt)
        
        # Log node status
        node_status = orchestrator.get_node_status()
        logger.info(f"Node status after processing: {node_status}")
        
        return result
        
    except Exception as e:
        logger.error(f"PDF processing failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "metadata": {
                "node_history": [],
                "node_notes": [],
                "node_error": [str(e)]
            }
        }

if __name__ == "__main__":
    # Example usage
    sample_pdf = "Sample PDF content for testing."
    sample_prompt = "Analyze this text and provide a summary."
    
    result = process_document(sample_pdf, sample_prompt)
    print(f"Processing result: {result}") 