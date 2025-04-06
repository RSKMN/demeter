import streamlit as st
from typing import Dict, Any, List
import time
import os

# Import agents
from agents.query_understanding_agent import QueryUnderstandingAgent
from agents.recipe_retrieval_agent import RecipeRetrievalAgent
from agents.conversion_agent import ConversionAgent

class DemeterApp:
    def __init__(self):
        self.initialize_session_state()
        
        # Load API key from environment or .env file
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        
        # Initialize agents
        self.query_agent = QueryUnderstandingAgent()
        self.recipe_agent = RecipeRetrievalAgent()
        self.conversion_agent = ConversionAgent(api_key=api_key)
    
    def initialize_session_state(self):
        """Initialize session state variables if they don't exist."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "processing" not in st.session_state:
            st.session_state.processing = False
    
    def display_chat_history(self):
        """Display the chat history."""
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            with st.chat_message(role):
                st.write(content)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process the user query through the agent system.
        
        Args:
            query: User's input query
            
        Returns:
            Processed response
        """
        # Step 1: Understand the query
        query_result = self.query_agent.process(query)
        intent = query_result.get("intent", "unknown")
        parameters = query_result.get("parameters", {})
        
        # Step 2: Route to appropriate agent based on intent
        if intent == "conversion":
            conversion_result = self.conversion_agent.process(parameters)
            return self._format_conversion_response(conversion_result)
        elif intent == "recipe":
            recipe_result = self.recipe_agent.process(parameters)
            return self._format_recipe_response(recipe_result)
        else:
            return {
                "type": "unknown",
                "content": "I'm not sure what you're asking for. Could you try rephrasing your question?"
            }
    
    def _format_conversion_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format conversion result into user-friendly response."""
        if not result.get("success", False):
            return {
                "type": "conversion_error",
                "content": result.get("message", "Sorry, I couldn't perform that conversion.")
            }
        
        # Handle Gemini text response
        if result.get("conversion_type") == "gemini_text":
            return {
                "type": "conversion",
                "content": result.get("gemini_response", ""),
                "data": result
            }
        
        # Format standard conversion response
        original_value = result.get("original_value", "")
        original_unit = result.get("original_unit", "")
        display_value = result.get("display_value", "")
        converted_unit = result.get("converted_unit", "")
        ingredient = result.get("ingredient", "")
        warning = result.get("warning", "")
        
        ingredient_text = f" of {ingredient}" if ingredient else ""
        
        content = f"**{original_value} {original_unit}{ingredient_text} = {display_value} {converted_unit}**"
        
        if warning:
            content += f"\n\n⚠️ *{warning}*"
            
        return {
            "type": "conversion",
            "content": content,
            "data": result
        }
    
    def _format_recipe_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format recipe result into user-friendly response."""
        if not result.get("success", False):
            return {
                "type": "recipe_error",
                "content": result.get("message", "Sorry, I couldn't find that recipe.")
            }
        
        recipe_name = result.get("recipe_name", "")
        ingredients = result.get("ingredients", [])
        instructions = result.get("instructions", [])
        prep_time = result.get("prep_time", "")
        cook_time = result.get("cook_time", "")
        servings = result.get("servings", "")
        source = result.get("source", "")
        
        # Format recipe into markdown
        content = f"## {recipe_name}\n\n"
        
        if prep_time or cook_time or servings:
            details = []
            if prep_time:
                details.append(f"Prep Time: {prep_time}")
            if cook_time:
                details.append(f"Cook Time: {cook_time}")
            if servings:
                details.append(f"Servings: {servings}")
            content += " | ".join(details) + "\n\n"
        
        content += "### Ingredients\n"
        for ingredient in ingredients:
            content += f"- {ingredient}\n"
        
        content += "\n### Instructions\n"
        for i, instruction in enumerate(instructions, 1):
            content += f"{i}. {instruction}\n"
        
        if source:
            content += f"\n*Source: {source}*"
            
        return {
            "type": "recipe",
            "content": content,
            "data": result
        }
    
    def run(self):
        """Run the Streamlit application."""
        # Set up the UI
        st.title("Demeter: Your Culinary Assistant")
        st.write("Ask me to convert recipe measurements or find recipes!")
        
        # Step 4: Display chat history
        self.display_chat_history()
        
        # Step 5: Handle user input
        if user_query := st.chat_input("What would you like to know?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_query})
            
            # Display the new user message
            with st.chat_message("user"):
                st.write(user_query)
            
            # Set processing flag
            st.session_state.processing = True
            
            # Display assistant typing indicator
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.write("Thinking...")
                
                # Process the query
                try:
                    response = self.process_query(user_query)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response["content"]
                    })
                    
                    # Update the message placeholder with the response
                    message_placeholder.write(response["content"])
                except Exception as e:
                    error_message = f"Sorry, I encountered an error: {str(e)}"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_message
                    })
                    message_placeholder.write(error_message)
                finally:
                    # Reset processing flag
                    st.session_state.processing = False

# Main entry point
if __name__ == "__main__":
    app = DemeterApp()
    app.run()