from pydantic import BaseModel
from typing import List, Optional

class AnalysisResponse(BaseModel):
    executive_summary: List[str]
    key_risks: List[str]
    opportunities: List[str]
    strategic_recommendations: List[str]
    filename: str
    pdf_file_url: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str
