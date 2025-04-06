from typing import Dict, List, Optional, Any
from agents.base_agent import BaseAgent  # Assuming you have a base agent class

class QueryUnderstandingAgent(BaseAgent):
    """
    Agent responsible for understanding user queries, classifying intent,
    and routing to appropriate specialized agents.
    """
    
    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        super().__init__(name="QueryUnderstandingAgent")
        self.model_config = model_config or {}
        
    def process(self, query: str) -> Dict[str, Any]:
        """
        Process the user query to determine intent and extract relevant information.
        
        Args:
            query: User's input query
            
        Returns:
            Dictionary containing:
            - intent: Classified intent (recipe, conversion, etc.)
            - entities: Extracted entities from the query
            - original_query: The original user query
            - parameters: Additional parameters for specialized agents
        """
        intent = self._classify_intent(query)
        entities = self._extract_entities(query, intent)
        
        return {
            "intent": intent,
            "entities": entities,
            "original_query": query,
            "parameters": self._build_parameters(intent, entities)
        }
    
    def _classify_intent(self, query: str) -> str:
        """
        Classify the intent of the user query.
        
        Args:
            query: User's input query
            
        Returns:
            Intent classification (recipe, conversion, etc.)
        """
        # Simple keyword-based classification for MVP
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in ["convert", "conversion", "how many", "equivalent", "equals"]):
            return "conversion"
        elif any(keyword in query_lower for keyword in ["recipe", "how to make", "how do i make", "how to cook", "how do i cook"]):
            return "recipe"
        else:
            # Default to recipe search as fallback
            return "recipe"
    
    def _extract_entities(self, query: str, intent: str) -> Dict[str, Any]:
        """
        Extract relevant entities based on the classified intent.
        
        Args:
            query: User's input query
            intent: Classified intent
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        if intent == "conversion":
            # For conversion queries, try to identify from_unit, to_unit, and quantity
            # This is a simple implementation - will need enhancement
            entities["conversion_query"] = query
        
        elif intent == "recipe":
            # For recipe queries, extract the dish or ingredients
            entities["recipe_query"] = query
        
        return entities
    
    def _build_parameters(self, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build parameters for specialized agents based on intent and entities.
        
        Args:
            intent: Classified intent
            entities: Extracted entities
            
        Returns:
            Parameters for specialized agents
        """
        parameters = {}
        
        if intent == "conversion":
            parameters["search_type"] = "conversion"
            parameters["conversion_query"] = entities.get("conversion_query", "")
            
        elif intent == "recipe":
            parameters["search_type"] = "recipe"
            parameters["recipe_query"] = entities.get("recipe_query", "")
            
        return parameters