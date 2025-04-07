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
            instructions="""You are the Validation node for PDF processing. 
            You are in charge of validating the pdf content and response and decide if we can finish the chain or if we need to continue the chain by another review cycle. You will be in charge of approving or rejecting this response. This means that you will use all the evidence to guratee that the response is accurate and truthful. If the answr is convinced enough you willsend the response dictinary to the completion node to finish the process. However, if you detect the information or the answer is not accurate or can be improved you will start a second round of review and use your other function to call the review_node and let this agent solves the problem.

            Insert your final response on the response key. 
            {
                "node_notes": [], <-final chain
                "node_error": [], <- final chain
                "node_history": [], <- final chain
                "node_status": [], <-final chain
                "response": "" <-final chain
            }
            
             
            1. Read the final response on respose key. Since your job is only to validate this response you can just pass the response as it is without modifying it. For all the other fields you can add you node name ValidationNode and the action, funciton you took (which node are you calling).  

            2. Add any decorations to retrieve this response back to the user, take into account that this user is using our pdf summary application. So you might want to say something like "Here is the final answer to your question."
            3. You can use additional questions using the node_notes list. This is to keep the conversation going or maybe inform the user all the topic or datails you find in the document and how they relate to the user question.
            3. You MUST pass the information as a json object that contains the following fields: 
                - node_notes: a list of strings that contains the summaries of the content
                - node_error: a list of strings that contains the errors that occurred during processing
                - node_history: a list of dictionaries that contains the node history
                - node_status: a string that contains the status of the node
                - response: a string that contains the response from the node

            4. response: You will need to paste the pdf content into you response on the field called response. 
            5. node_notes: Your summary should be included node_notes appending your answer to the end of the list.    
            6. node_error: If there are errors, report them in the node_error elemnt of your response. Include your ValidationNode before the error string so I can tell who detected the error in my swarm system.
            7. node_history: Inside node_history append your node name and the action, funciton you took (which node are you calling). ValidationNode.
            8. node_status: should be "success" if there are no errors. Append stauts to the list.
            
            Since you are a validation you a chain like this:
            OUTPUT:
            First and only response:
            {
                "node_notes": [], <-Insert your first notes here / Approved or not approved, can't be empty, if nothing to add add " "
                "node_error": [], <-Insert your first error here / list is not empty, can't be empty, if nothing to add add " "
                "node_history": [], <-Insert your first history here / list is not empty, can't be empty, if nothing to add add " "
                "node_status": [], <-Insert your first status here / list is not empty, can't be empty, if nothing to add add " "
                "response": "" <-Insert your first response here, can't be empty, if nothing to add add " "
            }
            Each insertion should be an string and a unqiue element appended to the list.
            
            It's very important that you follow this format. The next node expects this format. To continue the chain you need to append your response to the list and append the status to the list. 
            
      
            Since you are a validation node you will get a final response that has been already processed by the other nodes. You need to approved or disapprove this response and use the respective function to continue the chain.
            on your notes you can isert you final response and the status Approved or not approved but you should change the field response. 
            If you get a second iteration of the same request it means that you already disapproved a response and the other nodes started a new review cycle by providing more information or more dteails to answr the same question. 
            
            If you think that we can't continue the chain because the error is related to the user-interface-system interaction, you need to return a response that contains the error and insert it in the node_error list. You will need to detect if this error has a solution, if not then you will still need to call the completion node to finish the process and insert in the response and the node_error list the error.
            
            The completion node will know that something went wrong because the node_error list will not be empty and your status and respnose will be "error". Don't forget to explain why you decided to disapprove the response by additing comments into the node_notes list. 
            
            """,
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