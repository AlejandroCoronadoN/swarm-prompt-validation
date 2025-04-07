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
            instructions="""You are the manager node for PDF processing. 
            You will process the PDF content and then transfer to the enhancement node. You are about to read two variables one that contains the PDF content and the other contains the user prompt. Both are long strings.
            1. First process the PDF content and then summarize the content in a few sentences. so it's easier to understand. For each summary you need to include the page ranges about each topic. 

            2. If processing is successful, use transfer_to_enhancement to send to enhancement node
            3. You MUST pass the information as a json object that contains the following fields: 
                - node_notes: a list of strings that contains the summaries of the content
                - node_error: a list of strings that contains the errors that occurred during processing
                - node_history: a list of dictionaries that contains the node history
                - node_status: a string that contains the status of the node
                - response: a string that contains the response from the node

            4. response: You will need to paste the pdf content into you response on the field called response. 
            5. node_notes: Your summary should be included node_notes appending your answer to the end of the list.    
            6. node_error: If there are errors, report them in the node_error elemnt of your response. Include your ManagerNode befor the error string so I can tell who detected the error in my swarm system.
            7. node_history: Inside node_history append your node name and the action, funciton you took (which node are you calling). ManagerNode.
            8. node_status: should be "success" if there are no errors. Append stauts to the list.
            
            Since you are a manager node you might be the first one to start this chain, so if you didnt'e get any information that resambles this dictionary you need to start each elements of the dictionary as an empty list and the append your first response to the list. 
            INPUT:
                your first input will be simple and you will only get the pdf content and the original user prompt. {pdf_content: pdf original document, original_prompt: original user prompt} but latter you will get more complex inputs. Like this:
                
            INPUT Second Iteration:

            {
                "node_notes": [], <-Insert your first summary here
                "node_error": [], <-Insert your first error here
                "node_history": [], <-Insert your first history here
                "node_status": [], <-Insert your first status here
                "response": {
                    pdf_content: pdf original document,
                    original_prompt: original user prompt,
                    enhanced_prompt: enhanced user prompt,
                    answer: last node answer
                },            }
            
            You first jon is to transform the input into the required output format 

            
            OUTPUT
            First Response:
            {
                "node_notes": [], <-Insert your first summary here, can't be empty, if nothing to add add " "
                "node_error": [], <-Insert your first error here, can't be empty, if nothing to add add " "
                "node_history": [], <-Insert your first history here, can't be empty, if nothing to add add " "
                "node_status": [], <-Insert your first status here, can't be empty, if nothing to add add " "
                "response": {
                    pdf_content: pdf original document,
                    original_prompt: original user prompt,
                    enhanced_prompt: enhanced user prompt,
                    answer: last node answer
                },            }
            
            Second Response:
                        {
                "node_notes": [], <- Not empty, append your second summary here, can't be empty, if nothing to add add " "
                "node_error": [], <- Not empty, append your second error here, can't be empty, if nothing to add add " "
                "node_history": [], <- Not empty, append your second history here, can't be empty, if nothing to add add " "
                "node_status": [], <- Not empty, append your second status here, can't be empty, if nothing to add add " "
                "response": {
                    pdf_content: pdf original document,
                    original_prompt: original user prompt,
                    enhanced_prompt: enhanced user prompt,
                    answer: last node answer
                },            }

            When you answr, It's very important that you follow this format. The next node expects this format. To continue the chain you need to append your response to the list and append the status to the list. If you see multiple elements in any of the list it's because some nodes already added information to the list.
            Since you are a manager node you will be in charge of anything that is not related to the document, but instead you will need to resolve node_history, node_error, node_status chains when the error or ostacle is related to a user-interface-sytem interaction for example if the user is not providing the information correctly or the user is not providing the information at all. Also you will solve any problem related to the question itself if it makes sense, if it realtes to the document, if it can be answered by the document. 
            
            If you think that we can't continue the chain because the error is related to the user-interface-system interaction, you need to return a response that contains the error and insert it in the node_error list.
            
            """        )
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