"""Main entry point for PDF processing system testing."""

import json
import os
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import sys
import subprocess
import logging

try:
    import pyperclip
except ImportError:
    pyperclip = None
    print("Warning: pyperclip not installed. Clipboard functionality disabled.")

from dotenv import load_dotenv
from swarm import Swarm

# Change to use local imports
from app.orchestrator import Orchestrator
from app.utils.logging_config import setup_logger

# Set up logger
logger = setup_logger("main_debug")
logging.getLogger().setLevel(logging.DEBUG)  # Set root logger to DEBUG level

# Load environment variables
load_dotenv()

# Load default values from JSON files
try:
    with open('pdf.json', 'r') as f:
        pdf_data = json.load(f)
        DEFAULT_PDF_TEXT = pdf_data.get('pdf_text', '')
except Exception as e:
    logger.error(f"Error loading pdf.json: {str(e)}")
    DEFAULT_PDF_TEXT = """
        This is a sample PDF text.
        It contains information about testing the Swarm agent system.
        The purpose is to verify that all agents are working correctly.
    """

try:
    with open('prompt.json', 'r') as f:
        prompt_data = json.load(f)
        DEFAULT_PROMPT = prompt_data.get('prompt', 'Summarize this document and verify its structure.')
except Exception as e:
    logger.error(f"Error loading prompt.json: {str(e)}")
    DEFAULT_PROMPT = "Summarize this document and verify its structure."

def copy_to_clipboard(text):
    """Copy text to clipboard based on platform."""
    try:
        platform = sys.platform
        if platform == 'darwin':  # macOS
            cmd = ['pbcopy']
            subprocess.run(cmd, input=text.encode('utf-8'), check=True)
            return True
        elif platform == 'win32':  # Windows
            cmd = ['clip']
            subprocess.run(cmd, input=text.encode('utf-8'), check=True)
            return True
        elif platform.startswith('linux'):  # Linux
            cmd = ['xclip', '-selection', 'clipboard']
            subprocess.run(cmd, input=text.encode('utf-8'), check=True)
            return True
        else:
            logger.error(f"Unsupported platform for clipboard: {platform}")
            return False
    except Exception as e:
        logger.error(f"Failed to copy to clipboard: {str(e)}")
        return False

def save_to_json(data, pdf_name, prompt):
    """Save data to a JSON file with name based on PDF and prompt."""
    # Clean the prompt and PDF name for filename
    pdf_name = ''.join(c if c.isalnum() else '_' for c in pdf_name)
    prompt_text = ''.join(c if c.isalnum() else '_' for c in prompt[:30])
    
    # Create results directory if it doesn't exist
    os.makedirs("results", exist_ok=True)
    
    # Create filename with timestamp to avoid overwriting
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/result_{pdf_name}_{prompt_text}_{timestamp}.json"
    
    # Save the data
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, indent=2, ensure_ascii=False, default=str, fp=f)
    
    logger.info(f"Results saved to: {filename}")
    return filename

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
    """Run the PDF processing system."""
    logger.info("Starting PDF processing system debug...")
    
    try:
        logger.info("Creating orchestrator...")
        orchestrator = Orchestrator()
        
        # Log node status before processing
        logger.info("--- NODE STATUS ---")
        node_status = orchestrator.get_node_status()
        for node_name, status in node_status.items():
            logger.info(f"Node: {node_name} - Status: {status['status']} - Category: {status['category']}")
        
        # Get sample PDF or user-provided PDF
        logger.debug("Getting PDF for processing...")
        pdf_file = input("Enter PDF file path or press Enter to use sample: ")
        
        pdf_text = ""
        if pdf_file:
            try:
                with open(pdf_file, 'r') as f:
                    pdf_text = f.read()
                logger.info(f"PDF file loaded: {pdf_file}")
            except Exception as e:
                logger.error(f"Error loading PDF file: {str(e)}")
                pdf_text = DEFAULT_PDF_TEXT
        else:
            pdf_text = DEFAULT_PDF_TEXT
        
        # Get user prompt or use default
        logger.debug("Getting user prompt...")
        user_prompt = input("Enter prompt or press Enter to use default: ")
        if not user_prompt:
            user_prompt = DEFAULT_PROMPT
        
        # Process the PDF
        logger.info("--- STARTING PROCESS TEST ---")
        logger.info(f"Sample PDF length: {len(pdf_text)} characters")
        logger.info(f"User prompt: {user_prompt}")
        
        # Add handler to intercept logs
        log_records = []
        
        class TransferLogHandler(logging.Handler):
            def emit(self, record):
                if "TRANSFER:" in record.getMessage():
                    log_records.append(record.getMessage())
                    logger.info(f"FLOW TRACKING: {record.getMessage()}")
        
        # Add custom handler
        transfer_handler = TransferLogHandler()
        transfer_handler.setLevel(logging.INFO)
        logging.getLogger("orchestrator").addHandler(transfer_handler)
        
        result = orchestrator.process_pdf(pdf_text, user_prompt)
        
        logger.info("--- PROCESS RESULTS ---")
        logger.info(f"Status: {result.get('status')}")
        
        # Show the flow pattern
        logger.info("--- NODE FLOW ---")
        for transfer in log_records:
            logger.info(f"FLOW: {transfer}")
        
        if result.get('status') == 'error':
            logger.error(f"Error in processing: {result.get('error')}")
        else:
            logger.info(f"Result: {result.get('result')}")
            
            # Copy to clipboard for easy viewing
            try:
                pyperclip.copy(result.get('result', ''))
                logger.info("Result copied to clipboard")
            except Exception as e:
                logger.error(f"Error copying to clipboard: {str(e)}")
            
            # Save results to file
            filename = f"results/result_{pdf_file.replace('/', '_').replace('.', '_')}_{user_prompt.replace(' ', '_')[:20]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("results", exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"\nResults saved to: {filename}")
            print("Result has been copied to clipboard")
        
        # Log metadata
        logger.info("--- METADATA ---")
        node_history = result.get('metadata', {}).get('node_history', [])
        logger.info(f"Node history: {node_history}")
        
        node_notes = result.get('metadata', {}).get('node_notes', [])
        logger.info(f"Node notes: {node_notes}")
        
        node_errors = result.get('metadata', {}).get('node_error', [])
        logger.info(f"Node errors: {node_errors}")
        
        processing_time = result.get('metadata', {}).get('processing_time', {})
        logger.info(f"Start time: {processing_time.get('start')}")
        logger.info(f"End time: {processing_time.get('end')}")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 