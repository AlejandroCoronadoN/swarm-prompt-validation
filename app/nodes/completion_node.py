"""Completion node for PDF processing system."""

import logging
from typing import Any, ClassVar, Dict, Optional

from swarm import Agent

from ..core.base_node import NodeBase, NodeCategory
from ..utils.logging_config import setup_logger


class CompletionNode(NodeBase):
    """Completion node that finalizes the PDF processing workflow.
    
    Responsibilities:
    - Finalizes the processing results
    - Ensures all required information is present
    - Prepares the final response
    - Handles completion-specific errors
    - Summarizes the entire processing workflow
    """
    
    # Class-level logger
    logger: ClassVar[logging.Logger] = setup_logger("completion_node")
    
    def __init__(self) -> None:
        """Initialize the completion node."""
        super().__init__(
            category=NodeCategory.COMPLETION,
            name="CompletionNode",
            instructions="""You are the Completion node for PDF processing. 
            
            Your role is to finalize the validated answer and prepare it for delivery to the user.
            
            You will process a dictionary that contains:
            {
                "node_notes": [], <- Processing chain notes
                "node_error": [], <- Processing chain errors
                "node_history": [], <- Processing chain history
                "node_status": [], <- Processing chain status
                "response": {
                    "pdf_content": "Original PDF content",
                    "original_prompt": "User's original question",
                    "enhanced_prompt": "Enhanced prompt with requirements",
                    "content_structure": {
                        "sections": [...],
                        "required_elements": [...],
                        "formatting": "..."
                    },
                    "extracted_information": {
                        "key_points": [...],
                        "relevant_quotes": [...],
                        "sections": {...}
                    },
                    "draft_outline": "Structured outline",
                    "answer": "The validated answer",
                    "validation_result": {
                        "passed": true,
                        "score": 0-100,
                        "feedback": "Validation feedback"
                    }
                }
            }
            
            COMPLETION STEPS:
            1. Review all the processing history and notes
            2. Ensure the answer is complete and addresses the original user prompt
            3. Format the answer appropriately for user consumption
            4. Add any necessary context or explanations
            5. Create a final, polished response
            
            OUTPUT:
            Response:
                "node_notes": [], <- Append completion notes (preserving previous notes)
                "node_error": [], <- Append completion errors if any, or " " if none (preserving previous errors)
                "node_history": [], <- Append completion record (preserving previous history)
                "node_status": [], <- Append "completion_finished" (preserving previous status)
                "response": {
                    # Preserve all previous content
                    "pdf_content": "Original PDF content" (unchanged),
                    "original_prompt": "User's original question" (unchanged),
                    "enhanced_prompt": "Enhanced prompt" (unchanged),
                    "content_structure": {...} (unchanged),
                    "extracted_information": {...} (unchanged),
                    "draft_outline": "..." (unchanged),
                    "validation_result": {...} (unchanged),
                    
                    # Update the answer field with final version
                    "answer": "The final, polished answer ready for the user",
                    
                    # Add completion information
                    "processing_summary": "Summary of the entire processing workflow",
                    "completion_timestamp": "Timestamp of completion"
                }
            }
            """,
            functions=[]
        )
        self.available_nodes: Dict[str, Dict[str, Any]] = {}
        self.logger.info("Initializing CompletionNode")

    @property
    def uses_swarm(self) -> bool:
        return True

    def finalize_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the processed response.
        
        Args:
            context: Current processing context
            
        Returns:
            Dict[str, Any]: Final context with completed response
        """
        self.logger.info("Finalizing response")
        
        try:
            if isinstance(context, dict):
                context.update({
                    "node_status": context.get("node_status", []) + ["completion_finished"],
                    "node_history": context.get("node_history", []) + ["CompletionNode: Finalized response"],
                    "node_notes": context.get("node_notes", []) + ["Response finalized for user delivery"]
                })
            return context
        except Exception as e:
            self.logger.error(f"Response finalization failed: {str(e)}")
            return self.handle_error(e, context)

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle errors during completion.
        
        Args:
            error: The error that occurred
            context: Current processing context
            
        Returns:
            Dict[str, Any]: Updated context with error information
        """
        self.logger.error(f"Completion error: {str(error)}")
        if isinstance(context, dict):
            context.update({
                "node_status": ["error"] if "node_status" not in context else context["node_status"] + ["error"],
                "node_error": ["CompletionNode: Completion failed"] if "node_error" not in context else context["node_error"] + ["CompletionNode: Completion failed"],
            })
        else:
            context = {
                "node_status": ["error"],
                "node_error": [f"CompletionNode: {str(error)}"],
                "node_history": [],
                "node_notes": []
            }
        return context 