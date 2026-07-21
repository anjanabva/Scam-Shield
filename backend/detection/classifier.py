import json
import logging
from typing import Dict, Any

from detection.rules import evaluate_rules
from detection.prompts import SYSTEM_PROMPT, build_user_prompt, FOLLOWUP_SYSTEM_PROMPT, build_followup_prompt
from llm.openai_client import get_llm_response, get_embedding, stream_llm_response
from rag.vectorstore import search_similar

logger = logging.getLogger("classifier")

async def handle_followup(question: str, context: str, history: list = None) -> str:
    """
    Handles follow-up questions from the user after a scam analysis, including past chat history.
    """
    system_msg = FOLLOWUP_SYSTEM_PROMPT + f"\n\n### Original Transcript Context ###\n{context}"
    messages = [{"role": "system", "content": system_msg}]
    
    if history:
        for msg in history:
            role = "assistant" if msg.get("role") == "assistant" else "user"
            messages.append({"role": role, "content": msg.get("text", "")})
            
    messages.append({"role": "user", "content": question})
    
    response_text, usage = await get_llm_response(messages)
    
    if not response_text:
        return "Sorry, I'm having trouble connecting right now. Remember to block the suspicious contact and report to cybercrime.gov.in or 1930."
        
    return response_text

async def handle_followup_stream(question: str, context: str, history: list = None):
    """
    Handles follow-up questions from the user via streaming.
    """
    system_msg = FOLLOWUP_SYSTEM_PROMPT + f"\n\n### Original Transcript Context ###\n{context}"
    messages = [{"role": "system", "content": system_msg}]
    
    if history:
        for msg in history:
            role = "assistant" if msg.get("role") == "assistant" else "user"
            messages.append({"role": role, "content": msg.get("text", "")})
            
    messages.append({"role": "user", "content": question})
    
    async for chunk in stream_llm_response(messages):
        yield chunk

async def analyze_text(text: str) -> Dict[str, Any]:
    """
    The main orchestrator for Scam Shield.
    Takes user text, evaluates rules, retrieves RAG context, and gets the LLM verdict.
    """
    
    # 1. Rule-Based Deterministic Layer
    triggered_flags = evaluate_rules(text)
    logger.info(f"Triggered rule flags: {triggered_flags}")
    
    # 2. Embedding Generation
    embedding = await get_embedding(text)
    
    # 3. RAG Retrieval from Pinecone
    retrieved_context = []
    if embedding:
        retrieved_context = search_similar(embedding, top_k=3)
        logger.info(f"Retrieved {len(retrieved_context)} similar patterns from Pinecone.")
    
    # 4. Prompt Construction
    user_prompt = build_user_prompt(text, triggered_flags, retrieved_context)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    # 5. LLM Inference (forcing JSON output)
    response_text, usage = await get_llm_response(
        messages=messages,
        response_format={"type": "json_object"}
    )
    
    # 6. Parse and format the final output
    try:
        # Fallback if LLM fails
        if not response_text:
            raise ValueError("No response from LLM")
            
        verdict_data = json.loads(response_text)
        
        # Inject our deterministic flags into the final output
        verdict_data["red_flags"] = triggered_flags
        
        return verdict_data
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from LLM: {response_text}")
        return _fallback_response(triggered_flags)
    except Exception as e:
        logger.error(f"Error in analyze_text: {e}")
        return _fallback_response(triggered_flags)

def _fallback_response(triggered_flags: list[str]) -> Dict[str, Any]:
    """
    Provides a safe fallback response if the LLM or network fails, 
    relying entirely on the deterministic rule engine.
    """
    if triggered_flags:
        return {
            "verdict": "SUSPICIOUS",
            "confidence": 75,
            "matched_pattern": "Rule-based flag match",
            "explanation": "We detected concerning keywords typical of scams, but our AI analysis engine is currently unreachable. Please be cautious.",
            "red_flags": triggered_flags
        }
    else:
        return {
            "verdict": "UNKNOWN",
            "confidence": 0,
            "matched_pattern": None,
            "explanation": "Analysis engine is unreachable and no obvious red flags were detected. Please verify independently.",
            "red_flags": []
        }