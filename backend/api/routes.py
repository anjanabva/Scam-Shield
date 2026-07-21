from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str

class FollowupRequest(BaseModel):
    session_id: str
    message: str

@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "Citizen Fraud Shield API is running"}

@router.post("/analyze")
async def analyze_scam(request: AnalyzeRequest):
    """
    Main endpoint for classifying a scam from pasted text.
    Currently a placeholder until the detection engine is built.
    """
    return {
        "verdict": "UNKNOWN",
        "confidence": 0,
        "red_flags": [],
        "matched_pattern": None,
        "explanation": "Endpoint under construction. Detection engine not yet integrated."
    }

@router.post("/followup")
async def followup(request: FollowupRequest):
    """
    Endpoint for follow-up chat questions (e.g., 'What do I do now?').
    Currently a placeholder.
    """
    return {
        "reply": "Endpoint under construction."
    }
