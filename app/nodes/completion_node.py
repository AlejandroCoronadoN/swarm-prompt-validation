"""Completion node for PDF processing system."""

import logging
from typing import Any, ClassVar, Dict, Optional

from swarm import Agent

from ..core.base_node import NodeBase, NodeCategory
from ..utils.logging_config import setup_logger


class CompletionNode(NodeBase):
    """Completion node that finalizes the PDF processing workflow.
    
    Responsibilities:
    - Finalizes the processing results
    - Ensures all required information is present
    - Prepares the final response
    - Handles completion-specific errors
    """
    
    # Class-level logger
    logger: ClassVar[logging.Logger] = setup_logger("completion_node")
    
    def __init__(self) -> None:
        """Initialize the completion node."""
        super().__init__(
            category=NodeCategory.COMPLETION,
            name="CompletionNode",
            instructions="""You are the Completion node for PDF processing. 
            You are in charge of returning the final answer to the user. You need to pass the final response_dictionary
            {
                "node_notes": [], <-final chain
                "node_error": [], <- final chain
                "node_history": [], <- final chain
                "node_status": [], <-final chain
                "response": "" <-final chain
            }
            
             
            1. Read the final response on respose key.  

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
            6. node_error: If there are errors, report them in the node_error elemnt of your response. Include your CompletionNode before the error string so I can tell who detected the error in my swarm system.
            7. node_history: Inside node_history append your node name and the action, funciton you took (which node are you calling). CompletionNode.
            8. node_status: should be "success" if there are no errors. Append stauts to the list.
            
            Since you are a completion node you will be the last one to start this chain, and some elements and their respective list will not be empty. This is how the input will look like:
            INPUT
            {
                "node_notes": [], Final chain
                "node_error": [], Final chain
                "node_history": [], Final chain
                "node_status": [], Final chain
                "response": {
                    pdf_content: pdf original document,
                    original_prompt: original user prompt,
                    enhanced_prompt: enhanced user prompt,
                    answer: last node answer
                },            }
            
            It's very important that you follow this format. The next node expects this format. To continue the chain you need to append your response to the list and append the status to the list. 
            OUTPUT
            Response:
            {
                "node_notes": [], <-Insert your first summary here
                "node_error": [], <-Insert your first error here
                "node_history": [], <-Insert your first history here
                "node_status": [], <-Insert your first status here
                "response": { 
                    pdf_content: pdf original document,
                    original_prompt: original user prompt,
                    enhanced_prompt: enhanced user prompt,
                    answer: last node answer <- only update is required with your own version of the final answer for the user (allucination free).
                },            }
            
            Since you are a completion node you will get a final response that has been already processed by the other nodes. You just need to need to send thhe final version but verify that the response was not created by allucination or that it matches the content of the document. 
            
            If you think that we can't continue the chain because the error is related to the user-interface-system interaction, you need to return a response that contains the error and insert it in the node_error list.
            
            """,
        )
        self.available_nodes: Dict[str, Dict[str, Any]] = {}
        self.agent = self._create_agent()
        self.logger.info("Initializing CompletionNode")

    @property
    def uses_swarm(self) -> bool:
        return True

    def _create_agent(self) -> Agent:
        return Agent(
            name=self.name,
            instructions=self.instructions,
            functions=[self.finalize_response]
        )

    def finalize_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the processed response."""
        return self.update_context(
            context,
            status="completed",
            message="Processing completed successfully",
            final_response=context.get("processed_content")
        )

    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Agent:
        """Handle errors during completion.
        
        Args:
            error: The error that occurred
            context: Current processing context
            
        Returns:
            Agent: The current node for error management
        """
        self.logger.error(f"Completion error: {str(error)}")
        context["node_status"] = "error"
        context["error"] = str(error)
        return self 