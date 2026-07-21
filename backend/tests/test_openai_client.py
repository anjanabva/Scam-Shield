import asyncio
import sys

import os

# Ensure Python can find the llm module regardless of where the script is run from
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.openai_client import get_llm_response, get_embedding, token_usage_tracker

async def main():
    print("Testing get_llm_response...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short haiku about cybersecurity."}
    ]
    
    # Test text generation
    response_text, usage = await get_llm_response(messages)
    
    print("\n--- LLM Response ---")
    print(response_text)
    print("--------------------\n")
    
    # Test embeddings
    print("Testing get_embedding...")
    embedding = await get_embedding("digital arrest scam")
    
    if embedding:
        print(f"Embedding generated! Dimensions: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
    else:
        print("Failed to generate embedding.")
    
    # Verify the global usage tracker is working
    print("\n--- Final Token Usage Tracker ---")
    print(token_usage_tracker)

if __name__ == "__main__":
    asyncio.run(main())
