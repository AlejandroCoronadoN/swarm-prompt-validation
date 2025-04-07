"""Enhancement node for PDF processing system."""

import logging
from typing import Any, ClassVar, Dict, Optional

from swarm import Agent

from ..core.base_node import NodeBase, NodeCategory
from ..models.pdf_context import PDFContext
from ..utils.logging_config import setup_logger


class EnhancementNode(NodeBase):
    """Enhancement node for improving prompts and analyzing PDF content.
    
    This node is responsible for:
    1. Analyzing PDF content for key information
    2. Enhancing the user's prompt with additional context
    3. Identifying potential issues or missing information
    4. Preparing the context for the processing node
    """
    
    # Class-level logger
    logger: ClassVar[logging.Logger] = setup_logger("enhancement_node")
    
    def __init__(self) -> None:
        """Initialize the enhancement node."""
        super().__init__(
            category=NodeCategory.ENHANCEMENT,
            name="EnhancementNode",
            instructions="""
            You are the enhancement node for PDF processing. Your responsibilities are:
            1. Analyze PDF content
            2. Enhance user prompts
            3. Transfer to processing node
            """
        )
        self.available_nodes: Dict[str, Dict[str, Any]] = {}
        self.agent = self._create_agent()
        self.logger.info("Enhancement node initialized")

    @property
    def uses_swarm(self) -> bool:
        return True

    def _create_agent(self) -> Agent:
        return Agent(
            name=self.name,
            instructions=self.instructions,
            functions=[self.transfer_to_processing]
        )

    def transfer_to_processing(self, context: Dict[str, Any]) -> Agent:
        """Transfer to processing node."""
        self.update_context(
            context,
            status="success",
            message="Transferring to processing node"
        )
        return self.available_nodes["processing"].agent

    def handle_error(self, context: Dict[str, Any]) -> Agent:
        """Handle enhancement errors.
        
        Args:
            context: Current processing context
            
        Returns:
            Agent: The current node (self) to handle the error
        """
        self.logger.error("Enhancement error occurred")
        context.update({
            "status": "error",
            "message": "Enhancement failed",
            "node_error": ["Enhancement failed"],
            "validation_failed": True
        })
        return self 