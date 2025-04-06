import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_api():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Hello, testing the Gemini API connection.")
        print("API Test Response:", response.text)
        return True
    except Exception as e:
        print(f"Error connecting to Gemini API: {e}")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    if success:
        print("Environment setup successful! Gemini API is working.")
    else:
        print("Environment setup failed. Please check your API key and try again.")