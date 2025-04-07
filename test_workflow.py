"""Test script for PDF processing workflow."""

import os
import traceback
from typing import Dict, Any

from dotenv import load_dotenv
from app.nodes.completion_node import CompletionNode
from app.nodes.enhancement_node import EnhancementNode
from app.nodes.manager_node import ManagerNode
from app.nodes.processing_node import ProcessingNode
from app.nodes.review_node import ReviewNode
from app.nodes.validation_node import ValidationNode
from swarm import Swarm

# Load environment variables
load_dotenv()


def initialize_nodes() -> ManagerNode:
    """Initialize all nodes in the processing chain.
    
    Returns:
        ManagerNode: The initialized manager node
    """
    # Initialize nodes
    completion_node = CompletionNode()
    validation_node = ValidationNode()
    processing_node = ProcessingNode()
    enhancement_node = EnhancementNode()
    review_node = ReviewNode()
    manager_node = ManagerNode()
    
    return manager_node


def prepare_context(pdf_text: str, user_prompt: str) -> Dict[str, Any]:
    """Prepare the initial context for processing.
    
    Args:
        pdf_text: The PDF content to process
        user_prompt: The user's processing request
        
    Returns:
        Dict[str, Any]: The prepared context
    """
    return {
        "pdf_text": pdf_text,
        "user_prompt": user_prompt,
        "node_history": [],
        "node_notes": [],
        "node_status": "pending",
        "processing_metadata": {
            "start_time": "2024-03-21T00:00:00Z",
            "source": "test",
            "version": "1.0"
        },
        "next_node": None  # Will be set during processing
    }


def update_context_history(
    context: Dict[str, Any],
    node_name: str,
    action: str,
    note: str
) -> Dict[str, Any]:
    """Update context with node history and notes.
    
    Args:
        context: Current context
        node_name: Name of the node
        action: Action performed
        note: Note about the action
        
    Returns:
        Dict[str, Any]: Updated context
    """
    context["node_history"].append({
        "node": node_name,
        "action": action,
        "timestamp": "2024-03-21T00:00:00Z"
    })
    context["node_notes"].append(f"[{node_name}] {note}")
    return context


def main():
    """Run the PDF processing workflow."""
    try:
        # Print environment variables (without sensitive values)
        print("\nEnvironment Configuration:")
        print(f"OPENAI_API_KEY set: {'OPENAI_API_KEY' in os.environ}")
        print(f"SWARM_API_KEY set: {'SWARM_API_KEY' in os.environ}")
        
        # Initialize nodes
        print("\nInitializing nodes...")
        manager_node = initialize_nodes()
        
        # Prepare test data
        print("\nPreparing test data...")
        pdf_text = "This is a test PDF content. It contains important information."
        user_prompt = "What is the main topic of this PDF?"
        
        # Prepare context
        print("\nPreparing context...")
        context = prepare_context(pdf_text, user_prompt)
        
        # Initialize Swarm client
        print("\nInitializing Swarm client...")
        swarm = Swarm()
        print("Swarm client initialized")
        
        try:
            # Run processing with manager node
            print("\nStarting processing...")
            result = swarm.run(
                agent=manager_node,
                messages=[{
                    "role": "user",
                    "content": f"PDF Content: {pdf_text}\nUser Prompt: {user_prompt}",
                    "context": context
                }]
            )
            
            # Print results
            print("\nProcessing Results:")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"Message: {result.get('message', 'No message')}")
            print("\nNode History:")
            for entry in result.get("node_history", []):
                print(f"- {entry['node']}: {entry['action']}")
            print("\nNode Notes:")
            for note in result.get("node_notes", []):
                print(f"- {note}")
                
        except Exception as e:
            print(f"\nError during Swarm processing:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("\nTraceback:")
            traceback.print_exc()
            
    except Exception as e:
        print(f"\nError during setup:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()


if __name__ == "__main__":
    main() 