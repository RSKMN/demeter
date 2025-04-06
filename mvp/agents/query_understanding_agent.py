from typing import Dict, List, Optional, Any
import re
from .base_agent import BaseAgent  # Assuming you have this base class

class QueryUnderstandingAgent(BaseAgent):
    """
    Agent responsible for understanding user queries, classifying intent,
    and routing to appropriate specialized agents.
    """
    
    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        super().__init__(name="QueryUnderstandingAgent")
        self.model_config = model_config or {}
        self.intents = {
            "conversion": {
                "keywords": [
                    "convert", "conversion", "how many", "equivalent", "equals", 
                    "ounce", "gram", "cup", "tablespoon", "teaspoon", "pound", "kg",
                    "ml", "liter", "gallon", "quart", "pint"
                ],
                "patterns": [
                    r"(convert|change|transform|turn)\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(?:of\s+)?([a-zA-Z\s]+)\s+(?:to|into)\s+([a-zA-Z]+)",
                    r"how\s+(?:many|much)\s+([a-zA-Z]+)\s+(?:is|are|in)\s+(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(?:of\s+)?([a-zA-Z\s]+)",
                    r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)\s+(?:of\s+)?([a-zA-Z\s]+)\s+(?:to|into|in)\s+([a-zA-Z]+)"
                ]
            },
            "recipe": {
                "keywords": [
                    "recipe", "dish", "cook", "make", "prepare", "how to", "ingredients",
                    "instructions", "steps", "preparation", "cooking method"
                ],
                "patterns": [
                    r"(?:how\s+(?:to|do\s+I)\s+(?:make|cook|prepare))\s+([a-zA-Z\s]+)",
                    r"(?:recipe\s+for)\s+([a-zA-Z\s]+)",
                    r"(?:what\s+(?:are|is)\s+(?:the|some)\s+(?:recipe|dish|meal))\s+([a-zA-Z\s]+)"
                ]
            }
        }
    
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
        # Step 1: Classify intent
        intent = self._classify_intent(query)
        
        # Step 2: Extract entities based on intent
        entities = self._extract_entities(query, intent)
        
        # Step 3: Build parameters for downstream agents
        parameters = self._build_parameters(intent, entities)
        
        # Step 4: Return structured understanding of query
        return {
            "intent": intent,
            "entities": entities,
            "original_query": query,
            "parameters": parameters,
            "confidence": self._calculate_confidence(query, intent)
        }
    
    def _classify_intent(self, query: str) -> str:
        """
        Classify the intent of the user query.
        
        Args:
            query: User's input query
            
        Returns:
            Intent classification (recipe, conversion, etc.)
        """
        query_lower = query.lower()
        intent_scores = {}
        
        # Score each intent based on keyword matches and pattern matches
        for intent_name, intent_data in self.intents.items():
            # Keyword matching
            keyword_matches = sum(1 for keyword in intent_data["keywords"] if keyword in query_lower)
            
            # Pattern matching
            pattern_matches = sum(1 for pattern in intent_data["patterns"] if re.search(pattern, query_lower))
            
            # Calculate score (patterns are weighted more heavily)
            intent_scores[intent_name] = keyword_matches + (pattern_matches * 3)
        
        # Return the intent with the highest score
        if not intent_scores or max(intent_scores.values()) == 0:
            return "unknown"
        
        return max(intent_scores, key=intent_scores.get)
    
    def _extract_entities(self, query: str, intent: str) -> Dict[str, Any]:
        """
        Extract relevant entities based on the classified intent.
        
        Args:
            query: User's input query
            intent: Classified intent
            
        Returns:
            Dictionary of extracted entities
        """
        query_lower = query.lower()
        entities = {}
        
        if intent == "conversion":
            # Handle conversion queries
            # Try to extract: quantity, from_unit, to_unit, ingredient
            for pattern in self.intents["conversion"]["patterns"]:
                match = re.search(pattern, query_lower)
                if match:
                    groups = match.groups()
                    if len(groups) >= 3:
                        # Different patterns have different group orders
                        if pattern == self.intents["conversion"]["patterns"][0]:
                            # convert X unit of ingredient to Y
                            entities["quantity"] = groups[1]
                            entities["from_unit"] = groups[2]
                            entities["ingredient"] = groups[3]
                            entities["to_unit"] = groups[4]
                        elif pattern == self.intents["conversion"]["patterns"][1]:
                            # how many X in Y units of ingredient
                            entities["to_unit"] = groups[0]
                            entities["quantity"] = groups[1]
                            entities["from_unit"] = groups[2]
                            entities["ingredient"] = groups[3]
                        elif pattern == self.intents["conversion"]["patterns"][2]:
                            # X units of ingredient to Y
                            entities["quantity"] = groups[0]
                            entities["from_unit"] = groups[1]
                            entities["ingredient"] = groups[2]
                            entities["to_unit"] = groups[3]
                    break
            
            # If regex didn't match, store the whole query
            if not entities:
                entities["conversion_query"] = query
                
        elif intent == "recipe":
            # Handle recipe queries
            # Try to extract: dish_name
            for pattern in self.intents["recipe"]["patterns"]:
                match = re.search(pattern, query_lower)
                if match:
                    entities["dish_name"] = match.group(1).strip()
                    break
            
            # If regex didn't match, extract potential dish name using heuristics
            if "dish_name" not in entities:
                # Remove common recipe query prefixes
                prefixes = [
                    "recipe for ", "how to make ", "how do i make ", 
                    "how to cook ", "how do i cook ", "i want to make ",
                    "show me how to make ", "can you give me a recipe for "
                ]
                cleaned_query = query_lower
                for prefix in prefixes:
                    if cleaned_query.startswith(prefix):
                        cleaned_query = cleaned_query[len(prefix):]
                        break
                
                entities["dish_name"] = cleaned_query.strip()
        
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
        parameters = {"routing": intent}
        
        if intent == "conversion":
            parameters.update({
                "quantity": entities.get("quantity"),
                "from_unit": entities.get("from_unit"),
                "to_unit": entities.get("to_unit"),
                "ingredient": entities.get("ingredient"),
                "conversion_query": entities.get("conversion_query")
            })
            
        elif intent == "recipe":
            parameters.update({
                "dish_name": entities.get("dish_name"),
                "search_query": f"recipe for {entities.get('dish_name', '')}" if entities.get('dish_name') else None
            })
            
        return {k: v for k, v in parameters.items() if v is not None}
    
    def _calculate_confidence(self, query: str, intent: str) -> float:
        """
        Calculate confidence score for the intent classification.
        
        Args:
            query: User's input query
            intent: Classified intent
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if intent == "unknown":
            return 0.3
        
        query_lower = query.lower()
        intent_data = self.intents.get(intent, {"keywords": [], "patterns": []})
        
        # Count matches
        keyword_matches = sum(1 for keyword in intent_data["keywords"] if keyword in query_lower)
        pattern_matches = sum(1 for pattern in intent_data["patterns"] if re.search(pattern, query_lower))
        
        # Calculate base confidence
        total_keywords = len(intent_data["keywords"])
        max_keywords_expected = min(5, total_keywords)  # Don't expect all keywords to match
        keyword_score = min(keyword_matches / max_keywords_expected, 1.0) if max_keywords_expected > 0 else 0
        
        pattern_score = 1.0 if pattern_matches > 0 else 0.0
        
        # Weight pattern matches more heavily
        confidence = (keyword_score * 0.4) + (pattern_score * 0.6)
        
        # Ensure confidence is between 0.3 and 0.95
        return max(0.3, min(confidence, 0.95))