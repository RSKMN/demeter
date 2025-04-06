from typing import Dict, Any, List, Optional, Set
import time

class ContextManager:
    """Manages context across agent interactions."""
    
    def __init__(self):
        self.context = {
            "conversation_history": [],
            "extracted_entities": {
                "ingredients": [],
                "measurements": [],
                "recipe_names": [],
                "conversion_requests": []
            },
            "current_task": None,
            "task_progress": {},
            "session_start_time": time.time(),
            "last_update_time": time.time()
        }
    
    def update_context(self, key: str, value: Any) -> None:
        """
        Update a specific context value.
        
        Args:
            key: The context key to update
            value: The new value
        """
        self.context[key] = value
        self.context["last_update_time"] = time.time()
    
    def get_context(self, key: Optional[str] = None) -> Any:
        """
        Get context value(s).
        
        Args:
            key: The specific context key to retrieve, or None for all context
            
        Returns:
            The requested context value or the entire context
        """
        if key:
            return self.context.get(key)
        return self.context
    
    def add_to_conversation_history(self, message: Dict[str, Any]) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            message: The message to add
        """
        self.context["conversation_history"].append(message)
        self.context["last_update_time"] = time.time()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the full conversation history.
        
        Returns:
            The conversation history
        """
        return self.context["conversation_history"]
    
    def get_recent_conversation(self, num_messages: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent messages from the conversation history.
        
        Args:
            num_messages: Number of recent messages to return
            
        Returns:
            The most recent messages
        """
        history = self.context["conversation_history"]
        return history[-min(num_messages, len(history)):]
    
    def extract_entities(self, message: str) -> Dict[str, List[str]]:
        """
        Extract entities from a message and update the context.
        This is a placeholder for more sophisticated entity extraction.
        
        Args:
            message: The message to extract entities from
            
        Returns:
            Dictionary of extracted entities
        """
        # This is a very basic implementation
        # In a real system, you would use NLP or an LLM for this
        entities = {
            "ingredients": [],
            "measurements": [],
            "recipe_names": [],
            "conversion_requests": []
        }
        
        # Basic extraction of measurement patterns
        measurement_keywords = ["cup", "tablespoon", "teaspoon", "gram", "kg", "ounce", "pound", "ml", "liter"]
        for keyword in measurement_keywords:
            if keyword in message.lower():
                entities["measurements"].append(keyword)
        
        # Track if this seems like a conversion request
        conversion_keywords = ["convert", "conversion", "change", "metric", "imperial"]
        if any(keyword in message.lower() for keyword in conversion_keywords):
            entities["conversion_requests"].append(message)
        
        # Update the context with the new entities
        for entity_type, entity_list in entities.items():
            if entity_list:
                existing_entities = set(self.context["extracted_entities"].get(entity_type, []))
                updated_entities = existing_entities.union(set(entity_list))
                self.context["extracted_entities"][entity_type] = list(updated_entities)
        
        return entities
    
    def clear_session(self) -> None:
        """Clear the current session context but maintain conversation history."""
        history = self.context["conversation_history"]
        self.__init__()
        self.context["conversation_history"] = history