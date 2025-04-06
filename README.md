# Demeter: Your Culinary Assistant


## 🌿 Live Demo

The application is deployed and accessible at: [demeter-mvp.streamlit.app](https://demeter-mvp.streamlit.app)

## 📖 Overview

Demeter is an AI-powered culinary assistant designed to help users with recipe conversions, ingredient substitutions, and recipe discovery. The project utilizes multiple specialized agents for different tasks, all integrated through a streamlined user interface.

## 🧩 Project Components

### Agent Architecture

Demeter is built with a multi-agent architecture where specialized components handle different aspects of user queries:

1. **Query Understanding Agent**: Parses natural language inputs to understand user intent and extract parameters
2. **Conversion Agent**: Handles measurement unit conversions (e.g., cups to grams)
3. **Recipe Retrieval Agent**: Searches for and formats cooking recipes
4. **Substitution Agent**: Suggests alternative ingredients based on dietary restrictions or availability

### Technology Stack

- **Frontend**: Streamlit for the web interface
- **Backend**: Python with specialized agent modules
- **LLM Integration**:
  - **Llama3 70B**: Currently used for query processing and recipe generation
  - **Gemini Pro**: Initially used but temporarily disabled due to maximized API calls
  - **Phi-Data**: Used for agent integration and orchestration

## 🔄 Data Processing

The project involves extensive data processing to enhance the quality and accuracy of responses:

- **Dataset**: Currently processing 231,638 rows of recipe and ingredient data
- **Processing Method**: Data is handled in batches of 200 rows to optimize processing time and memory usage
- **Optimization**: Unsloth library is used for efficient model fine-tuning
- **Search Integration**: DuckDuckGo search API for recipe retrieval when needed
- **Development Environment**: Google Colab for model training and data processing

### Fine-Tuning Plans

Once the dataset processing is complete, we plan to fine-tune Gemini using Google Vertex AI with our processed recipe and conversion data to further enhance the system's understanding of culinary concepts.

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Streamlit
- Required libraries listed in `requirements.txt`

### Installation

```bash
# Clone the repository
git clone https://github.com/RSKMN/demeter.git
cd demeter

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your API keys

# Run the application
streamlit run app.py
```

## 🤖 Usage Examples

When using the Demeter app, try queries like:

- **Unit Conversions**: "Convert 2 cups of flour to grams"
- **Single Ingredient Conversions**: "How many grams is 1 teaspoon of salt?"
- **Recipe Requests**: "Find me a recipe for chocolate chip cookies"
- **Substitution Queries**: "What can I substitute for eggs in a cake recipe?"

Note: The app currently processes one conversion request at a time. For multiple conversions, please submit separate queries.

## 🛠️ Project Structure

```
demeter/
├── app.py                  # Main Streamlit application
├── agents/
│   ├── __init__.py
│   ├── query_understanding_agent.py
│   ├── conversion_agent.py
│   ├── recipe_retrieval_agent.py
│   └── substitution_agent.py
├── data/
│   ├── conversion_factors.json
│   └── ingredient_densities.json
├── utils/
│   ├── __init__.py
│   └── helpers.py
└── requirements.txt
```

## 🔜 Roadmap

- Complete dataset processing and model fine-tuning
- Implement more sophisticated conversions for complex ingredients
- Add meal planning capabilities
- Integrate dietary restriction awareness
- Develop mobile application


## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👏 Acknowledgments

- Recipe datasets used for training
- Open-source LLM communities
- Streamlit for the app framework