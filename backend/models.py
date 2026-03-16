from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnalysisResponse(BaseModel):
    executive_summary: List[str]
    key_risks: List[str]
    opportunities: List[str]
    strategic_recommendations: List[str]
    filename: str
    pdf_file_url: Optional[str] = None
    preview_url: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str

class NoteCreate(BaseModel):
    analysis_id: int
    selected_text: Optional[str] = ""
    note_text: str

class NoteResponse(BaseModel):
    id: int
    analysis_id: int
    selected_text: Optional[str] = ""
    note_text: str
    created_at: datetime

class QuestionRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    name: str
    password: str

class UserResponse(UserBase):
    id: int
    name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
