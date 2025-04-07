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
    """
    
    # Class-level logger
    logger: ClassVar[logging.Logger] = setup_logger("completion_node")
    
    def __init__(self) -> None:
        """Initialize the completion node."""
        super().__init__(
            category=NodeCategory.COMPLETION,
            name="CompletionNode",
            instructions="""
            You are the completion node for PDF processing. Your responsibilities are:
            1. Finalize processed content
            2. Format final output
            3. Prepare delivery package
            """
        )
        self.available_nodes: Dict[str, Dict[str, Any]] = {}
        self.agent = self._create_agent()
        self.logger.info("Initializing CompletionNode")

    @property
    def uses_swarm(self) -> bool:
        return True

    def _create_agent(self) -> Agent:
        return Agent(
            name=self.name,
            instructions=self.instructions,
            functions=[self.finalize_response]
        )

    def finalize_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the processed response."""
        return self.update_context(
            context,
            status="completed",
            message="Processing completed successfully",
            final_response=context.get("processed_content")
        )

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Agent:
        """Handle errors during completion.
        
        Args:
            error: The error that occurred
            context: Current processing context
            
        Returns:
            Agent: The current node for error management
        """
        self.logger.error(f"Completion error: {str(error)}")
        context["node_status"] = "error"
        context["error"] = str(error)
        return self 