"""Orchestrator for PDF processing system using Swarm."""

import logging
from datetime import datetime
from typing import Any, Dict

from swarm import Agent, Swarm

from .nodes.completion_node import CompletionNode
from .nodes.enhancement_node import EnhancementNode
from .nodes.manager_node import ManagerNode
from .nodes.processing_node import ProcessingNode
from .nodes.review_node import ReviewNode
from .nodes.validation_node import ValidationNode
from .utils.logging_config import setup_logger


class Orchestrator:
    """Orchestrates the PDF processing system using Swarm agents."""

    logger = setup_logger("orchestrator")

    def __init__(self):
        """Initialize the orchestrator with all nodes."""
        self.logger.info("Initializing Orchestrator")
        
        # Initialize Swarm client
        self.client = Swarm()

        # Define transfer functions for each node
        self._define_transfer_functions()

        # Create nodes in reverse order (to handle dependencies)
        self.completion_node = CompletionNode()
        self.completion_node.agent = self._create_completion_agent()

        self.review_node = ReviewNode()
        self.review_node.agent = self._create_review_agent()

        self.validation_node = ValidationNode()
        self.validation_node.agent = self._create_validation_agent()

        self.processing_node = ProcessingNode()
        self.processing_node.agent = self._create_processing_agent()

        self.enhancement_node = EnhancementNode()
        self.enhancement_node.agent = self._create_enhancement_agent()

        # Create available nodes dictionary
        self.available_nodes = {
            "enhancement": self.enhancement_node,
            "processing": self.processing_node,
            "validation": self.validation_node,
            "review": self.review_node,
            "completion": self.completion_node
        }

        # Initialize manager with available nodes and its agent
        self.manager_node = ManagerNode(self.available_nodes)
        self.manager_node.agent = self._create_manager_agent()
        
        # Add manager to available nodes for review->manager connection
        self.available_nodes["manager"] = self.manager_node

        self.logger.info("All nodes initialized and connected")

    def _define_transfer_functions(self):
        """Define transfer functions for node connections."""
        
        def transfer_to_enhancement(context: Dict[str, Any]) -> Agent:
            """Transfer from manager to enhancement."""
            self.logger.info("Transferring to enhancement node")
            return self.enhancement_node.agent

        def transfer_to_processing(context: Dict[str, Any]) -> Agent:
            """Transfer from enhancement to processing."""
            self.logger.info("Transferring to processing node")
            return self.processing_node.agent

        def transfer_to_validation(context: Dict[str, Any]) -> Agent:
            """Transfer from processing to validation."""
            self.logger.info("Transferring to validation node")
            return self.validation_node.agent

        def transfer_to_review(context: Dict[str, Any]) -> Agent:
            """Transfer from validation to review (on failure)."""
            self.logger.info("Transferring to review node")
            return self.review_node.agent

        def transfer_to_completion(context: Dict[str, Any]) -> Agent:
            """Transfer from validation to completion (on success)."""
            self.logger.info("Transferring to completion node")
            return self.completion_node.agent

        def transfer_to_manager(context: Dict[str, Any]) -> Agent:
            """Transfer from review back to manager."""
            self.logger.info("Transferring back to manager node")
            return self.manager_node.agent

        self.transfer_functions = {
            "to_enhancement": transfer_to_enhancement,
            "to_processing": transfer_to_processing,
            "to_validation": transfer_to_validation,
            "to_review": transfer_to_review,
            "to_completion": transfer_to_completion,
            "to_manager": transfer_to_manager
        }

    def _create_manager_agent(self) -> Agent:
        """Create manager node agent."""
        def process_pdf_content(context: Dict[str, Any]) -> Dict[str, Any]:
            """Process the PDF content."""
            self.logger.info("Processing PDF content in manager")
            if not context.get("pdf_text"):
                return {
                    "role": "function",
                    "name": "process_pdf_content",
                    "content": "Error: No PDF text provided"
                }
            return {
                "role": "function",
                "name": "process_pdf_content",
                "content": "PDF content validated, ready for enhancement"
            }

        return Agent(
            name="ManagerNode",
            instructions=self.manager_node.instructions,
            functions=[
                self.transfer_functions["to_enhancement"]
            ]
        )

    def _create_enhancement_agent(self) -> Agent:
        """Create enhancement node agent."""
        def enhance_content(context: Dict[str, Any]) -> Dict[str, Any]:
            """Enhance the content."""
            self.logger.info("Enhancing content")
            return {
                "role": "function",
                "name": "enhance_content",
                "content": "Content enhanced and ready for processing"
            }

        return Agent(
            name="EnhancementNode",
            instructions="""You are the enhancement node.
            1. Enhance the content using enhance_content
            2. Transfer to processing using transfer_to_processing""",
            functions=[
                enhance_content,
                self.transfer_functions["to_processing"]
            ]
        )

    def _create_processing_agent(self) -> Agent:
        """Create processing node agent."""
        return Agent(
            name="ProcessingNode",
            instructions=self.processing_node.instructions,
            functions=[self.transfer_functions["to_validation"]]
        )

    def _create_validation_agent(self) -> Agent:
        """Create validation node agent."""
        return Agent(
            name="ValidationNode",
            instructions=self.validation_node.instructions,
            functions=[
                self.transfer_functions["to_completion"],
                self.transfer_functions["to_review"]
            ]
        )

    def _create_review_agent(self) -> Agent:
        """Create review node agent."""
        return Agent(
            name="ReviewNode",
            instructions=self.review_node.instructions,
            functions=[self.transfer_functions["to_manager"]]
        )

    def _create_completion_agent(self) -> Agent:
        """Create completion node agent."""
        return Agent(
            name="CompletionNode",
            instructions=self.completion_node.instructions,
            functions=[]  # No transfers needed for completion node
        )

    def process_pdf(self, pdf_text: str, user_prompt: str) -> Dict[str, Any]:
        """Process PDF using the node chain."""
        try:
            initial_context = {
                "pdf_text": pdf_text,
                "user_prompt": user_prompt,
                "node_history": [],
                "node_notes": [],
                "node_error": [],
                "processing_metadata": {
                    "start_time": datetime.utcnow().isoformat(),
                    "source": "pdf_processor",
                    "version": "1.0"
                }
            }

            self.logger.info("Starting PDF processing")
            
            # Format the message content as a string
            message_content = f"""Process this PDF content according to the user's prompt.

PDF Content:
{pdf_text}

User Prompt:
{user_prompt}

Please analyze this content and proceed with processing."""

            # Run the agent
            try:
                self.logger.debug("Sending message to Swarm client")
                response = self.client.run(
                    agent=self.manager_node.agent,
                    messages=[{
                        "role": "user",
                        "content": message_content
                    }]
                )
                
                self.logger.debug(f"Raw response type: {type(response)}")
                self.logger.debug(f"Raw response: {response}")
                self.logger.debug(f"Response attributes: {dir(response)}")

                # Initialize processing tracking
                processing_history = []
                current_context = initial_context

                # Handle string response
                if isinstance(response, str):
                    self.logger.debug("Handling string response")
                    return {
                        "status": "success",
                        "result": response,
                        "metadata": {
                            "node_history": [{
                                "node": "manager",
                                "action": "direct_response",
                                "timestamp": datetime.utcnow().isoformat()
                            }],
                            "node_notes": [response],
                            "node_error": [],
                            "processing_history": [{
                                "role": "assistant",
                                "content": response,
                                "timestamp": datetime.utcnow().isoformat()
                            }],
                            "processing_time": {
                                "start": initial_context["processing_metadata"]["start_time"],
                                "end": datetime.utcnow().isoformat()
                            }
                        }
                    }

                # Handle response with messages
                messages = getattr(response, 'messages', [])
                self.logger.debug(f"Messages type: {type(messages)}")
                self.logger.debug(f"Messages content: {messages}")
                
                if messages:
                    for message in messages:
                        self.logger.debug(f"Processing message: {message}")
                        self.logger.debug(f"Message type: {type(message)}")
                        
                        # Convert string message to dict format
                        if isinstance(message, str):
                            message_dict = {
                                "role": "assistant",
                                "content": message
                            }
                        else:
                            message_dict = message

                        self.logger.debug(f"Message dict: {message_dict}")

                        # Record the processing step
                        processing_history.append({
                            "role": message_dict.get("role", "unknown"),
                            "content": message_dict.get("content", ""),
                            "name": message_dict.get("name", ""),
                            "timestamp": datetime.utcnow().isoformat()
                        })

                        # Update node history for function calls
                        if message_dict.get("role") == "function":
                            current_context["node_history"].append({
                                "node": message_dict.get("name", "unknown").split("_")[0],
                                "action": message_dict.get("name", "unknown"),
                                "timestamp": datetime.utcnow().isoformat()
                            })

                        # Record assistant messages as notes
                        if message_dict.get("role") == "assistant":
                            current_context["node_notes"].append(message_dict.get("content", ""))

                    # Get final result from last message
                    final_message = messages[-1]
                    if isinstance(final_message, str):
                        final_content = final_message
                    else:
                        final_content = final_message.get("content", "")

                else:
                    # Handle response without messages
                    self.logger.debug("Handling response without messages")
                    final_content = str(response)
                    processing_history.append({
                        "role": "assistant",
                        "content": final_content,
                        "timestamp": datetime.utcnow().isoformat()
                    })

                return {
                    "status": "success",
                    "result": final_content,
                    "metadata": {
                        "node_history": current_context["node_history"],
                        "node_notes": current_context["node_notes"],
                        "node_error": current_context["node_error"],
                        "processing_history": processing_history,
                        "processing_time": {
                            "start": initial_context["processing_metadata"]["start_time"],
                            "end": datetime.utcnow().isoformat()
                        }
                    }
                }

            except Exception as e:
                self.logger.error(f"Agent execution failed: {str(e)}")
                self.logger.error("Error details:", exc_info=True)
                raise

        except Exception as e:
            self.logger.error(f"Processing failed: {str(e)}")
            self.logger.error("Error details:", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "node_history": initial_context.get("node_history", []),
                    "node_notes": initial_context.get("node_notes", []),
                    "node_error": [str(e)],
                    "processing_time": {
                        "start": initial_context["processing_metadata"]["start_time"],
                        "end": datetime.utcnow().isoformat()
                    }
                }
            }

    def get_node_status(self) -> Dict[str, Any]:
        """Get status of all nodes in the system."""
        return {
            node_name: {
                "status": "active" if node.agent else "inactive",
                "category": node.category.value,
                "has_connections": bool(node.available_nodes)
            }
            for node_name, node in self.available_nodes.items()
        } 