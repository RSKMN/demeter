import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAgent(ABC):
    """Base class for all agents in the recipe conversion system."""
    
    def __init__(self, name: str):
        self.name = name
        self.is_busy = False
    
    @abstractmethod
    async def process(self, message: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process an incoming message and return a response.
        
        Args:
            message: The message to process
            context: Contextual information
            
        Returns:
            The processed response
        """
        pass
    
    def _format_response(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format the response from this agent.
        
        Args:
            content: The content of the response
            metadata: Additional metadata
            
        Returns:
            The formatted response
        """
        return {
            "agent": self.name,
            "content": content,
            "metadata": metadata or {}
        }
    
    async def handle_error(self, error: Exception, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle errors that occur during processing.
        
        Args:
            error: The exception that was raised
            message: The message being processed when the error occurred
            
        Returns:
            Error response
        """
        error_message = f"Error in {self.name}: {str(error)}"
        return self._format_response(error_message, {"error": str(error), "original_message": message})