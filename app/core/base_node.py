"""
Core node infrastructure for PDF processing system using Swarm agents.
"""

import os
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from pydantic import Field
from swarm import Agent


class NodeCategory(Enum):
    """Node categories for PDF processing system."""
    
    # Core Processing Categories
    MANAGER = "manager"
    ENHANCEMENT = "enhancement"
    PROCESSING = "processing"
    VALIDATION = "validation"
    REVIEW = "review"
    COMPLETION = "completion"


class NodeBase:
    """Base class for all processing nodes."""

    def __init__(
        self,
        category: NodeCategory,
        name: str,
        instructions: str,
        functions: List[Any] = None
    ):
        """Initialize the base node.
        
        Args:
            category: Node category
            name: Node name
            instructions: Node instructions
            functions: List of node functions
        """
        self.category = category
        self.name = name
        self.instructions = instructions
        self.functions = functions or []
        self.available_nodes: Dict[str, Any] = {}

    def update_context(
        self,
        context: Dict[str, Any],
        status: str,
        message: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Update the processing context.
        
        Args:
            context: Current context
            status: New status
            message: Status message
            **kwargs: Additional context updates
            
        Returns:
            Dict[str, Any]: Updated context
        """
        return {
            **context,
            "status": status,
            "message": message,
            **kwargs
        }

    @property
    def uses_swarm(self) -> bool:
        """Indicate if node uses Swarm for processing.
        
        Returns:
            bool: True if node uses Swarm, False otherwise
        """
        return True

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute node's processing logic.
        
        Args:
            context: Current processing context
            
        Returns:
            Dict[str, Any]: Updated context after processing
            
        Raises:
            NotImplementedError: Must be implemented by child classes
        """
        raise NotImplementedError

    def _create_agent(self) -> Optional[Agent]:
        """Create the Swarm agent for this node.
        
        Returns:
            Optional[Agent]: The created Swarm agent or None if not using Swarm
            
        Raises:
            ValueError: If required API keys are not set
        """
        if not self.uses_swarm:
            return None
            
        # Get API keys from environment
        swarm_api_key = os.getenv("SWARM_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not swarm_api_key:
            raise ValueError("SWARM_API_KEY environment variable is not set")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
            
        # Create agent with instructions and API keys
        agent = Agent(
            name=self.name,
            instructions=self.instructions,
            api_key=swarm_api_key,
            openai_api_key=openai_api_key
        )
        
        return agent 