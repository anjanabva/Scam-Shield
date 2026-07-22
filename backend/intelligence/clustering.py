"""
clustering.py
-------------
Queries the shared `campaign_submissions` Pinecone namespace — across **all
users** — and groups recent threat submissions by embedding similarity to
surface actively scaling fraud campaigns.

Public API
----------
    get_trending_campaigns(
        window_hours   = 24,   # look back N hours
        similarity_threshold = 0.75,  # cosine similarity to count as "same campaign"
        min_cluster_size     = 2,     # at least 2 different submissions to be a campaign
        top_n                = 5,     # return top N clusters by size
    ) -> list[dict]

Algorithm (greedy single-linkage, Pinecone-native)
--------------------------------------------------
  1. LIST all vector IDs in the namespace (Pinecone Serverless list() API)
  2. FETCH those vectors in batches to retrieve stored metadata
  3. FILTER to submissions whose `logged_at` falls within `window_hours`
  4. CLUSTER: for each unassigned submission, query Pinecone for its nearest
     neighbours within the same namespace. Neighbours with score ≥ threshold
     are merged into the same cluster. Already-assigned vectors are skipped.
  5. FILTER clusters where count < min_cluster_size
  6. SORT by cluster size descending, return top_n

Output shape (one item per cluster)
------------------------------------
  {
    "campaign_id":     "cluster-<short_hash>",
    "count":           6,
    "matched_pattern": "Fake customs officer / parcel scam",
    "top_red_flags":   ["urgency", "payment_demand", "impersonation"],
    "preview":         "This is the customs officer calling ...",
    "first_seen":      "2026-07-22T10:14:00Z",
    "last_seen":       "2026-07-22T11:52:00Z",
    "window_hours":    1.6,
  }
"""

import hashlib
import logging
from collections import Counter
from datetime import datetime, timezone, timedelta
from typing import Any

from rag.vectorstore import index

logger = logging.getLogger("clustering")

CAMPAIGN_NAMESPACE = "campaign_submissions"

# Pinecone list() returns IDs in pages; cap total IDs fetched per call
_MAX_IDS_TO_SCAN  = 20    # only look at the last 20 submissions
_FETCH_BATCH_SIZE = 10    # fetch in small batches of 10
_NEIGHBOUR_TOP_K  = 30    # neighbours to check per seed vector


# ── helpers ───────────────────────────────────────────────────────────────────

def _cluster_id(seed_id: str) -> str:
    """Stable short ID for a cluster based on its seed vector."""
    return "cluster-" + hashlib.sha256(seed_id.encode()).hexdigest()[:8]


def _parse_dt(iso_str: str) -> datetime | None:
    """Parse ISO-8601 string to UTC-aware datetime, returns None on failure."""
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _majority(values: list[str], fallback: str = "") -> str:
    """Return the most common non-empty string in a list."""
    counts = Counter(v for v in values if v)
    return counts.most_common(1)[0][0] if counts else fallback


def _top_flags(flag_csv_list: list[str], n: int = 5) -> list[str]:
    """Aggregate red_flags_csv strings from cluster members → top N flags."""
    all_flags: list[str] = []
    for csv in flag_csv_list:
        all_flags.extend(f.strip() for f in csv.split(",") if f.strip())
    return [flag for flag, _ in Counter(all_flags).most_common(n)]


# ── core function ─────────────────────────────────────────────────────────────

def get_trending_campaigns(
    window_hours: float = 24.0,
    similarity_threshold: float = 0.85,
    min_cluster_size: int = 2,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """
    Returns a list of trending campaign dicts (see module docstring for shape).
    Returns [] if Pinecone is unavailable or the namespace is empty.
    """
    if index is None:
        logger.error("clustering: Pinecone index not initialised.")
        return []

    # ── Step 1: list all vector IDs in the namespace ──────────────────────────
    # Pinecone SDK list() yields ListResponse objects where each page has a
    # .vectors attribute containing ListItem objects with an .id field.
    all_ids: list[str] = []
    try:
        for page in index.list(namespace=CAMPAIGN_NAMESPACE):
            if hasattr(page, "vectors"):
                # Standard SDK shape: ListResponse with ListItem objects
                all_ids.extend(item.id for item in page.vectors)
            elif isinstance(page, list):
                # Some SDK versions yield a plain list of ID strings
                all_ids.extend(str(v) for v in page)
            elif isinstance(page, str):
                all_ids.append(page)
            # else: unknown shape — skip silently
            if len(all_ids) >= _MAX_IDS_TO_SCAN:
                break
    except Exception as e:
        logger.error(f"clustering: failed to list vectors: {e}")
        return []

    if not all_ids:
        logger.info("clustering: campaign_submissions namespace is empty.")
        return []

    logger.info(f"clustering: found {len(all_ids)} total submission IDs")

    # ── Step 2: fetch vectors in batches to get values + metadata ────────────
    fetched: dict[str, dict] = {}   # id -> {values: [...], metadata: {...}}
    for i in range(0, len(all_ids), _FETCH_BATCH_SIZE):
        batch = all_ids[i : i + _FETCH_BATCH_SIZE]
        try:
            resp = index.fetch(ids=batch, namespace=CAMPAIGN_NAMESPACE)
            fetched.update(resp.get("vectors", {}))
        except Exception as e:
            logger.warning(f"clustering: batch fetch failed: {e}")

    logger.info(f"clustering: fetched {len(fetched)} vectors with metadata")

    # ── Step 3: filter to window_hours ────────────────────────────────────────
    cutoff = datetime.now(timezone.utc) - timedelta(hours=window_hours)
    recent: dict[str, dict] = {}
    for vid, vdata in fetched.items():
        meta = vdata.get("metadata") or {}
        logged_at = _parse_dt(meta.get("logged_at", ""))
        if logged_at and logged_at >= cutoff:
            recent[vid] = vdata

    logger.info(
        f"clustering: {len(recent)} submissions within last {window_hours}h window"
    )

    if not recent:
        return []

    # ── Step 4: greedy single-linkage clustering ──────────────────────────────
    assigned: set[str] = set()        # IDs already placed in a cluster
    clusters: list[dict] = []

    for seed_id, seed_data in recent.items():
        if seed_id in assigned:
            continue

        seed_values = seed_data.get("values")
        if not seed_values:
            continue

        # Query Pinecone for nearest neighbours of this seed
        try:
            nn_resp = index.query(
                vector=seed_values,
                top_k=_NEIGHBOUR_TOP_K,
                include_metadata=True,
                namespace=CAMPAIGN_NAMESPACE,
            )
            neighbours = nn_resp.get("matches", [])
        except Exception as e:
            logger.warning(f"clustering: neighbour query failed for {seed_id}: {e}")
            neighbours = []

        # Collect cluster members: seed + neighbours above threshold
        members: list[tuple[str, dict]] = []  # (id, metadata)

        for match in neighbours:
            mid   = match.get("id", "")
            score = match.get("score", 0.0)
            mmeta = match.get("metadata") or {}

            # Must be in recent window, above threshold, not yet assigned
            if mid not in recent:
                continue
            if score < similarity_threshold:
                continue
            if mid in assigned:
                continue

            members.append((mid, mmeta))
            assigned.add(mid)

        if not members:
            # seed itself didn't even make it in (can happen if values missing)
            assigned.add(seed_id)
            continue

        # Build cluster summary from member metadata
        seed_meta     = seed_data.get("metadata") or {}
        patterns      = [m[1].get("matched_pattern", "") for m in members]
        flag_csvs     = [m[1].get("red_flags_csv", "")  for m in members]
        previews      = [m[1].get("preview", "")        for m in members]
        timestamps    = [
            _parse_dt(m[1].get("logged_at", ""))
            for m in members
        ]
        valid_ts      = [t for t in timestamps if t is not None]

        first_seen    = min(valid_ts) if valid_ts else None
        last_seen     = max(valid_ts) if valid_ts else None
        window_span   = (
            round((last_seen - first_seen).total_seconds() / 3600, 1)
            if first_seen and last_seen else 0.0
        )

        clusters.append({
            "campaign_id":     _cluster_id(seed_id),
            "count":           len(members),
            "matched_pattern": _majority(patterns, fallback="Unknown pattern"),
            "top_red_flags":   _top_flags(flag_csvs),
            "preview":         next((p for p in previews if p), ""),
            "first_seen":      first_seen.isoformat() if first_seen else None,
            "last_seen":       last_seen.isoformat()  if last_seen  else None,
            "window_hours":    window_span,
        })

    # ── Step 5 & 6: filter small clusters, sort by size, return top_n ─────────
    trending = [c for c in clusters if c["count"] >= min_cluster_size]
    trending.sort(key=lambda c: c["count"], reverse=True)

    logger.info(
        f"clustering: found {len(trending)} active campaign(s) "
        f"(min_size={min_cluster_size}, threshold={similarity_threshold})"
    )
    return trending[:top_n]