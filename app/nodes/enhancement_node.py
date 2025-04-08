"""Enhancement node for improving prompts."""

import logging
from typing import Any, ClassVar, Dict, List, Optional

from swarm import Agent

from ..core.base_node import NodeBase, NodeCategory
from ..utils.logging_config import setup_logger


class EnhancementNode(NodeBase):
    """Enhancement node for improving and structuring prompts.
    
    This node is responsible for:
    1. Analyzing the user's prompt and PDF content
    2. Enhancing the prompt with specific requirements and formatting
    3. Creating a structured approach for generating answers
    4. Ensuring clarity and specificity in the prompt
    """
    
    # Class-level logger
    logger: ClassVar[logging.Logger] = setup_logger("enhancement_node")
    
    def __init__(self) -> None:
        """Initialize the enhancement node."""
        super().__init__(
            category=NodeCategory.ENHANCEMENT,
            name="EnhancementNode",
            instructions="""You are the Enhancement node for prompt improvement.
            
            Your role is to analyze the user's prompt and PDF content to create
            an enhanced, more specific prompt that will guide the completion node.
            
            You will process a dictionary that contains:
            {
                "node_notes": [], <- Initial or previous processing notes
                "node_error": [], <- Initial or previous error list
                "node_history": [], <- Initial or previous processing history
                "node_status": [], <- Initial or previous status
                "response": {
                    "pdf_content": "Extracted PDF content",
                    "original_prompt": "User's original question"
                }
            }
            
            ENHANCEMENT STEPS:
            1. Analyze the user's original prompt to understand their question
            2. Identify key topics and requirements from the prompt
            3. Review the PDF content to understand available information
            4. Create a structured, enhanced prompt that:
               - Clarifies ambiguous aspects of the original prompt
               - Specifies required formats for the answer (lists, sections, etc.)
               - Identifies specific information to include from the PDF
               - Adds requirements for citations or references to the PDF
            5. Outline content structure with specific sections to include
            
            OUTPUT:
            Response:
                "node_notes": [], <- Append enhancement notes
                "node_error": [], <- Append enhancement errors if any, or " " if none
                "node_history": [], <- Append enhancement record
                "node_status": [], <- Append "enhancement_completed" 
                "response": {
                    "pdf_content": "Original PDF content (unchanged)",
                    "original_prompt": "User's original question (unchanged)",
                    "enhanced_prompt": "Detailed enhanced prompt with specific requirements",
                    "content_structure": {
                        "sections": ["Introduction", "Main Analysis", "Conclusion"],
                        "required_elements": ["Citations", "Examples", "Summary"],
                        "formatting": "Description of required formatting"
                    }
                }
            }
            
            IMPORTANT: Once you have completed your analysis and enhancement of the prompt, 
            you MUST call the transfer_to_processing function to send your output to the 
            Processing node. Do not just return a text response - you must use the function call.
            
            FUNCTION USAGE: After completing your work, call the transfer_to_processing function 
            and pass your complete output context to it.
            """,
            functions=[]
        )
        self.available_nodes = {}
        self.logger.info("Enhancement node initialized")

    @property
    def uses_swarm(self) -> bool:
        return True

    def handle_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle enhancement errors.
        
        Args:
            context: Current enhancement context
            
        Returns:
            Dict[str, Any]: Updated context with error information
        """
        self.logger.error("Enhancement error occurred")
        if isinstance(context, dict):
            context.update({
                "node_status": ["error"] if "node_status" not in context else context["node_status"] + ["error"],
                "node_error": ["EnhancementNode: Enhancement failed"] if "node_error" not in context else context["node_error"] + ["EnhancementNode: Enhancement failed"],
            })
        else:
            context = {
                "node_status": ["error"],
                "node_error": ["EnhancementNode: Enhancement failed"],
                "node_history": [],
                "node_notes": []
            }
        return context 