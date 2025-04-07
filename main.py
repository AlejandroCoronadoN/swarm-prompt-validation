"""Main entry point for PDF processing system testing."""

import json
import os
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from swarm import Swarm

# Change to use local imports
from app.orchestrator import Orchestrator
from app.utils.logging_config import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger("main")

def process_pdf(pdf_text: str, user_prompt: str) -> Dict[str, Any]:
    """Process PDF using the orchestrator.
    
    Args:
        pdf_text: The PDF content to process
        user_prompt: The user's processing request
        
    Returns:
        Dict[str, Any]: Processing results
    """
    logger.info("Starting PDF processing")
    
    try:
        # Initialize orchestrator
        orchestrator = Orchestrator()
        
        # Process the PDF
        result = orchestrator.process_pdf(
            pdf_text=pdf_text,
            user_prompt=user_prompt
        )
        
        return {
            "statusCode": 200,
            "body": {
                "response": result.get("result", ""),
                "metadata": {
                    **result.get("metadata", {}),
                    "request_id": str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "statusCode": 500,
            "body": {
                "error": str(e),
                "message": "Processing failed",
                "traceback": traceback.format_exc()
            }
        }

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load JSON file content."""
    with open(file_path, 'r') as f:
        return json.load(f)

def main() -> None:
    """Test the PDF processing system with actual documents."""
    try:
        # Load test documents from local paths
        base_path = Path(__file__).parent
        pdf_content = load_json_file(base_path / "compost_tutorial.json")
        prompt_content = load_json_file(base_path / "prompt.json")
        
        logger.info("Processing test document")
        logger.info(f"PDF length: {len(pdf_content['pdf_text'])}")
        logger.info(f"Prompt: {prompt_content['prompt']}")
        
        # Process the document
        result = process_pdf(
            pdf_text=pdf_content["pdf_text"],
            user_prompt=prompt_content["prompt"]
        )
        
        # Print results
        print("\nProcessing Results:")
        print(json.dumps(result, indent=2))
        
        # Print processing chain if successful
        if result["statusCode"] == 200:
            print("\nProcessing Chain:")
            for entry in result["body"]["metadata"]["node_history"]:
                print(f"- {entry['node']}: {entry['action']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Main execution failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 