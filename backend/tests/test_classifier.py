import sys
import os
import asyncio
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from detection.classifier import analyze_text

async def main():
    print("--- End-to-End Classifier Test ---\n")
    
    test_text = """
    Hello, I am an inspector from the Cyber Cell in Mumbai. Your Aadhaar card was found linked 
    to a money laundering case. Do not disconnect this Skype call. We need to do a verification 
    process. Please transfer Rs. 50,000 to our safe account immediately for clearance.
    """
    
    print("Input Text:")
    print(test_text.strip())
    print("\nAnalyzing... (Hitting rule engine, Pinecone, and OpenAI)\n")
    
    result = await analyze_text(test_text)
    
    print("--- Final Output ---")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
