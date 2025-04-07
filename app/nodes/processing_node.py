"""Processing node for PDF processing system."""

import json
import logging
from typing import Any, ClassVar, Dict, Optional

from swarm import Agent

from ..core.base_node import NodeBase, NodeCategory
from ..utils.logging_config import setup_logger


class ProcessingNode(NodeBase):
    """Processing node for generating responses from PDF content.
    
    This node is responsible for:
    1. Processing the enhanced prompt
    2. Generating a response based on PDF content
    3. Ensuring response quality and accuracy
    4. Preparing for validation
    """
    
    # Class-level logger
    logger: ClassVar[logging.Logger] = setup_logger("processing_node")
    
    def __init__(self) -> None:
        """Initialize the processing node."""
        super().__init__(
            category=NodeCategory.PROCESSING,
            name="ProcessingNode",
            instructions="""
            You are the processing node for PDF content. Your responsibilities are:
            1. Process enhanced PDF content
            2. Generate responses based on user prompts
            3. Transfer processed content for validation
            """,
            functions=[]  # Functions will be set when connecting nodes
        )
        self.available_nodes: Dict[str, Any] = {}
        self.agent = self._create_agent()
        self.logger.info("Processing node initialized")

    @property
    def uses_swarm(self) -> bool:
        return True

    def _create_agent(self) -> Agent:
        return Agent(
            name=self.name,
            instructions=self.instructions,
            functions=[self.transfer_to_validation]
        )

    def transfer_to_validation(self, context: Dict[str, Any]) -> Agent:
        """Transfer to validation node."""
        self.update_context(
            context,
            status="success",
            message="Transferring to validation node"
        )
        return self.available_nodes["validation"].agent

    def handle_error(self, context: Dict[str, Any]) -> Agent:
        """Handle processing errors.
        
        Args:
            context: Current processing context
            
        Returns:
            Agent: The current node (self) to handle the error
        """
        self.logger.error("Processing error occurred")
        context.update({
            "status": "error",
            "message": "Processing failed",
            "node_error": ["Processing failed"],
            "validation_failed": True
        })
        return self 