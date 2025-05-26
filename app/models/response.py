"""
Pydantic models for API responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.insights import Insights
from app.models.questions import InterviewQuestion

class ResumeAnalysisResponse(BaseModel):
    """Response model for resume analysis"""
    structured_data: Dict[str, Any] = Field(..., description="Structured data extracted from the resume")
    insights: Dict[str, Any] = Field(..., description="Professional insights about the candidate")

class ResumeQuestionResponse(BaseModel):
    """Response model for interview question generation"""
    questions: List[Dict[str, Any]] = Field(..., description="List of generated interview questions")
    overview: Optional[str] = Field(default=None, description="Overview of the generated questions")
