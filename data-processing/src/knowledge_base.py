# src/knowledge_base.py

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

class KnowledgeBase:
    def __init__(self, base_path="data/knowledge_base"):
        self.base_path = Path(base_path)
        self.densities_path = self.base_path / "densities.json"
        self.conversions_path = self.base_path / "conversions.json"
        self.search_cache_path = self.base_path / "search_cache.json"
        
        # Ensure directories exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize knowledge bases
        self.densities = self._load_or_create(self.densities_path, self._initial_densities())
        self.conversions = self._load_or_create(self.conversions_path, self._initial_conversions())
        self.search_cache = self._load_or_create(self.search_cache_path, {})
    
    def _load_or_create(self, path: Path, default_data: Dict) -> Dict:
        """Load JSON file or create it with default data if it doesn't exist."""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        else:
            with open(path, 'w') as f:
                json.dump(default_data, f, indent=2)
            return default_data
    
    def save(self):
        """Save all knowledge bases to disk."""
        with open(self.densities_path, 'w') as f:
            json.dump(self.densities, f, indent=2)
        
        with open(self.conversions_path, 'w') as f:
            json.dump(self.conversions, f, indent=2)
        
        with open(self.search_cache_path, 'w') as f:
            json.dump(self.search_cache, f, indent=2)
    
    def get_density(self, ingredient: str) -> Optional[float]:
        """Get density for an ingredient (g/cup)."""
        # Normalize ingredient name
        normalized = self._normalize_ingredient(ingredient)
        
        # Direct lookup
        if normalized in self.densities:
            return self.densities[normalized]
        
        # Try to find partial matches
        for key, value in self.densities.items():
            if key in normalized or normalized in key:
                return value
        
        return None
    
    def add_density(self, ingredient: str, density: float):
        """Add or update density information."""
        normalized = self._normalize_ingredient(ingredient)
        self.densities[normalized] = density
        self.save()
    
    def convert_to_metric(self, quantity: float, unit: str, ingredient: str) -> Tuple[float, str]:
        """Convert a measurement to metric."""
        unit = unit.lower().strip()
        
        # Volume to volume conversions
        if unit in self.conversions["volume"]:
            ml_value = quantity * self.conversions["volume"][unit]
            
            # For small volumes, return in ml
            if ml_value < 100:
                return ml_value, "ml"
            # For larger volumes, convert to liters
            else:
                return ml_value / 1000, "L"
        
        # Weight to weight conversions
        elif unit in self.conversions["weight"]:
            g_value = quantity * self.conversions["weight"][unit]
            
            # For small weights, return in grams
            if g_value < 1000:
                return g_value, "g"
            # For larger weights, convert to kilograms
            else:
                return g_value / 1000, "kg"
        
        # Volume to weight conversions (using density)
        elif unit in self.conversions["volume_units"]:
            ml_value = quantity * self.conversions["volume"][unit]
            density = self.get_density(ingredient)
            
            if density:
                # Convert volume to weight using density
                g_value = ml_value * density / 240  # Density is g/cup, and 1 cup = 240ml
                if g_value < 1000:
                    return g_value, "g"
                else:
                    return g_value / 1000, "kg"
            else:
                # If no density available, return volume
                if ml_value < 100:
                    return ml_value, "ml"
                else:
                    return ml_value / 1000, "L"
        
        # Count units (no conversion needed)
        elif unit in self.conversions["count_units"]:
            return quantity, unit
        
        # Unknown unit
        return quantity, unit
    
    def _normalize_ingredient(self, ingredient: str) -> str:
        """Normalize ingredient name for consistent lookup."""
        return ingredient.lower().strip()
    
    def add_to_cache(self, query: str, result: Any):
        """Add search result to cache."""
        self.search_cache[query] = result
        self.save()
    
    def get_from_cache(self, query: str) -> Optional[Any]:
        """Get search result from cache."""
        return self.search_cache.get(query)
    
    def _initial_conversions(self) -> Dict:
        """Initialize conversion factors."""
        return {
            "volume": {
                "cup": 240,       # ml
                "tablespoon": 15, # ml
                "tbsp": 15,       # ml
                "teaspoon": 5,    # ml
                "tsp": 5,         # ml
                "fluid ounce": 30, # ml
                "fl oz": 30,      # ml
                "pint": 473,      # ml
                "quart": 946,     # ml
                "gallon": 3785,   # ml
                "ml": 1,          # ml
                "milliliter": 1,  # ml
                "l": 1000,        # ml
                "liter": 1000     # ml
            },
            "weight": {
                "pound": 453.592, # g
                "lb": 453.592,    # g
                "ounce": 28.35,   # g
                "oz": 28.35,      # g
                "gram": 1,        # g
                "g": 1,           # g
                "kg": 1000,       # g
                "kilogram": 1000  # g
            },
            "volume_units": [
                "cup", "tablespoon", "tbsp", "teaspoon", "tsp", 
                "fluid ounce", "fl oz", "pint", "quart", "gallon",
                "ml", "milliliter", "l", "liter"
            ],
            "weight_units": [
                "pound", "lb", "ounce", "oz", "gram", "g", "kg", "kilogram"
            ],
            "count_units": [
                "piece", "slice", "whole", "clove", "pinch", "dash"
            ]
        }
    
    def _initial_densities(self) -> Dict:
        """Initialize densities for common ingredients (g/cup)."""
        return {
            "flour": 120,
            "all-purpose flour": 120,
            "self-rising flour": 120,
            "cake flour": 115,
            "bread flour": 130,
            "whole wheat flour": 128,
            "sugar": 200,
            "white sugar": 200,
            "brown sugar": 220,
            "powdered sugar": 120,
            "confectioners' sugar": 120,
            "granulated sugar": 200,
            "honey": 340,
            "maple syrup": 328,
            "butter": 225,
            "vegetable oil": 218,
            "olive oil": 216,
            "milk": 240,
            "water": 240,
            "rice": 185,
            "white rice": 185,
            "brown rice": 190,
            "oats": 85,
            "salt": 288,
            "black pepper": 140,
            "baking powder": 192,
            "baking soda": 220,
            "cocoa powder": 85,
            "cornstarch": 125,
            "yeast": 150,
            "shredded cheese": 120,
            "cream cheese": 240,
            "yogurt": 245,
            "sour cream": 240,
            "mayonnaise": 220,
            "ketchup": 270,
            "mustard": 250,
            "chopped nuts": 120,
            "sliced almonds": 85,
            "chocolate chips": 170,
            "coffee": 150,
            "coffee grounds": 150
        }