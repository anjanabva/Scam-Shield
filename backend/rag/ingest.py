import json
import asyncio
import logging
import sys
import os

# Ensure Python can find our backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from llm.openai_client import get_embedding
from rag.vectorstore import upsert_documents

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ingest")

BATCH_SIZE = 10  # Pinecone upsert limit and to avoid rate limiting

async def process_and_upsert():
    logger.info(f"Loading corpus from {config.SCAM_CORPUS_PATH}")
    
    try:
        with open(config.SCAM_CORPUS_PATH, "r", encoding="utf-8") as f:
            corpus = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load corpus file: {e}")
        return

    logger.info(f"Loaded {len(corpus)} entries. Starting embedding generation...")
    
    vectors_to_upsert = []
    
    # Process sequentially to avoid hitting OpenAI rate limits on a free tier
    for i, item in enumerate(corpus):
        summary = item.get("script_summary")
        item_id = item.get("id")
        
        if not summary or not item_id:
            logger.warning(f"Skipping item {i} due to missing id or script_summary")
            continue
            
        logger.info(f"Generating embedding for {item_id} ({i+1}/{len(corpus)})...")
        embedding = await get_embedding(summary)
        
        if not embedding:
            logger.error(f"Failed to generate embedding for {item_id}")
            continue
            
        vector = {
            "id": item_id,
            "values": embedding,
            "metadata": item  # Store the entire object so we can retrieve title/flags easily
        }
        vectors_to_upsert.append(vector)
        
        # Batch upsert
        if len(vectors_to_upsert) >= BATCH_SIZE:
            logger.info(f"Upserting batch of {len(vectors_to_upsert)} vectors...")
            upsert_documents(vectors_to_upsert, namespace="scam_corpus")
            vectors_to_upsert = []
            
    # Upsert remaining
    if vectors_to_upsert:
        logger.info(f"Upserting final batch of {len(vectors_to_upsert)} vectors...")
        upsert_documents(vectors_to_upsert, namespace="scam_corpus")
        
    logger.info("Ingestion complete!")

if __name__ == "__main__":
    asyncio.run(process_and_upsert())