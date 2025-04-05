# src/parser.py

import re
import pandas as pd
from typing import List, Dict, Tuple, Optional

class RecipeParser:
    def __init__(self):
        # Common measurement units
        self.units = [
            'cup', 'cups', 'tablespoon', 'tablespoons', 'tbsp', 'teaspoon', 'teaspoons', 'tsp',
            'ounce', 'ounces', 'oz', 'pound', 'pounds', 'lb', 'lbs', 'gram', 'grams', 'g',
            'kilogram', 'kilograms', 'kg', 'ml', 'milliliter', 'milliliters', 'liter', 'liters', 'l',
            'pinch', 'pinches', 'dash', 'dashes', 'clove', 'cloves', 'piece', 'pieces', 'slice', 'slices',
            'bunch', 'bunches', 'whole', 'can', 'cans', 'package', 'packages', 'pkg', 'jar', 'jars'
        ]
        
        # Create regex pattern for measurements
        self.measurement_pattern = re.compile(
            r'(\d+(?:\.\d+)?(?:\s+\d+/\d+)?|\d+/\d+)\s*(' + '|'.join(self.units) + r')?\s+(?:of\s+)?(.+)',
            re.IGNORECASE
        )
        
        # Pattern for fractions
        self.fraction_pattern = re.compile(r'(\d+)/(\d+)')
    
    def parse_recipe_row(self, row: Dict) -> Dict:
        """Parse a recipe row from the dataset."""
        result = {
            'name': row.get('name', '').strip(),
            'ingredients_list': self._parse_ingredients(row),
            'steps': row.get('steps', [])
        }
        return result
    
    def _parse_ingredients(self, row: Dict) -> List[str]:
        """Extract ingredients from the row."""
        # Get ingredients from the ingredients column
        ingredients_raw = row.get('ingredients', [])
        
        # If ingredients is a string, convert to list
        if isinstance(ingredients_raw, str):
            try:
                # Try to evaluate as a Python list
                ingredients_raw = eval(ingredients_raw)
            except:
                # If not a valid Python list, split by commas
                ingredients_raw = ingredients_raw.split(',')
        
        # Clean ingredient names
        cleaned_ingredients = []
        for ingredient in ingredients_raw:
            if isinstance(ingredient, str):
                cleaned_ingredients.append(ingredient.strip())
        
        return cleaned_ingredients
    
    def extract_quantities_from_steps(self, recipe_name: str, ingredients: List[str], steps: List[str]) -> Dict[str, str]:
        """Extract quantities from recipe steps."""
        quantities = {}
        combined_steps = ' '.join(steps) if isinstance(steps, list) else steps
        
        # For each ingredient, try to find a quantity in the steps
        for ingredient in ingredients:
            # Extract base ingredient name (remove qualifiers like "fresh", "chopped", etc.)
            base_ingredient = self._get_base_ingredient(ingredient)
            
            # Look for measurements near the ingredient name
            quantity = self._find_quantity_in_text(combined_steps, base_ingredient)
            
            if quantity:
                quantities[ingredient] = quantity
        
        return quantities
    
    def _get_base_ingredient(self, ingredient: str) -> str:
        """Extract the base ingredient name without qualifiers."""
        # Remove common qualifiers
        qualifiers = ['fresh', 'dried', 'chopped', 'minced', 'sliced', 'diced', 'ground', 'grated', 'shredded']
        base = ingredient.lower()
        
        for qualifier in qualifiers:
            base = base.replace(qualifier, '').strip()
        
        return base
    
    def _find_quantity_in_text(self, text: str, ingredient: str) -> Optional[str]:
        """Find quantity for an ingredient in text."""
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        ingredient_lower = ingredient.lower()
        
        # Search for the ingredient in the text
        ingredient_pos = text_lower.find(ingredient_lower)
        
        if ingredient_pos >= 0:
            # Look for measurements before the ingredient
            # Check 100 characters before the ingredient position
            search_start = max(0, ingredient_pos - 100)
            text_before = text[search_start:ingredient_pos]
            
            # Find all numbers and units in the text before
            matches = re.findall(
                r'(\d+(?:\.\d+)?(?:\s+\d+/\d+)?|\d+/\d+)\s*(' + '|'.join(self.units) + r')?', 
                text_before
            )
            
            if matches:
                # Get the last match (closest to ingredient)
                quantity, unit = matches[-1]
                if unit:
                    return f"{quantity} {unit}"
                else:
                    return quantity
        
        return None
    
    def normalize_fraction(self, quantity: str) -> float:
        """Convert fraction string to float."""
        if not quantity:
            return 0.0
            
        # Check if it's a mixed number (e.g., "1 1/2")
        parts = quantity.split()
        if len(parts) > 1:
            try:
                whole = float(parts[0])
                fraction_part = self._fraction_to_float(parts[1])
                return whole + fraction_part
            except:
                pass
        
        # Check if it's a simple fraction (e.g., "1/2")
        fraction_match = self.fraction_pattern.match(quantity)
        if fraction_match:
            return self._fraction_to_float(quantity)
        
        # Try to convert to float directly
        try:
            return float(quantity)
        except:
            return 0.0
    
    def _fraction_to_float(self, fraction: str) -> float:
        """Convert a fraction string to float."""
        try:
            if '/' in fraction:
                num, denom = fraction.split('/')
                return float(num) / float(denom)
            return float(fraction)
        except:
            return 0.0