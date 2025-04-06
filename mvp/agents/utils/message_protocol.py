from datetime import datetime
from typing import Dict, Any, Optional, List
import json

class MessageProtocol:
    """Utility for standardizing message format between agents."""
    
    INTENTS = {
        "QUERY": "user_query",
        "RECIPE_SEARCH": "recipe_search",
        "CONVERSION_REQUEST": "conversion_request",
        "RESPONSE": "response_to_user",
        "ERROR": "error_message",
        "TASK_COMPLETE": "task_complete",
        "TASK_FAILED": "task_failed"
    }
    
    @staticmethod
    def create_message(sender: str, content: str, intent: Optional[str] = None, 
                      metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a standardized message.
        
        Args:
            sender: The agent sending the message
            content: The content of the message
            intent: The intent of the message
            metadata: Additional metadata
            
        Returns:
            The formatted message
        """
        return {
            "sender": sender,
            "content": content,
            "intent": intent,
            "metadata": metadata or {},
            "timestamp": MessageProtocol._get_timestamp()
        }
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get the current timestamp."""
        return datetime.now().isoformat()
    
    @staticmethod
    def serialize(message: Dict[str, Any]) -> str:
        """Serialize a message to JSON string."""
        return json.dumps(message)
    
    @staticmethod
    def deserialize(message_str: str) -> Dict[str, Any]:
        """Deserialize a JSON string to a message dict."""
        return json.loads(message_str)
    
    @staticmethod
    def validate_message(message: Dict[str, Any]) -> bool:
        """
        Validate that a message has the required fields.
        
        Args:
            message: The message to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["sender", "content"]
        return all(field in message for field in required_fields)
    
    @staticmethod
    def get_conversation_summary(messages: List[Dict[str, Any]]) -> str:
        """
        Create a summary of a conversation from a list of messages.
        
        Args:
            messages: List of message objects
            
        Returns:
            A string summary of the conversation
        """
        summary = []
        for msg in messages:
            sender = msg.get("sender", "Unknown")
            content = msg.get("content", "")
            summary.append(f"{sender}: {content}")
        
        return "\n".join(summary)