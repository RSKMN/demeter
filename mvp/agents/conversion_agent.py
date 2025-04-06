import requests
import json
import re
# from .utils.density_utils import get_density
# from .utils.unit_utils import convert_to_metric

class ConversionAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-pro:generateContent?key={api_key}"

    def convert_ingredient(self, query: str):
        """
        Convert the given query using Gemini directly and return the raw text response.
        """
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": f"Convert the following ingredients to metric units (grams or ml as appropriate): {query}. Provide output as a plain text list."
                            }
                        ]
                    }
                ]
            }

            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            
            print("Gemini Raw Output:", result['candidates'][0]['content']['parts'][0]['text'])


            if response.status_code == 200:
                result = response.json()
                print("DEBUG: Raw Gemini response:", json.dumps(result, indent=2))

                # Return the entire raw response text, untouched
                return {
                    "success": True,
                    "conversion_type": "gemini_raw",
                    "message": result['candidates'][0]['content']['parts'][0]['text']
                }
            else:
                print("Error from Gemini API:", response.status_code, response.text)
                return {
                    "success": False,
                    "conversion_type": "gemini_error",
                    "message": response.text
                }
        except Exception as e:
            print("Exception during Gemini API call:", str(e))
            return {
                "success": False,
                "conversion_type": "exception",
                "message": str(e)
            }


# Example usage:
if __name__ == '__main__':
    agent = ConversionAgent(api_key="GOOGLE_API_KEY")
    query = "convert 2.5 cups of sugar and 1 teaspoon of salt into grams"
    print(agent.convert_ingredient(query))


# === Legacy Logic (commented out) ===
# def parse_ingredients(...):
#     # legacy parsing logic
#     pass

# def convert_with_density(...):
#     # uses DuckDuckGo density search
#     pass

# def validate_conversion(...):
#     # post-validation rules
#     pass
