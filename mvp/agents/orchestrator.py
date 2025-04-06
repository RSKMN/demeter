from typing import Dict, Any, List, Optional
import asyncio
from .agent_registry import AgentRegistry
from .utils.context_manager import ContextManager
from .utils.message_protocol import MessageProtocol

class Orchestrator:
    """
    Orchestrates the flow of messages between agents and manages the overall workflow.
    """
    
    def __init__(self, registry: AgentRegistry, context_manager: ContextManager):
        self.registry = registry
        self.context_manager = context_manager
    
    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input through the agent workflow.
        
        Args:
            user_input: The input from the user
            
        Returns:
            The final response to present to the user
        """
        # Extract entities and update context
        self.context_manager.extract_entities(user_input)
        
        # Create initial message
        initial_message = MessageProtocol.create_message(
            sender="user",
            content=user_input,
            intent=MessageProtocol.INTENTS["QUERY"]
        )
        
        # Add to conversation history
        self.context_manager.add_to_conversation_history(initial_message)
        
        # Get current context
        current_context = self.context_manager.get_context()
        
        try:
            # Step 1: Route to Query Understanding Agent
            query_agent_response = await self.registry.route_message(
                initial_message, 
                "query_understanding",
                current_context
            )
            
            # Update context with query understanding results
            if "metadata" in query_agent_response:
                for key, value in query_agent_response["metadata"].items():
                    self.context_manager.update_context(key, value)
            
            # Step 2: Route to appropriate agent based on intent
            if query_agent_response.get("intent") == MessageProtocol.INTENTS["RECIPE_SEARCH"]:
                # Route to Recipe Retrieval Agent
                recipe_message = MessageProtocol.create_message(
                    sender="query_understanding",
                    content=query_agent_response["content"],
                    intent=MessageProtocol.INTENTS["RECIPE_SEARCH"],
                    metadata=query_agent_response.get("metadata", {})
                )
                
                agent_response = await self.registry.route_message(
                    recipe_message,
                    "recipe_retrieval",
                    self.context_manager.get_context()
                )
                
            elif query_agent_response.get("intent") == MessageProtocol.INTENTS["CONVERSION_REQUEST"]:
                # Route to Conversion Agent
                conversion_message = MessageProtocol.create_message(
                    sender="query_understanding",
                    content=query_agent_response["content"],
                    intent=MessageProtocol.INTENTS["CONVERSION_REQUEST"],
                    metadata=query_agent_response.get("metadata", {})
                )
                
                agent_response = await self.registry.route_message(
                    conversion_message,
                    "conversion",
                    self.context_manager.get_context()
                )
            else:
                # Default to using the query agent's response directly
                agent_response = query_agent_response
            
            # Step 3: Final integration through Phi-Agent
            integration_message = MessageProtocol.create_message(
                sender=agent_response.get("agent", "unknown"),
                content=agent_response.get("content", ""),
                intent=MessageProtocol.INTENTS["RESPONSE"],
                metadata=agent_response.get("metadata", {})
            )
            
            final_response = await self.registry.route_message(
                integration_message,
                "integration",
                self.context_manager.get_context()
            )
            
            # Add final response to conversation history
            self.context_manager.add_to_conversation_history(
                MessageProtocol.create_message(
                    sender="system",
                    content=final_response.get("content", ""),
                    intent=MessageProtocol.INTENTS["RESPONSE"]
                )
            )
            
            return final_response
            
        except Exception as e:
            error_response = {
                "agent": "orchestrator",
                "content": f"An error occurred: {str(e)}",
                "metadata": {"error": str(e)},
                "intent": MessageProtocol.INTENTS["ERROR"]
            }
            
            # Add error response to conversation history
            self.context_manager.add_to_conversation_history(
                MessageProtocol.create_message(
                    sender="system",
                    content=error_response["content"],
                    intent=MessageProtocol.INTENTS["ERROR"]
                )
            )
            
            return error_response