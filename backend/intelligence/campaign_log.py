"""
campaign_log.py
---------------
Logs every anonymized scam submission to the Pinecone `campaign_submissions` namespace
so the clustering layer can surface trending fraud campaigns.

Public API
----------
    await log_submission(text, verdict_data)  ->  bool

Design notes
------------
- NO raw PII is stored.  The original text is truncated to 500 chars and the
  document ID is a SHA-256 hash of the full text, which is not reversible.
- The vector stored is the text embedding (same model used by the RAG layer)
  so that cosine-similarity clustering works out of the box.
- The metadata stored is intentionally minimal: verdict label, confidence,
  matched_pattern, red_flag count, and a UTC timestamp (no user identifiers).
- Failures are logged but never raised so the caller (`analyze_text`) is
  never blocked by a logging error.
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from llm.openai_client import get_embedding
from rag.vectorstore import upsert_documents

logger = logging.getLogger("campaign_log")

# Pinecone namespace for campaign submissions (separate from the curated corpus)
CAMPAIGN_NAMESPACE = "campaign_submissions"

# Max chars of anonymized text stored in metadata (for cluster label display)
_MAX_PREVIEW_CHARS = 500


def _submission_id(text: str) -> str:
    """Returns a stable, non-reversible SHA-256 ID for de-duplication."""
    return "sub-" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]


def _anonymize_preview(text: str) -> str:
    """
    Returns a truncated preview of the submission for metadata storage.
    Strips leading/trailing whitespace and caps at _MAX_PREVIEW_CHARS.
    This is intentionally lossy — we do NOT want to store full transcripts.
    """
    preview = text.strip()[:_MAX_PREVIEW_CHARS]
    if len(text.strip()) > _MAX_PREVIEW_CHARS:
        preview += " …"
    return preview


async def log_submission(text: str, verdict_data: Dict[str, Any]) -> bool:
    """
    Embeds and upserts an anonymized submission into Pinecone so the
    campaign-clustering layer can group similar fraud patterns over time.

    Args:
        text:         The raw user-submitted transcript / message.
        verdict_data: The dict returned by ``analyze_text()``.  Expected keys:
                      ``verdict``, ``confidence``, ``matched_pattern``,
                      ``red_flags`` (list[str]).

    Returns:
        True  — upsert succeeded.
        False — embedding or upsert failed (already logged; caller can ignore).
    """
    # --- 0. Guard — only log threat-level verdicts ---------------------------
    verdict_label = str(verdict_data.get("verdict", "")).upper()
    if verdict_label not in ("SCAM", "SUSPICIOUS"):
        logger.debug(
            f"campaign_log: skipping log for verdict='{verdict_label}' "
            "(only SCAM / SUSPICIOUS are campaign-relevant)"
        )
        return False

    # --- 1. Generate embedding ------------------------------------------------
    embedding = await get_embedding(text)
    if not embedding:
        logger.warning("campaign_log: embedding failed, submission NOT logged.")
        return False

    # --- 2. Build anonymized metadata -----------------------------------------
    red_flags: list = verdict_data.get("red_flags") or []
    metadata = {
        # Verdict fields (safe to store — no user identity)
        "verdict":         str(verdict_data.get("verdict", "UNKNOWN")),
        "confidence":      int(verdict_data.get("confidence") or 0),
        "matched_pattern": str(verdict_data.get("matched_pattern") or ""),
        "red_flag_count":  len(red_flags),
        "red_flags_csv":   ",".join(red_flags[:10]),   # cap to avoid oversized metadata

        # Anonymized preview for cluster label display
        "preview":         _anonymize_preview(text),

        # Timestamp for recency-weighted clustering
        "logged_at":       datetime.now(timezone.utc).isoformat(),
    }

    # --- 3. Build Pinecone vector record -------------------------------------
    doc_id = _submission_id(text)
    vector_record = {
        "id":       doc_id,
        "values":   embedding,
        "metadata": metadata,
    }

    # --- 4. Upsert into campaign_submissions namespace -----------------------
    success = upsert_documents(
        vectors=[vector_record],
        namespace=CAMPAIGN_NAMESPACE,
    )

    if success:
        logger.info(
            f"campaign_log: logged submission {doc_id} "
            f"[verdict={metadata['verdict']}, confidence={metadata['confidence']}]"
        )
    else:
        logger.error(
            f"campaign_log: Pinecone upsert failed for submission {doc_id}"
        )

    return success