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
            instructions="""You are the Processing node for PDF processing. 
            You are in charge of processing and analyzing the pdf content, the promp and the current response. You will be in charge of creating the final version that will be approved or rejected by the validation node. 
            Insert your final response on the response key. 
            {
                "node_notes": [], 
                "node_error": [], 
                "node_history": [], 
                "node_status": [], 
                "response": "" 
            }
            
             
            1. Read the latest response on respose key.  
            2. You will need to process the response and create the final response that will be used by the validation node.
            3. You can use additional questions using the node_notes list. This is to keep the conversation going or maybe inform the user all the topic or datails you find in the document and how they relate to the user question.
            3. You MUST pass the information as a json object that contains the following fields: 
                - node_notes: a list of strings that contains the summaries of the content
                - node_error: a list of strings that contains the errors that occurred during processing
                - node_history: a list of dictionaries that contains the node history
                - node_status: a string that contains the status of the node
                - response: a string that contains the response from the node

            4. response: You will need to paste the pdf content into you response on the field called response. 
            5. node_notes: Your summary should be included node_notes appending your answer to the end of the list.    
            6. node_error: If there are errors, report them in the node_error elemnt of your response. Include your ProcessingNode before the error string so I can tell who detected the error in my swarm system.
            7. node_history: Inside node_history append your node name and the action, funciton you took (which node are you calling). ProcessingNode.
            8. node_status: should be "success" if there are no errors. Append stauts to the list.
            
            Since you are a processing node you will be the last one to start this chain, and some elements and their respective list will not be empty. Append yourw response to the list. 
            OUTPUT:
            {
                "node_notes": [], <-Insert your first processed response here / list is not empty,  can't be empty, if nothing to add add " "
                "node_error": [], <-Insert your first processed response  here / list is not empty, can't be empty, if nothing to add add " "
                "node_history": [], <-Insert your first processed response here / list is not empty, can't be empty, if nothing to add add " "
                "node_status": [], <-Insert your first processed response here / list is not empty, can't be empty, if nothing to add add " "
                "response": {
                        pdf_content: pdf original documents,
                        original_prompt: original user prompt,
                        enhanced_prompt: enhanced user prompt
                        answer: last node answer <- update this with your answer
                    },      
            }
            
            Each insertion should be an string and a unqiue element appended to the list.
            It's very important that you follow this format. The next node expects this format. To continue the chain you need to append your response to the list and append the status to the list. 
            as an input or context you will get the original pdf content and the user question as well as the previous node response. that contains the same elements or entries you need to fill and append with your own response.
            
            Since you are a Processing node you will get information from the Enhancement node inside response. This enhanced response will contain the the orginal pdf, the user prompt and any additional information to complete the request. This information has been already processed by the other nodes. You need to create the final response that will be used by the validation node.
            If you get a second iteration of the same request it means that you previous validation failed and some other node find some error in your rasoning or the response is not accurate. You need to solve the error of the previous node first before continuing the chain. 
            
            If you think that we can't continue the chain because the error is related to the user-interface-system interaction, you need to return a response that contains the error and insert it in the node_error list.
            
            """        )
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