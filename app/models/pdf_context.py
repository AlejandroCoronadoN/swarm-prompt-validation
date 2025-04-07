"""PDF processing context model."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PDFContext:
    """Context for PDF processing operations.
    
    This class holds all the necessary information for processing PDFs through the
    Swarm system, including the PDF content, prompts, responses, and processing metadata.
    """
    
    # Core PDF and Prompt Data
    pdf_text: str = ""
    user_prompt: str = ""
    enhanced_prompt: str = ""
    response: str = ""
    response_args: Dict[str, Any] = field(default_factory=dict)
    
    # Processing Metadata
    node_history: List[str] = field(default_factory=list)
    node_notes: List[str] = field(default_factory=list)
    node_status: bool = True
    node_error: List[str] = field(default_factory=list)
    validation_failed: bool = False
    
    # Additional Processing Information
    processing_time: Optional[float] = None
    token_count: Optional[int] = None
    confidence_score: Optional[float] = None
    
    def update(
        self,
        status: str,
        message: str,
        **kwargs: Any
    ) -> None:
        """Update context with new information.
        
        Args:
            status: Status of the operation ('success' or 'error')
            message: Status message to add to notes
            **kwargs: Additional context updates
        """
        self.node_status = status == "success"
        self.node_history.append(self.__class__.__name__)
        self.node_notes.append(message)
        
        # Update with additional kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of context
        """
        return {
            "pdf_text": self.pdf_text,
            "user_prompt": self.user_prompt,
            "enhanced_prompt": self.enhanced_prompt,
            "response": self.response,
            "response_args": self.response_args,
            "node_history": self.node_history,
            "node_notes": self.node_notes,
            "node_status": self.node_status,
            "node_error": self.node_error,
            "validation_failed": self.validation_failed,
            "processing_time": self.processing_time,
            "token_count": self.token_count,
            "confidence_score": self.confidence_score,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PDFContext":
        """Create context from dictionary.
        
        Args:
            data: Dictionary containing context data
            
        Returns:
            PDFContext: New context instance
        """
        return cls(**data)
    
    def is_valid(self) -> bool:
        """Check if context is valid for processing.
        
        Returns:
            bool: True if context is valid, False otherwise
        """
        return (
            bool(self.pdf_text)
            and bool(self.user_prompt)
            and not self.validation_failed
            and self.node_status
        )
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of processing information.
        
        Returns:
            Dict[str, Any]: Processing summary
        """
        return {
            "node_count": len(self.node_history),
            "note_count": len(self.node_notes),
            "error_count": len(self.node_error),
            "processing_time": self.processing_time,
            "token_count": self.token_count,
            "confidence_score": self.confidence_score,
        } 