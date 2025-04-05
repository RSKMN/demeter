# src/web_search.py

import re
import time
from typing import Dict, Any, Optional, List, Tuple
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests

class WebSearchManager:
    def __init__(self, knowledge_base, max_retries=3, delay=2):
        self.knowledge_base = knowledge_base
        self.max_retries = max_retries
        self.delay = delay
        self.ddgs = DDGS()
    
    def search_ingredient_density(self, ingredient: str) -> Optional[float]:
        """Search for ingredient density online."""
        # Check cache first
        cache_key = f"density_{ingredient}"
        cached = self.knowledge_base.get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Perform search
        query = f"{ingredient} density grams per cup cooking"
        
        try:
            results = self.search_with_retry(query)
            
            if not results:
                return None
            
            # Extract density from search results
            density = self._extract_density_from_results(results, ingredient)
            
            if density:
                # Add to cache and knowledge base
                self.knowledge_base.add_to_cache(cache_key, density)
                self.knowledge_base.add_density(ingredient, density)
                return density
                
        except Exception as e:
            print(f"Error searching for {ingredient} density: {e}")
        
        return None
    
    def search_ingredient_quantity(self, recipe_name: str, ingredient: str) -> Optional[str]:
        """Search for standard quantity of an ingredient in a recipe."""
        # Check cache first
        cache_key = f"quantity_{recipe_name}_{ingredient}"
        cached = self.knowledge_base.get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Perform search
        query = f"{recipe_name} recipe {ingredient} how much"
        
        try:
            results = self.search_with_retry(query)
            
            if not results:
                return None
            
            # Extract quantity from search results
            quantity = self._extract_quantity_from_results(results, ingredient)
            
            if quantity:
                # Add to cache
                self.knowledge_base.add_to_cache(cache_key, quantity)
                return quantity
                
        except Exception as e:
            print(f"Error searching for {ingredient} quantity in {recipe_name}: {e}")
        
        return None
    
    def search_with_retry(self, query: str) -> List[Dict[str, Any]]:
        """Perform search with retry logic."""
        for attempt in range(self.max_retries):
            try:
                results = list(self.ddgs.text(query, max_results=5))
                time.sleep(self.delay)  # Be nice to the search engine
                return results
            except Exception as e:
                print(f"Search attempt {attempt+1} failed: {e}")
                time.sleep(self.delay * (attempt + 1))  # Exponential backoff
        
        return []
    
    def _extract_density_from_results(self, results: List[Dict[str, Any]], ingredient: str) -> Optional[float]:
        """Extract density information from search results."""
        # Patterns to search for
        patterns = [
            r'(\d+(?:\.\d+)?)\s*g(?:rams)?\s*per\s*cup',
            r'(\d+(?:\.\d+)?)\s*g(?:rams)?\s*/\s*cup',
            r'cup\s*of\s*[^.]*?weighs\s*(\d+(?:\.\d+)?)\s*g(?:rams)?',
            r'density\s*of\s*[^.]*?is\s*(\d+(?:\.\d+)?)\s*g(?:rams)?\s*per\s*cup'
        ]
        
        for result in results:
            # Try to extract from snippet
            text = result.get('body', '')
            for pattern in patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        return float(matches.group(1))
                    except ValueError:
                        continue
            
            # Try to extract from title
            text = result.get('title', '')
            for pattern in patterns:
                matches = re.search(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        return float(matches.group(1))
                    except ValueError:
                        continue
                        
            # Try to visit the page for more detailed extraction
            try:
                url = result.get('href')
                if url:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        text = soup.get_text()
                        
                        # Look for density patterns
                        for pattern in patterns:
                            matches = re.search(pattern, text, re.IGNORECASE)
                            if matches:
                                try:
                                    return float(matches.group(1))
                                except ValueError:
                                    continue
            except:
                continue
        
        # Default densities for common ingredient categories
        if any(word in ingredient.lower() for word in ['flour', 'powder']):
            return 120.0  # Default flour density
        elif any(word in ingredient.lower() for word in ['sugar', 'sweetener']):
            return 200.0  # Default sugar density
        elif any(word in ingredient.lower() for word in ['oil', 'syrup']):
            return 240.0  # Default oil density
            
        return None
    
    def _extract_quantity_from_results(self, results: List[Dict[str, Any]], ingredient: str) -> Optional[str]:
        """Extract quantity information from search results."""
        # Pattern for ingredient quantities
        pattern = r'(\d+(?:\.\d+)?)\s*(?:cup|tablespoon|tbsp|teaspoon|tsp|oz|ounce|lb|pound|g|gram)s?\s+(?:of\s+)?[^,.]*?' + re.escape(ingredient)
        
        for result in results:
            # Try to extract from snippet
            text = result.get('body', '')
            matches = re.search(pattern, text, re.IGNORECASE)
            if matches:
                return matches.group(0)
                
            # Try to visit the page for more detailed extraction
            try:
                url = result.get('href')
                if url:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        ingredient_sections = soup.find_all(['li', 'p'])
                        
                        for section in ingredient_sections:
                            text = section.get_text()
                            if ingredient.lower() in text.lower():
                                matches = re.search(pattern, text, re.IGNORECASE)
                                if matches:
                                    return matches.group(0)
            except:
                continue
                
        return None