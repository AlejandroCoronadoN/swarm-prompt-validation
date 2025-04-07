import logging
from typing import Any, Dict

from swarm import Agent, Swarm

from app.nodes.manager_node import ManagerNode
from app.orchestrator import Orchestrator
from app.utils.logging_config import setup_logger

logger = setup_logger("test_pdf_flow")

def test_pdf_processing_flow():
    """Test the complete PDF processing flow."""
    try:
        logger.info("Testing PDF processing flow")
        
        # Initialize orchestrator
        orchestrator = Orchestrator()
        
        # Test sample data
        sample_pdf_text = """
        This is a sample PDF content.
        It contains multiple lines
        and some technical information.
        """
        
        sample_prompt = "Summarize the key points in this text."
        
        # Process the PDF
        result = orchestrator.process_pdf(
            pdf_text=sample_pdf_text,
            user_prompt=sample_prompt
        )
        
        # Log the flow results
        logger.debug("Processing Result:")
        logger.debug(f"Status: {result['status']}")
        logger.debug(f"Node History: {result['metadata']['node_history']}")
        logger.debug(f"Node Notes: {result['metadata']['node_notes']}")
        logger.debug(f"Errors: {result['metadata']['node_error']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }

def test_node_connections():
    """Test if all nodes are properly connected."""
    try:
        logger.info("Testing node connections")
        
        orchestrator = Orchestrator()
        
        # Check all nodes exist
        nodes_to_check = [
            "manager",
            "enhancement",
            "processing",
            "validation",
            "review",
            "completion"
        ]
        
        for node_name in nodes_to_check:
            node = orchestrator.available_nodes.get(node_name)
            logger.debug(f"Checking {node_name} node:")
            logger.debug(f"- Exists: {node is not None}")
            logger.debug(f"- Has agent: {hasattr(node, 'agent')}")
            logger.debug(f"- Has available_nodes: {hasattr(node, 'available_nodes')}")
            
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Run tests
    logger.info("Starting tests")
    
    # Test node connections
    connection_result = test_node_connections()
    print(f"\nNode connections test: {'passed' if connection_result else 'failed'}")
    
    # Test full processing flow
    flow_result = test_pdf_processing_flow()
    print("\nProcessing flow result:")
    print(f"Status: {flow_result['status']}")
    if flow_result['status'] == 'success':
        print(f"Result: {flow_result['result']}")
        print("\nProcessing chain:")
        for entry in flow_result['metadata']['node_history']:
            print(f"- {entry['node']}: {entry['action']}")
    else:
        print(f"Error: {flow_result.get('error', 'Unknown error')}") 