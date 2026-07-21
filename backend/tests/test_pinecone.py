import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config

print("--- Pinecone Connection Test ---")
print(f"Index Name in Config: {config.PINECONE_INDEX_NAME}")
print(f"API Key present: {bool(config.PINECONE_API_KEY)}")

try:
    from rag.vectorstore import index
    if index:
        print("\nSUCCESS: Connected to Pinecone index!")
        stats = index.describe_index_stats()
        print(f"Index Stats: {stats}")
    else:
        print("\nFAILURE: Index object is None. Check if your API key and index name are correct in .env.")
except Exception as e:
    print(f"\nERROR: Failed to connect to Pinecone. Exception: {e}")
