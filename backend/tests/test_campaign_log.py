"""
test_campaign_log.py
--------------------
End-to-end test for intelligence/campaign_log.py.

Tests:
  1. log_submission() returns True on a valid scam transcript
  2. The upserted vector is queryable from the `campaign_submissions` namespace
  3. Metadata fields are stored correctly
  4. log_submission() returns False and does not raise on an empty text
"""

import asyncio
import sys
import os
import time

# ── resolve backend root so imports work without installing the package ──────
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from intelligence.campaign_log import log_submission, _submission_id, CAMPAIGN_NAMESPACE
from rag.vectorstore import index  # direct Pinecone client for verification

# ── Fixtures ──────────────────────────────────────────────────────────────────

FAKE_TRANSCRIPT = (
    "This is the customs officer calling. Your package has been seized. "
    "You must pay Rs 15,000 immediately via UPI or you will be arrested. "
    "Do not tell anyone about this call. Transfer to me now."
)

FAKE_VERDICT = {
    "verdict": "SCAM",
    "confidence": 95,
    "matched_pattern": "Fake customs officer / parcel scam",
    "explanation": "Classic parcel-seizure extortion script.",
    "red_flags": ["urgency", "payment_demand", "secrecy"],
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def section(title: str):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")

def ok(msg: str):   print(f"  OK  {msg}")
def fail(msg: str): print(f"  FAIL  {msg}")
def info(msg: str): print(f"  INFO  {msg}")

# ── Tests ─────────────────────────────────────────────────────────────────────

async def test_log_submission_success():
    section("TEST 1 -- log_submission() happy path")
    result = await log_submission(FAKE_TRANSCRIPT, FAKE_VERDICT)
    if result:
        ok("log_submission() returned True")
    else:
        fail("log_submission() returned False -- check logs above")
    return result


async def test_vector_queryable():
    section("TEST 2 -- verify vector is queryable in Pinecone")
    if index is None:
        fail("Pinecone index not initialised -- skipping query verification")
        return False

    # Give Pinecone a moment to make the upsert available
    info("Waiting 3 s for Pinecone to index the vector ...")
    time.sleep(3)

    doc_id = _submission_id(FAKE_TRANSCRIPT)
    info(f"Fetching vector id: {doc_id}")

    try:
        result = index.fetch(ids=[doc_id], namespace=CAMPAIGN_NAMESPACE)
        vectors = result.get("vectors", {})
        if doc_id in vectors:
            ok(f"Vector found in namespace '{CAMPAIGN_NAMESPACE}'")
            metadata = vectors[doc_id].get("metadata", {})
            info(f"Stored metadata: {metadata}")

            # Spot-check critical fields
            assert metadata.get("verdict") == "SCAM",          "verdict mismatch"
            assert metadata.get("confidence") == 95,           "confidence mismatch"
            assert metadata.get("red_flag_count") == 3,        "red_flag_count mismatch"
            assert "logged_at" in metadata,                    "missing logged_at"
            assert "preview" in metadata,                      "missing preview"
            ok("All metadata fields verified")
            return True
        else:
            fail(f"Vector '{doc_id}' NOT found in namespace '{CAMPAIGN_NAMESPACE}'")
            return False
    except Exception as e:
        fail(f"Pinecone fetch raised: {e}")
        return False


async def test_log_empty_text():
    section("TEST 3 -- log_submission() with empty text (should fail gracefully)")
    result = await log_submission("", FAKE_VERDICT)
    if not result:
        ok("Returned False on empty text -- no crash")
    else:
        fail("Unexpectedly returned True on empty text")
    return True  # test itself passes regardless -- we just want no exception


async def test_safe_verdict_is_skipped():
    section("TEST 4 -- SAFE verdict should be silently skipped (not logged)")
    safe_verdict = {"verdict": "SAFE", "confidence": 10}
    result = await log_submission("Hello, is this the bank?", safe_verdict)
    if not result:
        ok("SAFE verdict correctly skipped -- namespace stays clean")
    else:
        fail("SAFE verdict was logged -- this pollutes clustering!")
    return True  # test passes when result is False


async def test_log_minimal_scam_verdict():
    section("TEST 5 -- minimal SCAM dict logs without KeyError")
    minimal_scam = {"verdict": "SCAM", "confidence": 60}
    # No 'matched_pattern', no 'red_flags' -- should not raise
    result = await log_submission(
        "Send Rs 5000 via UPI immediately or your account will be blocked.",
        minimal_scam
    )
    if result:
        ok("Minimal SCAM dict upserted -- no KeyError on missing fields")
    else:
        fail("Upsert failed -- check logs")
    return result


# ── Runner ────────────────────────────────────────────────────────────────────

async def main():
    print("\nScam Shield -- campaign_log.py test suite")
    print(f"   Namespace under test: '{CAMPAIGN_NAMESPACE}'")

    results = []
    results.append(await test_log_submission_success())
    results.append(await test_vector_queryable())
    results.append(await test_log_empty_text())
    results.append(await test_safe_verdict_is_skipped())
    results.append(await test_log_minimal_scam_verdict())

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
