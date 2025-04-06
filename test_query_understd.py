# test_query_agent.py
from mvp.agents.query_understanding_agent import QueryUnderstandingAgent

def test_queries():
    agent = QueryUnderstandingAgent()
    
    test_cases = [
        "How do I make chocolate chip cookies?",
        "Convert 2 cups of flour to grams",
        "How many teaspoons are in 1/4 cup of sugar?",
        "Recipe for grilled cheese sandwich",
        "What's the best way to cook pasta?"
    ]
    
    for query in test_cases:
        result = agent.process(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result['intent']} (Confidence: {result['confidence']:.2f})")
        print(f"Entities: {result['entities']}")
        print(f"Parameters: {result['parameters']}")

if __name__ == "__main__":
    test_queries()