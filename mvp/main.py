import streamlit as st
import os
import asyncio
from dotenv import load_dotenv

# Load custom agent modules
from agents.agent_registry import AgentRegistry
from agents.orchestrator import Orchestrator
from agents.utils.context_manager import ContextManager
from agents.utils.message_protocol import MessageProtocol

# The actual agent implementations will be imported in Step 3
# For now, we'll create placeholder imports
# These will be replaced with real implementations in the next steps
from agents.query_understanding_agent import QueryUnderstandingAgent
from agents.recipe_retrieval_agent import RecipeRetrievalAgent
from agents.conversion_agent import ConversionAgent
from agents.integration_agent import IntegrationAgent

# Load environment variables
load_dotenv()

# Check if API key is available
if not os.getenv("GOOGLE_API_KEY"):
    st.error("Please set the GOOGLE_API_KEY environment variable in the .env file")
    st.stop()

# Create placeholder agent classes for testing
# These will be replaced with real implementations in Steps 3-6
class PlaceholderAgent:
    def __init__(self, name):
        self.name = name
    
    async def process(self, message, context=None):
        return {
            "agent": self.name,
            "content": f"[{self.name}] Processed: {message.get('content', 'No content')}",
            "metadata": {},
            "intent": message.get("intent", "unknown")
        }
    
    async def handle_error(self, error, message):
        return {
            "agent": self.name,
            "content": f"Error in {self.name}: {str(error)}",
            "metadata": {"error": str(error)},
            "intent": "error"
        }

# Initialize the agent system
def initialize_agents():
    registry = AgentRegistry()
    context_manager = ContextManager()
    
    # Register actual agent implementations
    registry.register_agent(QueryUnderstandingAgent())
    registry.register_agent(RecipeRetrievalAgent())
    registry.register_agent(ConversionAgent())
    registry.register_agent(IntegrationAgent())
    
    orchestrator = Orchestrator(registry, context_manager)
    return orchestrator

# Create a function to process messages asynchronously
async def process_message_async(orchestrator, user_input):
    return await orchestrator.process_user_input(user_input)

# Initialize the orchestrator
orchestrator = initialize_agents()

# Streamlit UI
st.title("Recipe Conversion System")
st.subheader("Multi-Agent MVP")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask about a recipe or measurement conversion"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        # Process with multi-agent system
        response = asyncio.run(process_message_async(orchestrator, prompt))
        
        message_placeholder.markdown(response["content"])
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response["content"]})