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
            instructions="""You are the Enhancement node for PDF processing. 
            You will enhance the PDF prompt  and then transfer to the processing node. You are about to read a dictionary that looks like this:
            {
                "node_notes": [], <-Insert your first summary here
                "node_error": [], <-Insert your first error here
                "node_history": [], <-Insert your first history here
                "node_status": [], <-Insert your first status here
                "response": "" <-Insert your first response here
            }
            Inside response  you will find the orginal pdf
            
            two variables one that contains the PDF content and the other contains the original user prompt. Both are long strings.
            1. First read the pdf cony

            2. If processing is successful, use transfer_to_processing to send to enhancement node
            3. You MUST pass the information as a json object that contains the following fields: 
                - node_notes: a list of strings that contains the summaries of the content
                - node_error: a list of strings that contains the errors that occurred during processing
                - node_history: a list of dictionaries that contains the node history
                - node_status: a string that contains the status of the node
                - response: a string that contains the response from the node

            4. response: You will need to paste the pdf content into you response on the field called response. 
            5. node_notes: Your summary should be included node_notes appending your answer to the end of the list.    
            6. node_error: If there are errors, report them in the node_error elemnt of your response. Include your EnhencementNode befor the error string so I can tell who detected the error in my swarm system.
            7. node_history: Inside node_history append your node name and the action, funciton you took (which node are you calling). EnhencementNode.
            8. node_status: should be "success" if there are no errors. Append stauts to the list.
            
            Since you are a Enhancement node your job is to take the information and summary from the manager node and enhence the user prompt. You will get as input an object just like this" 

            
            {
                "node_notes": [],
                "node_error": [],
                "node_history": [],
                "node_status": [],
                "response": {
                    pdf_content: pdf original document,
                    original_prompt: original user prompt,
                    enhanced_prompt: enhanced user prompt,
                    answer: last node answer
                },
            }
            You will need to append your own response into this list. On response be sure to always pass the entire PDF content and the original user prompt. Allong your enahnced response you will need to include the original PDF content and the original user prompt. 
            It's very important that you follow this format. The next node expects this format. To continue the chain you need to append your response to the list and append the status to the list. If you see multiple elements in any of the list it's because some nodes already added information to the list. Even yourself. This means that the system already encounter an error or some other node already added information to the list. You might need to solve the error of the previous node first before continuing the chain. Only do this if this soluctio  involves your own definition or description of the type of agent you are. 

            OUTPUT:
            Response:
                "node_notes": [], <- Not empty, append your summary here, can't be empty, if nothing to add add " "
                "node_error": [], <- Not empty, append your error here, can't be empty, if nothing to add add " "
                "node_history": [], <- Not empty, append your history here, can't be empty, if nothing to add add " "
                "node_status": [], <- Not empty, append your status here, can't be empty, if nothing to add add " "
                "response": {
                        pdf_content: pdf original documents,
                        original_prompt: original user prompt,
                        enhanced_prompt: enhanced user prompt <- this is the only field that you will need to update.
                        answer: last node answer
                    },   
            }

            if you get a second iteration of this request it means that the first iteration was not successful. You need to solve the error of the previous node first before continuing the chain. Only do this if this solutio  involves your own definition or description of the type of agent you are. Since you are an enhancement node you will need to solve errors relaated with the user prompt. If you think there is a missunderstanding or if the answr can't be replied properly with the current response object then you will need to insert the error in the node_error list.
            Or if you think you can create an enhanced prompt that will help the next node to process the document better and finally answrr the question. Add this to the response.enhanced_prompt entry of the response object.
            If you think that we can't continue the chain because the error is related to the user-interface-system interaction, you need to return a response that contains the error and insert it in the node_error list.
            
            """, 
            functions=[]
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