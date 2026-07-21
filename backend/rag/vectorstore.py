import logging
from pinecone import Pinecone
import config

logger = logging.getLogger("vectorstore")

# Initialize Pinecone client
try:
    if config.PINECONE_API_KEY and config.PINECONE_INDEX_NAME:
        pc = Pinecone(api_key=config.PINECONE_API_KEY)
        index = pc.Index(config.PINECONE_INDEX_NAME)
        logger.info(f"Successfully connected to Pinecone index: {config.PINECONE_INDEX_NAME}")
    else:
        logger.warning("Pinecone API key or Index Name is missing in .env")
        index = None
except Exception as e:
    logger.error(f"Failed to initialize Pinecone: {e}")
    index = None

def upsert_documents(vectors: list, namespace: str = "scam_corpus") -> bool:
    """
    Upserts a list of vectors into Pinecone.
    
    Args:
        vectors: A list of dicts formatted for Pinecone
        namespace: The Pinecone namespace to store the vectors in (default: 'scam_corpus')
        vectors: A list of dicts formatted for Pinecone, e.g.,
                 [{"id": "doc1", "values": [0.1, 0.2, ...], "metadata": {"text": "..."}}]
                 
    Returns:
        bool: True if successful, False otherwise.
    """
    if not index:
        logger.error("Pinecone index is not initialized.")
        return False
        
    try:
        index.upsert(vectors=vectors, namespace=namespace)
        logger.info(f"Successfully upserted {len(vectors)} documents to Pinecone namespace '{namespace}'.")
        return True
    except Exception as e:
        logger.error(f"Error upserting to Pinecone: {e}")
        return False

def search_similar(embedding: list[float], top_k: int = 3, include_metadata: bool = True, namespace: str = "scam_corpus") -> list:
    """
    Searches Pinecone for the top_k most similar vectors to the provided embedding.
    
    Args:
        embedding: The vector to search against.
        top_k: Number of results to return.
        include_metadata: Whether to return the stored metadata.
        namespace: The Pinecone namespace to search in (default: 'scam_corpus')
        
    Returns:
        A list of match dictionaries from Pinecone.
    """
    if not index:
        logger.error("Pinecone index is not initialized.")
        return []
        
    try:
        response = index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=include_metadata,
            namespace=namespace
        )
        return response.get('matches', [])
    except Exception as e:
        logger.error(f"Error querying Pinecone: {e}")
        return []