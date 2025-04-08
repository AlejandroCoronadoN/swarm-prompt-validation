"""Validation node for verifying answers based on PDF content."""

import logging
from typing import Any, ClassVar, Dict, List, Optional

from swarm import Agent

from ..core.base_node import NodeBase, NodeCategory
from ..utils.logging_config import setup_logger


class ValidationNode(NodeBase):
    """Validation node for verifying generated answers against source PDF content.
    
    This node is responsible for:
    1. Validating the accuracy of processed content against the source PDF
    2. Identifying any factual errors or inconsistencies
    3. Flagging content that needs improvement
    4. Providing specific feedback for correction
    5. Routing to Review node for error correction or Completion node for final processing
    """
    
    # Class-level logger
    logger: ClassVar[logging.Logger] = setup_logger("validation_node")
    
    def __init__(self) -> None:
        """Initialize the validation node."""
        super().__init__(
            category=NodeCategory.VALIDATION,
            name="ValidationNode",
            instructions="""You are the Validation node for ensuring content accuracy.
            
            Your role is to carefully validate the processed answer against the original PDF 
            content to ensure accuracy, completeness, and adherence to the original prompt.
            
            You will process a dictionary that contains:
            {
                "node_notes": [], <- Previous processing notes
                "node_error": [], <- Previous error list
                "node_history": [], <- Previous processing history
                "node_status": [], <- Previous status
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
                    "answer": "The generated answer to validate"
                }
            }
            
            If you're receiving this context for a second time (during a review cycle), the response may also include:
            {
                "validation_result": {
                    "passed": false,
                    "score": 0-100,
                    "feedback": "Previous validation feedback",
                    "issues": [...]
                },
                "review_notes": "Notes from the review node"
            }
            
            VALIDATION STEPS:
            1. Compare the answer against the PDF content
            2. Check for factual accuracy and completeness
            3. Ensure the answer addresses the original prompt
            4. Identify any mistakes, omissions, or inaccuracies
            5. Check for proper citations and references
            
            ROUTING DECISION:
            - If validation passes (score >= 70): Transfer to Completion node
            - If validation fails (score < 70): Transfer to Review node for correction
            
            OUTPUT:
            Response:
                "node_notes": [], <- Append validation notes (preserving previous notes)
                "node_error": [], <- Append validation errors if any, or " " if none (preserving previous errors)
                "node_history": [], <- Append validation record (preserving previous history)
                "node_status": [], <- Append "validation_passed" or "validation_failed" (preserving previous status)
                "response": {
                    # Preserve all previous content unchanged
                    "pdf_content": the original PDF content (unchanged),
                    "original_prompt": the user's original prompt (unchanged),
                    "enhanced_prompt": "Enhanced prompt (unchanged)",
                    "content_structure": {...} (unchanged),
                    "extracted_information": {...} (unchanged),
                    "draft_outline": "..." (unchanged),
                    "answer": the original answer (unchanged),
                    # Add validation result
                    "validation_result": {
                        "passed": true/false,
                        "score": 0-100,
                        "feedback": "Detailed feedback on the answer",
                        "issues": [
                            {
                                "type": "factual_error/omission/etc.",
                                "description": "Specific issue description",
                                "correction": "Suggested correction"
                            }
                        ]
                    }
                }
            }
            """,
            functions=[]
        )
        self.available_nodes = {}
        self.logger.info("Validation node initialized")

    @property
    def uses_swarm(self) -> bool:
        return True

    def validate_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the content against the PDF source.
        
        Args:
            context: Current processing context
            
        Returns:
            Dict[str, Any]: Updated context with validation results
        """
        self.logger.info("Validating content against PDF source")
        
        try:
            # Add validation logic here
            return context
        except Exception as e:
            self.logger.error(f"Content validation failed: {str(e)}")
            return self.handle_error(context)

    def handle_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validation errors.
        
        Args:
            context: Current validation context
            
        Returns:
            Dict[str, Any]: Updated context with error information
        """
        self.logger.error("Validation error occurred")
        if isinstance(context, dict):
            context.update({
                "node_status": ["error"] if "node_status" not in context else context["node_status"] + ["error"],
                "node_error": ["ValidationNode: Validation failed"] if "node_error" not in context else context["node_error"] + ["ValidationNode: Validation failed"],
            })
        else:
            context = {
                "node_status": ["error"],
                "node_error": ["ValidationNode: Validation failed"],
                "node_history": [],
                "node_notes": []
            }
        return context 