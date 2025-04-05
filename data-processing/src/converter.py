# src/converter.py

import re
from typing import Dict, List, Tuple, Optional
from .knowledge_base import KnowledgeBase
from .web_search import WebSearchManager

class RecipeConverter:
    def __init__(self, knowledge_base: KnowledgeBase, web_search: WebSearchManager):
        self.knowledge_base = knowledge_base
        self.web_search = web_search
        
        # Pattern for extracting quantity and unit from ingredient string
        self.quantity_pattern = re.compile(
            r'^(\d+(?:\.\d+)?(?:\s+\d+/\d+)?|\d+/\d+)\s*(' + 
            '|'.join(knowledge_base.conversions["volume_units"] + 
                    knowledge_base.conversions["weight_units"] + 
                    knowledge_base.conversions["count_units"]) + 
            r')?\s+(?:of\s+)?(.+)$',
            re.IGNORECASE
        )
        
        # Pattern for fractions
        self.fraction_pattern = re.compile(r'(\d+)/(\d+)')
    
    def generate_standard_ingredient_list(self, recipe: Dict) -> List[str]:
        """Generate a standardized list of ingredients with quantities."""
        recipe_name = recipe['name']
        ingredients = recipe['ingredients_list']
        steps = recipe['steps']
        
        # Try to extract quantities from recipe steps
        quantities_from_steps = {}
        if steps:
            if isinstance(steps, str):
                steps = [steps]
            if isinstance(steps, list):
                from .parser import RecipeParser
                parser = RecipeParser()
                quantities_from_steps = parser.extract_quantities_from_steps(recipe_name, ingredients, steps)
        
        standard_ingredients = []
        
        for ingredient in ingredients:
            # Check if ingredient already has quantity
            quantity_match = self.quantity_pattern.match(ingredient)
            
            if quantity_match:
                # Ingredient already has quantity
                quantity, unit, ingredient_name = quantity_match.groups()
                standardized = f"{quantity} {unit} {ingredient_name}".strip()
                standard_ingredients.append(standardized)
            else:
                # Check if quantity was found in steps
                if ingredient in quantities_from_steps:
                    quantity = quantities_from_steps[ingredient]
                    standard_ingredients.append(f"{quantity} {ingredient}")
                else:
                    # Search for quantity online
                    quantity = self.web_search.search_ingredient_quantity(recipe_name, ingredient)
                    if quantity:
                        standard_ingredients.append(f"{quantity}")
                    else:
                        # No quantity found, add as is (to taste)
                        standard_ingredients.append(f"{ingredient} to taste")
        
        return standard_ingredients
    
    def generate_metric_ingredient_list(self, standard_ingredients: List[str]) -> List[str]:
        """Convert standard ingredients to metric."""
        metric_ingredients = []
        
        for ingredient_str in standard_ingredients:
            # Parse ingredient string
            parts = self._parse_ingredient_string(ingredient_str)
            
            if not parts:
                # Could not parse, keep as is
                metric_ingredients.append(ingredient_str)
                continue
                
            quantity, unit, ingredient_name = parts
            
            # Skip if no quantity or unit
            if not quantity or not unit:
                metric_ingredients.append(ingredient_str)
                continue
            
            # Convert quantity to float
            quantity_float = self._convert_to_float(quantity)
            
            # Get density if needed
            if unit in self.knowledge_base.conversions["volume_units"]:
                density = self.knowledge_base.get_density(ingredient_name)
                if not density:
                    # Search for density online
                    density = self.web_search.search_ingredient_density(ingredient_name)
            
            # Convert to metric
            metric_quantity, metric_unit = self.knowledge_base.convert_to_metric(
                quantity_float, unit, ingredient_name
            )
            
            # Format metric quantity
            if metric_quantity == int(metric_quantity):
                metric_quantity = int(metric_quantity)
            else:
                metric_quantity = round(metric_quantity, 1)
            
            # Create metric ingredient string
            metric_ingredient = f"{metric_quantity} {metric_unit} {ingredient_name}"
            metric_ingredients.append(metric_ingredient)
        
        return metric_ingredients
    
    def _parse_ingredient_string(self, ingredient_str: str) -> Optional[Tuple[str, str, str]]:
        """Parse ingredient string into quantity, unit, and name."""
        # Check for "to taste" format
        if "to taste" in ingredient_str:
            name = ingredient_str.replace("to taste", "").strip()
            return None, None, name
        
        # Try parsing with regex
        match = self.quantity_pattern.match(ingredient_str)
        if match:
            quantity, unit, name = match.groups()
            if not unit:
                unit = "piece"  # Default unit
            return quantity, unit, name
        
        # Handle special case where no clear pattern
        words = ingredient_str.split()
        if len(words) >= 2:
            # Check if first word is a number
            if self._is_number(words[0]):
                return words[0], words[1] if len(words) > 1 else "piece", " ".join(words[2:])
        
        return None, None, ingredient_str
    
    def _is_number(self, s: str) -> bool:
        """Check if string is a number or fraction."""
        if self.fraction_pattern.match(s):
            return True
        try:
            float(s)
            return True
        except:
            return False
    
    def _convert_to_float(self, quantity: str) -> float:
        """Convert quantity string to float."""
        try:
            # Check for mixed fraction (e.g., "1 1/2")
            parts = quantity.split()
            if len(parts) > 1:
                whole = float(parts[0])
                fraction = parts[1]
                if '/' in fraction:
                    num, denom = fraction.split('/')
                    return whole + (float(num) / float(denom))
                return whole
            
            # Check for simple fraction
            if '/' in quantity:
                num, denom = quantity.split('/')
                return float(num) / float(denom)
            
            # Simple number
            return float(quantity)
        except:
            return 0.0