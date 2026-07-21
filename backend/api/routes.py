from typing import Optional
from fastapi import APIRouter
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
