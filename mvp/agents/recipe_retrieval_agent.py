# agents/recipe_retrieval_agent.py
from typing import Dict, List, Optional, Any
from agents.base_agent import BaseAgent
from duckduckgo_search import DDGS
import re
import json

class RecipeRetrievalAgent(BaseAgent):
    """
    Agent responsible for retrieving recipe information based on user queries.
    Uses DuckDuckGo search to find relevant recipes.
    """
    
    def __init__(self):
        super().__init__(name="RecipeRetrievalAgent")
        self.ddgs = DDGS()
        
    def process(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process recipe search parameters and retrieve relevant recipe information.
        
        Args:
            parameters: Dictionary containing search parameters
                - dish_name: Name of the dish to search for
                - search_query: Optional formatted search query
                
        Returns:
            Dictionary containing recipe information
        """
        dish_name = parameters.get("dish_name", "")
        search_query = parameters.get("search_query", f"recipe for {dish_name}")
        
        # Step 1: Perform search
        search_results = self._search_recipes(search_query)
        
        # Step 2: Filter and clean results
        filtered_results = self._filter_results(search_results, dish_name)
        
        # Step 3: Format the response
        return self._format_response(filtered_results, dish_name)
    
    def _search_recipes(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for recipes using DuckDuckGo.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        try:
            # Add "recipe" to the query if it's not already there
            if "recipe" not in query.lower():
                query = f"{query} recipe"
                
            results = self.ddgs.text(query, max_results=max_results)
            return list(results)
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _filter_results(self, results: List[Dict[str, Any]], dish_name: str) -> List[Dict[str, Any]]:
        """
        Filter and clean search results to ensure they're relevant recipe pages.
        
        Args:
            results: List of search results
            dish_name: Name of the dish to filter by
            
        Returns:
            Filtered list of search results
        """
        filtered = []
        recipe_sites = [
            "allrecipes", "foodnetwork", "epicurious", "simplyrecipes", 
            "seriouseats", "bonappetit", "tasty", "delish", "food.com",
            "bbc", "jamieoliver", "cooking.nytimes", "taste.com", "recipetineats"
        ]
        
        for result in results:
            # Check if the result is from a known recipe site
            is_recipe_site = any(site in result.get("href", "").lower() for site in recipe_sites)
            
            # Check if title or body contains recipe-related words
            title = result.get("title", "").lower()
            body = result.get("body", "").lower()
            
            has_recipe_keywords = any(keyword in title or keyword in body 
                                     for keyword in ["recipe", "how to make", "ingredients", "instructions", "cook"])
            
            # Check if the dish name appears in the title or early in the body
            has_dish_name = dish_name.lower() in title or dish_name.lower() in body[:100]
            
            if (is_recipe_site or has_recipe_keywords) and has_dish_name:
                # Clean and simplify the result
                filtered.append({
                    "title": self._clean_title(result.get("title", "")),
                    "url": result.get("href", ""),
                    "snippet": self._extract_info_from_snippet(result.get("body", "")),
                    "source": self._extract_source(result.get("href", ""))
                })
        
        return filtered
    
    def _clean_title(self, title: str) -> str:
        """Clean recipe titles by removing common suffixes and site names."""
        patterns = [
            r" - Allrecipes$", r" \| Allrecipes$", r" \| Food Network$",
            r" \| Epicurious$", r" - Simply Recipes$", r" Recipe \|.*$",
            r" \| Bon Appétit$", r" \| BBC Good Food$", r" - Tasty$"
        ]
        
        cleaned = title
        for pattern in patterns:
            cleaned = re.sub(pattern, "", cleaned)
        
        return cleaned.strip()
    
    def _extract_info_from_snippet(self, snippet: str) -> str:
        """Extract useful information from the search result snippet."""
        # Look for ingredients list or start of instructions
        ingredients_match = re.search(r"(?:ingredients|you['']ll need)[:;]?\s*(.*?)(?:\.|$)", snippet, re.IGNORECASE)
        if ingredients_match:
            return ingredients_match.group(0)
        
        # Just return the first sentence if no ingredients found
        first_sentence = re.split(r'[.!?]', snippet)[0]
        if first_sentence:
            return first_sentence + "."
        
        return snippet[:150] + "..." if len(snippet) > 150 else snippet
    
    def _extract_source(self, url: str) -> str:
        """Extract source website name from URL."""
        match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if match:
            domain = match.group(1)
            # Remove common TLDs and split by dots
            base_domain = re.sub(r"\.(?:com|org|net|co\.uk|io)$", "", domain)
            return base_domain.split(".")[-1].capitalize()
        return "Unknown Source"
    
    def _format_response(self, results: List[Dict[str, Any]], dish_name: str) -> Dict[str, Any]:
        """
        Format search results into a user-friendly response.
        
        Args:
            results: List of filtered search results
            dish_name: Name of the dish
            
        Returns:
            Formatted response
        """
        if not results:
            return {
                "success": False,
                "message": f"I couldn't find any recipes for {dish_name}. Would you like to try a different dish?",
                "results": []
            }
        
        # Structured response with highlighted recipe
        top_recipe = results[0] if results else None
        additional_recipes = results[1:] if len(results) > 1 else []
        
        return {
            "success": True,
            "message": f"I found some great recipes for {dish_name}!",
            "top_recipe": top_recipe,
            "additional_recipes": additional_recipes,
            "result_count": len(results)
        }