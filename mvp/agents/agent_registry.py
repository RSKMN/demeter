from typing import Dict, Type, List, Any, Optional
import asyncio
from .base_agent import BaseAgent

class AgentRegistry:
    """
    Registry for managing and coordinating agents.
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the registry.
        
        Args:
            agent: The agent to register
        """
        self.agents[agent.name] = agent
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """
        Get an agent by name.
        
        Args:
            name: The name of the agent
            
        Returns:
            The agent if found, None otherwise
        """
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """
        Get a list of all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(self.agents.keys())
    
    async def route_message(self, message: Dict[str, Any], to_agent: str, 
                           context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route a message to a specific agent.
        
        Args:
            message: The message to route
            to_agent: The name of the agent to route to
            context: Optional context to pass along
            
        Returns:
            The response from the agent
        """
        agent = self.get_agent(to_agent)
        if not agent:
            raise ValueError(f"Agent '{to_agent}' not found in registry")
        
        try:
            return await agent.process(message, context)
        except Exception as e:
            return await agent.handle_error(e, message)