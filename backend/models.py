from pydantic import BaseModel
from typing import List, Optional

class AnalysisResponse(BaseModel):
    executive_summary: List[str]
    key_risks: List[str]
    opportunities: List[str]
    strategic_recommendations: List[str]
    filename: str

class ErrorResponse(BaseModel):
    detail: str
