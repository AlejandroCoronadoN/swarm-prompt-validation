"""Validation node for PDF processing system."""

import logging
from typing import Any, ClassVar, Dict, Optional

from swarm import Agent

from ..core.base_node import NodeBase, NodeCategory
from ..models.pdf_context import PDFContext
from ..utils.logging_config import setup_logger


class ValidationNode(NodeBase):
    """Validation node for verifying processing results.
    
    This node is responsible for:
    1. Validating generated responses
    2. Checking accuracy against PDF content
    3. Ensuring all requirements are met
    4. Determining if review is needed
    """
    
    # Class-level logger
    logger: ClassVar[logging.Logger] = setup_logger("validation_node")
    
    def __init__(self) -> None:
        """Initialize the validation node."""
        super().__init__(
            category=NodeCategory.VALIDATION,
            name="ValidationNode",
            instructions="""
            You are the validation node for PDF processing. Your responsibilities are:
            1. Validate processed content
            2. Transfer to completion if valid
            3. Transfer to review if issues found
            """
        )
        self.available_nodes: Dict[str, Dict[str, Any]] = {}
        self.agent = self._create_agent()
        self.logger.info("Validation node initialized")

    @property
    def uses_swarm(self) -> bool:
        return True

    def _create_agent(self) -> Agent:
        return Agent(
            name=self.name,
            instructions=self.instructions,
            functions=[
                self.transfer_to_completion,
                self.transfer_to_review
            ]
        )

    def transfer_to_completion(self, context: Dict[str, Any]) -> Agent:
        """Transfer to completion node if validation passes."""
        self.update_context(
            context,
            status="success",
            message="Validation passed, transferring to completion"
        )
        return self.available_nodes["completion"].agent

    def transfer_to_review(self, context: Dict[str, Any]) -> Agent:
        """Transfer to review node if validation fails."""
        self.update_context(
            context,
            status="review_needed",
            message="Validation failed, transferring to review"
        )
        return self.available_nodes["review"].agent

    def handle_error(self, context: Dict[str, Any]) -> Agent:
        """Handle validation errors.
        
        Args:
            context: Current processing context
            
        Returns:
            Agent: The current node (self) to handle the error
        """
        self.logger.error("Validation error occurred")
        context.update({
            "status": "error",
            "message": "Validation failed",
            "node_error": ["Validation failed"],
            "validation_failed": True
        })
        return self 