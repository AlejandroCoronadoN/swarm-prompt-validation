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
        
        # Initialize node history for tracking
        self.node_history = []
        
        # Initialize Swarm client with debug logging
        self.client = Swarm()  # Initialize Swarm client
        self.logger.info("Swarm client initialized")
        
        # Step 1: Create all nodes first
        self.logger.info("Creating nodes...")
        self.completion_node = CompletionNode()
        self.review_node = ReviewNode()
        self.validation_node = ValidationNode()
        self.processing_node = ProcessingNode()
        self.enhancement_node = EnhancementNode()
        self.logger.info("All nodes created")

        # Step 2: Create available nodes dictionary
        self.available_nodes = {
            "enhancement": self.enhancement_node,
            "processing": self.processing_node,
            "validation": self.validation_node,
            "review": self.review_node,
            "completion": self.completion_node
        }
        self.logger.info(f"Available nodes: {list(self.available_nodes.keys())}")

        # Step 3: Create transfer functions
        self.logger.info("Defining transfer functions...")
        self._define_transfer_functions()
        self.logger.info("Transfer functions defined")

        # Step 4: Create agents for each node
        self.logger.info("Creating agents for nodes...")
        self._create_agents()
        self.logger.info("All node agents created")

        # Step 5: Create manager node with access to all other nodes
        self.logger.info("Creating manager node...")
        self.manager_node = ManagerNode(self.available_nodes)
        self.manager_node.agent = self._create_manager_agent()
        self.logger.info("Manager node created")
        
        # Add manager to available nodes for review->manager connection
        self.available_nodes["manager"] = self.manager_node

        self.logger.info("All nodes initialized and connected")

    def _define_transfer_functions(self):
        """Define transfer functions for node connections."""
        
        def transfer_to_enhancement(context):
            """Transfer from manager to enhancement."""
            self.logger.info("🔄 TRANSFER: Manager → Enhancement")
            self.logger.debug(f"Context type: {type(context)}")
            self.logger.debug(f"Context at transfer time: {context}")
            
            # Track in the orchestrator's context
            if hasattr(self, 'node_history'):
                self.node_history.append({
                    "node": "manager",
                    "action": "transfer_to_enhancement",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return self.enhancement_node.agent

        def transfer_to_processing(context):
            """Transfer from enhancement to processing."""
            self.logger.info("🔄 TRANSFER: Enhancement → Processing")
            self.logger.debug(f"Context type: {type(context)}")
            self.logger.debug(f"Context at transfer time: {context}")
            
            # Track in the orchestrator's context
            if hasattr(self, 'node_history'):
                self.node_history.append({
                    "node": "enhancement",
                    "action": "transfer_to_processing",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return self.processing_node.agent

        def transfer_to_validation(context):
            """Transfer from processing to validation."""
            self.logger.info("🔄 TRANSFER: Processing → Validation")
            self.logger.debug(f"Context type: {type(context)}")
            self.logger.debug(f"Context at transfer time: {context}")
            
            # Track in the orchestrator's context
            if hasattr(self, 'node_history'):
                self.node_history.append({
                    "node": "processing",
                    "action": "transfer_to_validation",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return self.validation_node.agent

        def transfer_to_review(context):
            """Transfer from validation to review (on failure)."""
            self.logger.info("🔄 TRANSFER: Validation → Review (Validation Failed)")
            self.logger.debug(f"Context type: {type(context)}")
            self.logger.debug(f"Context at transfer time: {context}")
            
            # Track in the orchestrator's context
            if hasattr(self, 'node_history'):
                self.node_history.append({
                    "node": "validation",
                    "action": "transfer_to_review",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return self.review_node.agent

        def transfer_to_completion(context):
            """Transfer from validation to completion (on success)."""
            self.logger.info("🔄 TRANSFER: Validation → Completion (Validation Passed)")
            self.logger.debug(f"Context type: {type(context)}")
            self.logger.debug(f"Context at transfer time: {context}")
            
            # Track in the orchestrator's context
            if hasattr(self, 'node_history'):
                self.node_history.append({
                    "node": "validation",
                    "action": "transfer_to_completion",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            return self.completion_node.agent

        def transfer_to_manager(context):
            """Transfer from review back to manager."""
            self.logger.info("🔄 TRANSFER: Review → Manager")
            self.logger.debug(f"Context type: {type(context)}")
            self.logger.debug(f"Context at transfer time: {context}")
            
            # Track in the orchestrator's context
            if hasattr(self, 'node_history'):
                self.node_history.append({
                    "node": "review",
                    "action": "transfer_to_manager",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
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
            ],
            tool_choice="auto"
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
            instructions=self.enhancement_node.instructions,
            functions=[
                self.transfer_functions["to_processing"]
            ],
            tool_choice="auto"
        )

    def _create_processing_agent(self) -> Agent:
        """Create processing node agent."""
        def process_content(context: Dict[str, Any]) -> Dict[str, Any]:
            """Process the content."""
            self.logger.info("Processing content")
            return {
                "role": "function",
                "name": "process_content",
                "content": "Content processed and ready for validation"
            }

        return Agent(
            name="ProcessingNode",
            instructions=self.processing_node.instructions,
            functions=[
                self.transfer_functions["to_validation"]
            ],
            tool_choice="auto"
        )

    def _create_validation_agent(self) -> Agent:
        """Create validation node agent."""
        def validate_content(context: Dict[str, Any]) -> Dict[str, Any]:
            """Validate the content."""
            self.logger.info("Validating content")
            return {
                "role": "function",
                "name": "validate_content",
                "content": "Content validated successfully"
            }

        return Agent(
            name="ValidationNode",
            instructions=self.validation_node.instructions,
            functions=[
                self.transfer_functions["to_completion"],
                self.transfer_functions["to_review"]
            ],
            tool_choice="auto"
        )

    def _create_review_agent(self) -> Agent:
        """Create review node agent."""
        def review_content(context: Dict[str, Any]) -> Dict[str, Any]:
            """Review the content."""
            self.logger.info("Reviewing content")
            return {
                "role": "function",
                "name": "review_content",
                "content": "Content reviewed and ready for manager"
            }

        return Agent(
            name="ReviewNode",
            instructions=self.review_node.instructions,
            functions=[
                self.transfer_functions["to_manager"]
            ],
            tool_choice="auto"
        )

    def _create_completion_agent(self) -> Agent:
        """Create completion node agent."""
        def complete_content(context: Dict[str, Any]) -> Dict[str, Any]:
            """Complete the content processing."""
            self.logger.info("Completing content processing")
            return {
                "role": "function",
                "name": "complete_content",
                "content": "Content processing completed successfully"
            }

        return Agent(
            name="CompletionNode",
            instructions=self.completion_node.instructions,
            functions=[complete_content]
        )

    def _create_agents(self):
        """Create agents for all nodes."""
        self.logger.info("Creating agents for nodes")
        
        # First, set available_nodes for each node
        self.logger.info("Setting up node connections")
        for node_name, node in self.available_nodes.items():
            node.available_nodes = self.available_nodes
            self.logger.info(f"Set available_nodes for {node_name}")
        
        # Now create the agents
        self.logger.info("Creating completion agent")
        self.completion_node.agent = self._create_completion_agent()
        
        self.logger.info("Creating review agent")
        self.review_node.agent = self._create_review_agent()
        
        self.logger.info("Creating validation agent")
        self.validation_node.agent = self._create_validation_agent()
        
        self.logger.info("Creating processing agent")
        self.processing_node.agent = self._create_processing_agent()
        
        self.logger.info("Creating enhancement agent")
        self.enhancement_node.agent = self._create_enhancement_agent()

    def process_pdf(self, pdf_text: str, user_prompt: str) -> Dict[str, Any]:
        """Process PDF using the node chain."""
        try:
            # Reset node history for this run
            self.node_history = []
            
            initial_context = {
                "pdf_text": pdf_text,
                "user_prompt": user_prompt,
                "processing_metadata": {
                    "start_time": datetime.utcnow().isoformat(),
                    "source": "pdf_processor",
                    "version": "1.0"
                }
            }

            self.logger.info("Starting PDF processing")
            
            # Format the message content
            message_content = f"""Process this PDF content according to the user's prompt.

PDF Content:
{pdf_text}

User Prompt:
{user_prompt}

Please analyze this content and proceed with processing."""

            # Run the agent chain starting with manager
            try:
                self.logger.info("Starting agent chain with manager node")
                self.logger.debug(f"Initial context: {initial_context}")
                
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

                # Process the response
                if isinstance(response, str):
                    self.logger.info("Received string response")
                    return {
                        "status": "success",
                        "result": response,
                        "metadata": {
                            "node_history": self.node_history,
                            "node_notes": [],
                            "node_error": [],
                            "processing_time": {
                                "start": initial_context["processing_metadata"]["start_time"],
                                "end": datetime.utcnow().isoformat()
                            }
                        }
                    }

                # Handle response with messages
                messages = getattr(response, 'messages', [])
                if messages:
                    self.logger.info(f"Processing {len(messages)} messages")
                    for i, msg in enumerate(messages):
                        self.logger.debug(f"Message {i}: {msg}")
                    
                    final_message = messages[-1]
                    if isinstance(final_message, str):
                        final_content = final_message
                    else:
                        final_content = final_message.get("content", "")

                    self.logger.info("Processing completed successfully")
                    return {
                        "status": "success",
                        "result": final_content,
                        "metadata": {
                            "node_history": self.node_history,
                            "node_notes": [],
                            "node_error": [],
                            "processing_time": {
                                "start": initial_context["processing_metadata"]["start_time"],
                                "end": datetime.utcnow().isoformat()
                            }
                        }
                    }

                self.logger.warning("No messages in response")
                return {
                    "status": "success",
                    "result": str(response),
                    "metadata": {
                        "node_history": self.node_history,
                        "node_notes": [],
                        "node_error": [],
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
                    "node_history": self.node_history,
                    "node_notes": [],
                    "node_error": [str(e)],
                    "processing_time": {
                        "start": initial_context["processing_metadata"]["start_time"],
                        "end": datetime.utcnow().isoformat()
                    }
                }
            }

    def get_node_status(self) -> Dict[str, Dict[str, str]]:
        """Get status of all nodes for debugging purposes."""
        self.logger.info("Getting node status")
        status = {}
        
        for node_name, node in self.available_nodes.items():
            node_type = node.__class__.__name__
            has_agent = hasattr(node, 'agent') and node.agent is not None
            
            status[node_name] = {
                "status": "initialized" if has_agent else "not initialized",
                "type": node_type,
                "category": self._get_node_category(node_type),
                "has_agent": has_agent
            }
        
        return status

    def _get_node_category(self, node_type: str) -> str:
        """Get the category of a node by its type."""
        if "Manager" in node_type:
            return "control"
        elif "Enhancement" in node_type:
            return "preprocessing"
        elif "Processing" in node_type:
            return "processing"
        elif "Validation" in node_type:
            return "validation"
        elif "Review" in node_type:
            return "review"
        elif "Completion" in node_type:
            return "completion"
        else:
            return "unknown" 