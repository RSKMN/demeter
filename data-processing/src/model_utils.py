# src/model_utils.py

from unsloth import FastLanguageModel
import torch

def load_llama_model():
    """
    Load Meta-Llama-3-8B-Instruct model using Unsloth.
    """
    print("[🔄] Loading Meta-Llama-3-8B-Instruct model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Meta-Llama-3-8B-Instruct-bnb-4bit",
    dtype = torch.float32,  # ⚠️ CPU-safe
    load_in_4bit = False     # Disable bitsandbytes
    )

    FastLanguageModel.for_inference(model)
    print("[✅] Model loaded.")
    return model, tokenizer
