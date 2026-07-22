"""
test_clustering.py
------------------
End-to-end test for intelligence/clustering.py :: get_trending_campaigns().

Strategy
--------
1. Seed 4 slightly-varied "fake customs officer" transcripts into Pinecone
   via log_submission() (same pipeline the real app uses).
2. Wait for Pinecone to make the vectors available.
3. Call get_trending_campaigns() and assert:
   - At least one cluster is returned
   - The top cluster has count >= 2
   - Required fields are present in each cluster dict
4. Print the full cluster output so we can visually verify the data.
"""

import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from intelligence.campaign_log import log_submission
from intelligence.clustering import get_trending_campaigns

# ── Fixtures: 4 phrasing variants of the same customs-officer scam ───────────

CUSTOMS_VARIANTS = [
    (
        "Hello, I am calling from Customs department. We have seized a parcel "
        "registered in your name containing illegal documents. You must pay a "
        "clearance fee of Rs 12,000 via UPI immediately or face arrest.",
        {"verdict": "SCAM", "confidence": 92, "matched_pattern": "Fake customs officer / parcel scam",
         "red_flags": ["urgency", "payment_demand", "impersonation"]},
    ),
    (
        "This is Indian Customs authority. Your package has been held at the "
        "airport. It contains suspicious items. Pay Rs 8,500 to release it now "
        "otherwise a case will be filed against you today.",
        {"verdict": "SCAM", "confidence": 90, "matched_pattern": "Fake customs officer / parcel scam",
         "red_flags": ["urgency", "payment_demand", "impersonation", "threat_of_arrest"]},
    ),
    (
        "Sir I am from customs office. A parcel in your name has been stopped "
        "at Delhi airport. There are illegal items inside. You must transfer "
        "Rs 15,000 immediately to avoid getting arrested. Don't tell anyone.",
        {"verdict": "SCAM", "confidence": 95, "matched_pattern": "Fake customs officer / parcel scam",
         "red_flags": ["urgency", "payment_demand", "secrecy", "impersonation"]},
    ),
    (
        "Customs department calling. We caught a package with your Aadhar on it "
        "at the port. Drugs were found inside. Pay Rs 20,000 via Google Pay "
        "in the next 30 minutes or we will send police to your home.",
        {"verdict": "SCAM", "confidence": 97, "matched_pattern": "Fake customs officer / parcel scam",
         "red_flags": ["urgency", "payment_demand", "threat_of_arrest", "impersonation"]},
    ),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def section(title: str):
    print(f"\n{'='*58}")
    print(f"  {title}")
    print(f"{'='*58}")

def ok(msg):   print(f"  OK    {msg}")
def fail(msg): print(f"  FAIL  {msg}")
def info(msg): print(f"  INFO  {msg}")

# ── Tests ─────────────────────────────────────────────────────────────────────

async def seed_submissions():
    section("SEED -- pushing 4 customs-scam variants into Pinecone")
    successes = 0
    for i, (text, verdict) in enumerate(CUSTOMS_VARIANTS, 1):
        result = await log_submission(text, verdict)
        if result:
            ok(f"Variant {i} logged")
            successes += 1
        else:
            fail(f"Variant {i} failed to log")
    info(f"Seeded {successes}/{len(CUSTOMS_VARIANTS)} submissions")
    return successes == len(CUSTOMS_VARIANTS)


def test_get_trending_campaigns():
    section("TEST 1 -- get_trending_campaigns() returns clusters")
    clusters = get_trending_campaigns(
        window_hours=24,
        similarity_threshold=0.75,
        min_cluster_size=2,
        top_n=5,
    )

    info(f"Clusters returned: {len(clusters)}")

    if not clusters:
        fail("No clusters returned -- either namespace is empty or threshold too high")
        return False

    ok(f"{len(clusters)} cluster(s) found")
    return True


def test_cluster_count(clusters):
    section("TEST 2 -- top cluster has count >= 2")
    top = clusters[0]
    count = top.get("count", 0)
    info(f"Top cluster count: {count}")
    if count >= 2:
        ok(f"count={count} >= 2 -- campaign signal confirmed")
        return True
    else:
        fail(f"count={count} -- too small, may need more seed data")
        return False


def test_cluster_fields(clusters):
    section("TEST 3 -- required fields present in every cluster")
    required = {"campaign_id", "count", "matched_pattern", "top_red_flags",
                "preview", "first_seen", "last_seen", "window_hours"}
    all_ok = True
    for i, c in enumerate(clusters, 1):
        missing = required - set(c.keys())
        if missing:
            fail(f"Cluster {i} missing fields: {missing}")
            all_ok = False
        else:
            ok(f"Cluster {i} has all required fields")
    return all_ok


def print_clusters(clusters):
    section("CLUSTER OUTPUT (visual check)")
    for i, c in enumerate(clusters, 1):
        print(f"\n  --- Campaign #{i} ---")
        print(f"  ID:      {c['campaign_id']}")
        print(f"  Count:   {c['count']} submissions")
        print(f"  Pattern: {c['matched_pattern']}")
        print(f"  Flags:   {', '.join(c['top_red_flags'])}")
        print(f"  Window:  {c['first_seen']}  →  {c['last_seen']}  ({c['window_hours']}h)")
        print(f"  Preview: {c['preview'][:80]}...")


# ── Runner ────────────────────────────────────────────────────────────────────

async def main():
    print("\nScam Shield -- clustering.py test suite")

    # 1. Seed data
    seeded = await seed_submissions()

    # 2. Give Pinecone time to index
    info("Waiting 4s for Pinecone to index vectors ...")
    time.sleep(4)

    # 3. Run clustering
    clusters = get_trending_campaigns(
        window_hours=24,
        similarity_threshold=0.82,
        min_cluster_size=2,
        top_n=5,
    )

    # 4. Tests
    results = []
    results.append(bool(clusters))                         # T1: any clusters?
    if clusters:
        results.append(test_cluster_count(clusters))       # T2: count >= 2?
        results.append(test_cluster_fields(clusters))      # T3: fields OK?
        print_clusters(clusters)
    else:
        results += [False, False]

    section("SUMMARY")
    passed = sum(1 for r in results if r)
    total  = len(results)
    print(f"  {passed}/{total} tests passed")
    if passed == total:
        print("\n  All tests passed!\n")
    else:
        print("\n  Some tests failed -- review output above.\n")

if __name__ == "__main__":
    asyncio.run(main())
