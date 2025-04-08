"""Processing node for analyzing enhanced prompts and PDF content."""

import logging
from typing import Any, ClassVar, Dict, Optional

from swarm import Agent

from ..core.base_node import NodeBase, NodeCategory
from ..utils.logging_config import setup_logger


class ProcessingNode(NodeBase):
    """Processing node for analyzing PDF content based on enhanced prompts.
    
    This node is responsible for:
    1. Taking enhanced prompts and PDF content
    2. Extracting relevant information from the PDF
    3. Organizing information according to the enhanced prompt structure
    4. Preparing data for the completion node
    """
    
    # Class-level logger
    logger: ClassVar[logging.Logger] = setup_logger("processing_node")
    
    def __init__(self) -> None:
        """Initialize the processing node."""
        super().__init__(
            category=NodeCategory.PROCESSING,
            name="ProcessingNode",
            instructions="""You are the Processing node for PDF content extraction and organization.
            
            Your role is to analyze the PDF content based on the enhanced prompt,
            extract the most relevant information, and organize it for the completion node.
            
            You will process a dictionary that contains:
            {
                "node_notes": [], <- Enhancement notes
                "node_error": [], <- Enhancement errors if any
                "node_history": [], <- Enhancement history
                "node_status": [], <- Enhancement status
                "response": {
                    "pdf_content": "Extracted PDF content",
                    "original_prompt": "User's original question",
                    "enhanced_prompt": "Detailed enhanced prompt with specific requirements",
                    "content_structure": {
                        "sections": ["Introduction", "Main Analysis", "Conclusion"],
                        "required_elements": ["Citations", "Examples", "Summary"],
                        "formatting": "Description of required formatting"
                    }
                }
            }
            
            PROCESSING STEPS:
            1. Analyze the enhanced prompt to understand requirements
            2. Thoroughly review the PDF content
            3. Extract information relevant to the enhanced prompt
            4. Organize extracted information according to the content structure
            5. Identify key quotes and sections from the PDF for citations
            6. Prepare draft outline based on extracted information
            
            OUTPUT:
            Response:
                "node_notes": [], <- Append processing notes
                "node_error": [], <- Append processing errors if any, or " " if none
                "node_history": [], <- Append processing record
                "node_status": [], <- Append "processing_completed"
                "response": {
                    "pdf_content": "Original PDF content (unchanged)",
                    "original_prompt": "User's original question (unchanged)",
                    "enhanced_prompt": "Enhanced prompt (unchanged)",
                    "content_structure": { ... } <- (unchanged),
                    "extracted_information": {
                        "key_points": ["Point 1", "Point 2", ...],
                        "relevant_quotes": ["Quote 1", "Quote 2", ...],
                        "sections": {
                            "section_name": "Extracted content relevant to this section",
                            ...
                        }
                    },
                    "draft_outline": "Structured outline based on extracted information"
                }
            }
            
            IMPORTANT: Once you have completed the processing steps above, you MUST call the
            transfer_to_validation function to send your output to the Validation node. 
            Do not just return a text response - you must use the function call.
            
            FUNCTION USAGE: After completing your work, call the transfer_to_validation function
            and pass your complete output context to it.
            """,
            functions=[]
        )
        self.available_nodes = {}
        self.logger.info("Processing node initialized")

    @property
    def uses_swarm(self) -> bool:
        return True

    def handle_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle processing errors.
        
        Args:
            context: Current processing context
            
        Returns:
            Dict[str, Any]: Updated context with error information
        """
        self.logger.error("Processing error occurred")
        if isinstance(context, dict):
            context.update({
                "node_status": ["error"] if "node_status" not in context else context["node_status"] + ["error"],
                "node_error": ["ProcessingNode: Processing failed"] if "node_error" not in context else context["node_error"] + ["ProcessingNode: Processing failed"],
            })
        else:
            context = {
                "node_status": ["error"],
                "node_error": ["ProcessingNode: Processing failed"],
                "node_history": [],
                "node_notes": []
            }
        return context 