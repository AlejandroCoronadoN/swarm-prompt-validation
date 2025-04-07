"""Manager node for PDF processing system."""

import json
import logging
from typing import Any, ClassVar, Dict, Optional

from swarm import Agent

from ..core.base_node import NodeBase, NodeCategory
from ..utils.logging_config import setup_logger


class ManagerNode(NodeBase):
    """Manager node for coordinating PDF processing."""
    
    # Properly annotate logger as ClassVar
    logger: ClassVar[logging.Logger] = setup_logger("manager_node")
    
    def __init__(self, available_nodes: Dict[str, Any]) -> None:
        """Initialize the manager node."""
        def validate_input(context: Dict[str, Any]) -> Dict[str, Any]:
            """Validate the input before processing."""
            self.logger.info("Validating input")
            # Do validation work here
            return {
                "role": "function",
                "name": "validate_input",
                "content": {
                    "validation_result": "valid",
                    "next_step": "enhancement"
                }
            }

        super().__init__(
            category=NodeCategory.MANAGER,
            name="ManagerNode",
            instructions="""
            You are the manager node for PDF processing.
            1. First validate the input using validate_input
            2. If valid, transfer to enhancement using transfer_to_enhancement
            """,
            functions=[validate_input]  # Node's processing functions
        )
        self.available_nodes = available_nodes
        self.logger.info("Manager node initialized")
    
    @property
    def uses_swarm(self) -> bool:
        return True

    def _create_agent(self) -> Agent:
        return Agent(
            name=self.name,
            instructions=self.instructions,
            functions=[self.transfer_to_enhancement]
        )

    def transfer_to_enhancement(self, context: Dict[str, Any]) -> Agent:
        """Transfer to enhancement node."""
        self.update_context(
            context,
            status="success",
            message="Transferring to enhancement node"
        )
        return self.available_nodes["enhancement"].agent
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Agent:
        """Handle errors during processing.
        
        Args:
            error: The error that occurred
            context: Current processing context
            
        Returns:
            Agent: The current node for error management
        """
        self.logger.error(f"Manager error: {str(error)}")
        context["node_status"] = "error"
        context["error"] = str(error)
        return self

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message."""
        self.logger.info("Processing message in ManagerNode")
        self.logger.debug(f"Message content length: {len(str(message.get('content', '')))}")
        # Process message
        result = super().process_message(message)
        self.logger.info("ManagerNode completed processing")
        return result 