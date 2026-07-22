from typing import Optional
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str

class FollowupRequest(BaseModel):
    question: Optional[str] = None
    context: Optional[str] = None
    history: list = []
    session_id: Optional[str] = None

@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Citizen Fraud Shield API is running"}

@router.post("/analyze")
async def analyze_scam(request: AnalyzeRequest):
    """
    Main endpoint for classifying a scam from pasted text.
    """
    from detection.classifier import analyze_text
    
    result = await analyze_text(request.text)
    return result

@router.post("/followup")
async def followup(request: FollowupRequest):
    """
    Endpoint for follow-up chat questions.
    """
    from detection.classifier import handle_followup_stream
    
    return StreamingResponse(
        handle_followup_stream(
            request.question or "", 
            request.context or "", 
            request.history
        ),
        media_type="text/event-stream"
    )

@router.get("/trending")
async def trending_campaigns(
    window_hours: float = Query(default=24.0, ge=1.0, le=168.0,
                                description="Look-back window in hours (1–168)"),
    min_cluster_size: int  = Query(default=2, ge=2, le=20,
                                   description="Minimum submissions to count as a campaign"),
):
    """
    Returns active emerging scam campaigns detected by cross-user similarity
    clustering of recent submissions in the campaign_submissions namespace.
    """
    from intelligence.clustering import get_trending_campaigns

    # get_trending_campaigns is synchronous (Pinecone SDK is sync);
    # run it in the thread pool so we don't block the event loop.
    from fastapi.concurrency import run_in_threadpool
    campaigns = await run_in_threadpool(
        get_trending_campaigns,
        window_hours=window_hours,
        min_cluster_size=min_cluster_size,
    )
    return {"campaigns": campaigns, "total": len(campaigns)}
