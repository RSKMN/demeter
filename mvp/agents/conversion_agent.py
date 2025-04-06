# agents/conversion_agent.py
from typing import Dict, List, Optional, Any, Tuple, Union
from agents.base_agent import BaseAgent
from duckduckgo_search import DDGS
import re
import google.generativeai as genai
import json

class ConversionAgent(BaseAgent):
    """
    Agent responsible for handling measurement conversions in cooking context.
    Uses DuckDuckGo search for density information and Gemini API for calculations.
    """
    
    def __init__(self, api_key: str):
        super().__init__(name="ConversionAgent")
        self.ddgs = DDGS()
        self.api_key = api_key
        self._initialize_gemini()
        
        # Common conversion factors
        self.volume_conversions = {
            # Base unit: milliliters (ml)
            "ml": 1,
            "milliliter": 1,
            "milliliters": 1,
            "millilitre": 1,
            "millilitres": 1,
            "cc": 1,
            "tsp": 4.93,
            "teaspoon": 4.93,
            "teaspoons": 4.93,
            "tbsp": 14.79,
            "tablespoon": 14.79,
            "tablespoons": 14.79,
            "fl oz": 29.57,
            "fluid ounce": 29.57,
            "fluid ounces": 29.57,
            "cup": 236.59,
            "cups": 236.59,
            "pint": 473.18,
            "pints": 473.18,
            "pt": 473.18,
            "quart": 946.35,
            "quarts": 946.35,
            "qt": 946.35,
            "gallon": 3785.41,
            "gallons": 3785.41,
            "gal": 3785.41,
            "liter": 1000,
            "liters": 1000,
            "litre": 1000,
            "litres": 1000,
            "l": 1000
        }
        
        self.weight_conversions = {
            # Base unit: grams (g)
            "g": 1,
            "gram": 1,
            "grams": 1,
            "kg": 1000,
            "kilogram": 1000,
            "kilograms": 1000,
            "kilo": 1000,
            "kilos": 1000,
            "oz": 28.35,
            "ounce": 28.35,
            "ounces": 28.35,
            "lb": 453.59,
            "pound": 453.59,
            "pounds": 453.59,
            "#": 453.59
        }
        
        # Common ingredient densities (g/ml)
        self.densities = {
            "water": 1.0,
            "milk": 1.03,
            "flour": 0.55,
            "all purpose flour": 0.55,
            "all-purpose flour": 0.55,
            "bread flour": 0.53,
            "cake flour": 0.4,
            "sugar": 0.85,
            "granulated sugar": 0.85,
            "brown sugar": 0.75,
            "powdered sugar": 0.56,
            "confectioners sugar": 0.56,
            "butter": 0.96,
            "oil": 0.92,
            "vegetable oil": 0.92,
            "olive oil": 0.92,
            "honey": 1.42,
            "maple syrup": 1.32,
            "salt": 1.22,
            "rice": 0.75,
            "oats": 0.4,
            "yogurt": 1.0,
            "cream": 1.0
        }
    
    def _initialize_gemini(self):
        """Initialize Gemini API client."""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def process(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process conversion request based on parameters.
        
        Args:
            parameters: Dictionary containing conversion parameters
                - quantity: Amount to convert
                - from_unit: Source unit
                - to_unit: Target unit
                - ingredient: Ingredient being converted
                - conversion_query: Original query (fallback)
                
        Returns:
            Dictionary containing conversion results
        """
        # Extract parameters
        quantity = parameters.get("quantity")
        # from_unit = parameters.get("from_unit")
        # to_unit = parameters.get("to_unit")
        ingredient = parameters.get("ingredient")
        original_query = parameters.get("conversion_query", "")
        
        # If we're missing needed parameters, try to extract them from original query
        if not all([quantity, from_unit, to_unit]) and original_query:
            extracted = self._extract_conversion_params(original_query)
            quantity = quantity or extracted.get("quantity")
            from_unit = from_unit or extracted.get("from_unit")
            to_unit = to_unit or extracted.get("to_unit")
            ingredient = ingredient or extracted.get("ingredient")
        
        # Convert string quantity to number
        try:
            if quantity and isinstance(quantity, str):
                if "/" in quantity:
                    # Handle fractions
                    parts = quantity.split("/")
                    quantity = float(parts[0]) / float(parts[1])
                else:
                    quantity = float(quantity)
        except (ValueError, ZeroDivisionError):
            quantity = None
        
        # If we still don't have required parameters, fall back to Gemini
        # if not all([quantity, from_unit, to_unit]):
        if(1):
            return self._fallback_to_gemini(original_query)
        
        # Normalize units
        from_unit = self._normalize_unit(from_unit)
        to_unit = self._normalize_unit(to_unit)
        
        # Determine conversion type (volume-to-volume, weight-to-weight, or needs density)
        result = self._perform_conversion(quantity, from_unit, to_unit, ingredient)
        
        # Validate the result
        validated_result = self._validate_result(result, quantity, from_unit, to_unit, ingredient)
        
        return validated_result
    
    def _extract_conversion_params(self, query: str) -> Dict[str, Any]:
        """Extract conversion parameters from a natural language query."""
        # Patterns to match different query formats
        patterns = [
            # "Convert X cups of flour to grams"
            r"(?:convert|change|transform)\s+(\d+(?:\.\d+)?|(?:\d+\/\d+))\s*([a-zA-Z\s]+)(?:\s+of\s+)?([a-zA-Z\s]+)?\s+(?:to|into)\s+([a-zA-Z\s]+)",
            
            # "How many grams in X cups of flour"
            r"(?:how\s+many|what\s+is)\s+([a-zA-Z\s]+)\s+(?:is|are|in)\s+(\d+(?:\.\d+)?|(?:\d+\/\d+))\s*([a-zA-Z\s]+)(?:\s+of\s+)?([a-zA-Z\s]+)?",
            
            # "X cups of flour in grams"
            r"(\d+(?:\.\d+)?|(?:\d+\/\d+))\s*([a-zA-Z\s]+)(?:\s+of\s+)?([a-zA-Z\s]+)?\s+(?:to|into|in)\s+([a-zA-Z\s]+)"
        ]
        
        query = query.lower().strip()
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                groups = match.groups()
                if pattern == patterns[0]:  # First pattern
                    return {
                        "quantity": groups[0],
                        "from_unit": groups[1].strip(),
                        "ingredient": groups[2].strip() if groups[2] else None,
                        "to_unit": groups[3].strip()
                    }
                elif pattern == patterns[1]:  # Second pattern
                    return {
                        "quantity": groups[1],
                        "from_unit": groups[2].strip(),
                        "ingredient": groups[3].strip() if groups[3] else None,
                        "to_unit": groups[0].strip()
                    }
                else:  # Third pattern
                    return {
                        "quantity": groups[0],
                        "from_unit": groups[1].strip(),
                        "ingredient": groups[2].strip() if groups[2] else None,
                        "to_unit": groups[3].strip()
                    }
        
        # If no pattern matches, return empty dictionary
        return {}
    
    def _normalize_unit(self, unit: str) -> str:
        """Normalize unit names to standard format."""
        if not unit:
            return unit
            
        unit = unit.lower().strip()
        
        # Handle plural forms and common abbreviations
        if unit in self.volume_conversions:
            return unit
        if unit in self.weight_conversions:
            return unit
            
        # Check for singular/plural forms
        if unit.endswith('s') and unit[:-1] in self.volume_conversions:
            return unit[:-1]
        if unit.endswith('s') and unit[:-1] in self.weight_conversions:
            return unit[:-1]
            
        # Common abbreviations and alternatives
        unit_map = {
            "milliliter": "ml", "millilitre": "ml",
            "liter": "l", "litre": "l",
            "teaspoon": "tsp", "tablespoon": "tbsp",
            "fluid ounce": "fl oz", "fluid oz": "fl oz",
            "ounce": "oz", "pound": "lb",
            "gram": "g", "kilogram": "kg",
            "cubic centimeter": "ml", "cubic centimetre": "ml",
            "c": "cup", "pt": "pint", "qt": "quart", "gal": "gallon"
        }
        
        for key, value in unit_map.items():
            if unit == key or unit == key + "s":
                return value
                
        # Return the original if no match
        return unit
    
    def _get_density(self, ingredient: str) -> float:
        """
        Get the density of an ingredient in g/ml.
        If not in our database, search online.
        """
        if not ingredient:
            return None
            
        ingredient = ingredient.lower().strip()
        
        # Check our database first
        if ingredient in self.densities:
            return self.densities[ingredient]
            
        # Try to find by partial match
        for key, value in self.densities.items():
            if key in ingredient or ingredient in key:
                return value
                
        # If not found, search online
        try:
            search_query = f"density of {ingredient} in g/ml cooking"
            results = self.ddgs.text(search_query, max_results=3)
            
            # Try to extract density from search results
            for result in results:
                body = result.get("body", "").lower()
                
                # Look for patterns like "density of X is Y g/ml" or "Y g/ml"
                density_patterns = [
                    r"density of [a-zA-Z\s]+ is (\d+(?:\.\d+)?)\s*g/ml",
                    r"(\d+(?:\.\d+)?)\s*g/ml",
                    r"(\d+(?:\.\d+)?)\s*grams? per milliliter"
                ]
                
                for pattern in density_patterns:
                    match = re.search(pattern, body)
                    if match:
                        try:
                            return float(match.group(1))
                        except ValueError:
                            pass
            
            # Fallback to Gemini for density information
            response = self.model.generate_content(
                f"What is the density of {ingredient} in g/ml? Reply with just the number, nothing else."
            )
            
            density_text = response.text.strip()
            try:
                # Extract just the number
                density_match = re.search(r"(\d+(?:\.\d+)?)", density_text)
                if density_match:
                    return float(density_match.group(1))
            except Exception:
                pass
                
        except Exception as e:
            print(f"Error getting density: {e}")
        
        # Default to water density if we can't find anything
        return 1.0
    
    def _perform_conversion(self, quantity: float, from_unit: str, to_unit: str, ingredient: str) -> Dict[str, Any]:
        """
        Perform the measurement conversion.
        
        Args:
            quantity: Amount to convert
            from_unit: Source unit
            to_unit: Target unit
            ingredient: Ingredient being converted
            
        Returns:
            Dictionary with conversion result
        """
        # Check if both units are volume units
        from_is_volume = from_unit in self.volume_conversions
        to_is_volume = to_unit in self.volume_conversions
        
        # Check if both units are weight units
        from_is_weight = from_unit in self.weight_conversions
        to_is_weight = to_unit in self.weight_conversions
        
        # Same unit type conversion (volume to volume or weight to weight)
        if from_is_volume and to_is_volume:
            # Convert to base units (ml) and then to target units
            base_value = quantity * self.volume_conversions[from_unit]
            result_value = base_value / self.volume_conversions[to_unit]
            return {
                "success": True,
                "original_value": quantity,
                "original_unit": from_unit,
                "converted_value": result_value,
                "converted_unit": to_unit,
                "ingredient": ingredient,
                "conversion_type": "volume-to-volume"
            }
            
        elif from_is_weight and to_is_weight:
            # Convert to base units (g) and then to target units
            base_value = quantity * self.weight_conversions[from_unit]
            result_value = base_value / self.weight_conversions[to_unit]
            return {
                "success": True,
                "original_value": quantity,
                "original_unit": from_unit,
                "converted_value": result_value,
                "converted_unit": to_unit,
                "ingredient": ingredient,
                "conversion_type": "weight-to-weight"
            }
            
        # Volume to weight or weight to volume (need density)
        elif ingredient:
            density = self._get_density(ingredient)
            
            if from_is_volume and to_is_weight:
                # Volume to weight: volume (ml) * density (g/ml) = weight (g)
                volume_ml = quantity * self.volume_conversions[from_unit]
                weight_g = volume_ml * density
                result_value = weight_g / self.weight_conversions[to_unit]
                return {
                    "success": True,
                    "original_value": quantity,
                    "original_unit": from_unit,
                    "converted_value": result_value,
                    "converted_unit": to_unit,
                    "ingredient": ingredient,
                    "density": density,
                    "conversion_type": "volume-to-weight"
                }
                
            elif from_is_weight and to_is_volume:
                # Weight to volume: weight (g) / density (g/ml) = volume (ml)
                weight_g = quantity * self.weight_conversions[from_unit]
                volume_ml = weight_g / density
                result_value = volume_ml / self.volume_conversions[to_unit]
                return {
                    "success": True,
                    "original_value": quantity,
                    "original_unit": from_unit,
                    "converted_value": result_value,
                    "converted_unit": to_unit,
                    "ingredient": ingredient,
                    "density": density,
                    "conversion_type": "weight-to-volume"
                }
        
        # If we get here, we couldn't perform the conversion
        return {
            "success": False,
            "message": "Could not perform conversion. Please check units and ingredient.",
            "original_value": quantity,
            "original_unit": from_unit,
            "requested_unit": to_unit,
            "ingredient": ingredient
        }
    
    def _validate_result(self, result: Dict[str, Any], quantity: float, from_unit: str, to_unit: str, ingredient: str) -> Dict[str, Any]:
        """
        Validate conversion results for reasonableness.
        
        Args:
            result: Conversion result
            quantity: Original quantity
            from_unit: Source unit
            to_unit: Target unit
            ingredient: Ingredient being converted
            
        Returns:
            Validated result, possibly with warnings
        """
        if not result["success"]:
            return result
        
        # Add rounded value for display
        converted_value = result["converted_value"]
        result["display_value"] = self._format_number(converted_value)
        
        # Check for extreme conversions
        if converted_value > 1000:
            result["warning"] = f"The converted value is very large ({result['display_value']} {to_unit}). Please verify this is correct."
        elif converted_value < 0.01 and converted_value > 0:
            result["warning"] = f"The converted value is very small ({result['display_value']} {to_unit}). Please verify this is correct."
        
        # If we're using density for conversion, verify it's reasonable
        if "density" in result and result["density"] > 2.0:
            result["warning"] = f"Using an unusually high density value ({result['density']} g/ml) for {ingredient}. Result may be inaccurate."
        
        return result
    
    def _format_number(self, number: float) -> str:
        """Format a number for readable display."""
        if number == int(number):
            return str(int(number))
        
        # For fractions, try to show common cooking fractions
        if number < 1:
            fractions = {0.25: "1/4", 0.33: "1/3", 0.5: "1/2", 0.67: "2/3", 0.75: "3/4"}
            for fraction_value, fraction_str in fractions.items():
                if abs(number - fraction_value) < 0.02:
                    return fraction_str
        
        # Otherwise show 1-2 decimal places
        return f"{number:.2f}".rstrip('0').rstrip('.') if '.' in f"{number:.2f}" else f"{number:.2f}"
    
    def _fallback_to_gemini(self, query: str) -> Dict[str, Any]:
        """
        Fallback to Gemini for complex conversions or when parsing fails.
        
        Args:
            query: Original conversion query
            
        Returns:
            Dictionary with conversion result
        """
        try:
            system_prompt = """
            You are a cooking conversion expert. Provide precise measurement conversions for cooking.
            Format your response as valid JSON with these fields:
            - "original_value": the starting quantity 
            - "original_unit": the unit being converted from
            - "converted_value": the numeric result of the conversion
            - "converted_unit": the unit being converted to
            - "ingredient": the ingredient being converted (if applicable)
            - "explanation": a brief explanation of the conversion
            
            Only provide the JSON response, no other text.
            """
            
            response = self.model.generate_content(
                [system_prompt, f"Convert this: {query}"]
            )
            
            try:
                # Try to parse the response as JSON
                result_json = json.loads(response.text.strip())
                
                return {
                    "success": True,
                    "original_value": result_json.get("original_value"),
                    "original_unit": result_json.get("original_unit"),
                    "converted_value": result_json.get("converted_value"),
                    "converted_unit": result_json.get("converted_unit"),
                    "ingredient": result_json.get("ingredient"),
                    "display_value": self._format_number(float(result_json.get("converted_value", 0))),
                    "explanation": result_json.get("explanation"),
                    "conversion_type": "gemini"
                }
            except json.JSONDecodeError:
                # If not valid JSON, extract what we can
                return {
                    "success": True,
                    "gemini_response": response.text.strip(),
                    "conversion_type": "gemini_text"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Could not perform conversion. {str(e)}",
                "original_query": query
            }