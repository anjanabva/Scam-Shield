import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Model Configuration
LLM_MODEL = "gpt-5.4-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# Pinecone Config
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Paths
SCAM_CORPUS_PATH = "./data/scam_corpus.json"