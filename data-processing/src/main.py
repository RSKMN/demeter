# src/main.py

import os
import pandas as pd
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import json
import argparse

from .knowledge_base import KnowledgeBase
from .web_search import WebSearchManager
from .parser import RecipeParser
from .converter import RecipeConverter

def process_recipes(input_file: str, output_file: str, batch_size: int = 10):
    """Process recipes from input CSV and save to output CSV."""
    # Create output directory if it doesn't exist
    output_path = Path(output_file).parent
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize components
    knowledge_base = KnowledgeBase()
    web_search = WebSearchManager(knowledge_base)
    parser = RecipeParser()
    converter = RecipeConverter(knowledge_base, web_search)
    
    # Read input CSV
    # src/main.py (continued)

    print(f"Reading recipes from {input_file}...")
    try:
        df = pd.read_csv(input_file, sep='\t')
    except Exception as e:
        print(f"Error reading input file: {e}")
        try:
            df = pd.read_csv(input_file)  # Try with default separator
        except Exception as e:
            print(f"Could not read file: {e}")
            return
    
    print(f"Found {len(df)} recipes.")
    
    # Initialize result columns
    df['standard_ingredients'] = None
    df['metric_ingredients'] = None
    
    # Process in batches
    for i in range(0, len(df), batch_size):
        print(f"Processing batch {i//batch_size + 1}/{(len(df) + batch_size - 1)//batch_size}...")
        batch = df.iloc[i:i+batch_size].copy()
        
        for idx, row in tqdm(batch.iterrows(), total=len(batch), desc="Processing recipes"):
            try:
                # Parse recipe
                recipe = parser.parse_recipe_row(row)
                
                # Generate standard ingredients list
                standard_ingredients = converter.generate_standard_ingredient_list(recipe)
                standard_ingredients_str = json.dumps(standard_ingredients)
                
                # Generate metric ingredients list
                metric_ingredients = converter.generate_metric_ingredient_list(standard_ingredients)
                metric_ingredients_str = json.dumps(metric_ingredients)
                
                # Update dataframe
                df.at[idx, 'standard_ingredients'] = standard_ingredients_str
                df.at[idx, 'metric_ingredients'] = metric_ingredients_str
            except Exception as e:
                print(f"Error processing recipe at index {idx}: {e}")
                # Set to empty lists for failed processing
                df.at[idx, 'standard_ingredients'] = "[]"
                df.at[idx, 'metric_ingredients'] = "[]"
        
        # Save knowledge base after each batch to preserve progress
        knowledge_base.save()
    
    # Save results
    print(f"Saving results to {output_file}...")
    df.to_csv(output_file, index=False)
    print("Conversion complete!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Convert recipe ingredients to standard and metric formats')
    parser.add_argument('--input', '-i', required=True, help='Input CSV file path')
    parser.add_argument('--output', '-o', required=True, help='Output CSV file path')
    parser.add_argument('--batch-size', '-b', type=int, default=10, help='Batch size for processing')
    
    args = parser.parse_args()
    
    process_recipes(args.input, args.output, args.batch_size)

if __name__ == "__main__":
    main()