# data-processing/process.py

import os
import sys
import pandas as pd
import torch

# Add src/ to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.model_utils import load_llama_model

model, tokenizer = load_llama_model()

def process_ingredient(ingredient: str) -> str:
    prompt = f"""
Convert the following ingredient to a standardized quantity and metric equivalent.
If density is unknown or missing, respond with NEED_SEARCH.

Ingredient: {ingredient}
"""
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=100)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

def main():
    input_csv = "data-processing/data/input/recipes.csv"
    output_csv = "data-processing/data/output/converted_recipes.csv"

    if not os.path.exists(input_csv):
        print(f"[❌] CSV not found at {input_csv}")
        return

    df = pd.read_csv(input_csv)

    if 'ingredients' not in df.columns:
        print("[❌] 'ingredients' column missing.")
        return

    print("[🔁] Processing ingredients...")
    df['standardized_ingredients'] = df['ingredients'].apply(process_ingredient)
    df.to_csv(output_csv, index=False)
    print(f"[✅] Output saved to {output_csv}")

if __name__ == "__main__":
    main()
