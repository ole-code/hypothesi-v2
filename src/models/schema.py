from pydantic import BaseModel
from typing import Optional, List, Any

class ReviewRequest(BaseModel):
    source: str
    source_type: Optional[str] = None
    use_llm: bool = False
    llm_model: str = "gemini-1.5-flash"

class ReviewResponse(BaseModel):
    executive_summary: Optional[str]
    reliability_score: Optional[int]
    structured_data: Optional[dict]
    claims: Optional[List[str]]
    evidence: Optional[List[dict]]
    recommendation: Optional[str]