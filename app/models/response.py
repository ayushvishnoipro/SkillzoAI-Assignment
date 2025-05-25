from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from .resume import ResumeData

class InsightItem(BaseModel):
    """Individual insight about a resume"""
    category: str = Field(..., description="Category of the insight (e.g., 'Skills', 'Experience')")
    insight: str = Field(..., description="The actual insight text")
    confidence: float = Field(..., description="Confidence score (0-1)")

class ResumeInsights(BaseModel):
    """Collection of insights about a resume"""
    strengths: List[str] = []
    improvement_areas: List[str] = []
    key_skills: List[str] = []
    experience_summary: str = ""
    career_level: str = ""
    industry_fit: List[str] = []
    
class InterviewQuestion(BaseModel):
    """Interview question model"""
    question: str
    difficulty: str = Field(..., description="Easy, Medium, Hard")
    category: str = Field(..., description="Technical, Behavioral, Experience, etc.")
    intent: str = Field(..., description="What the interviewer is trying to assess")
    
class ResumeAnalysisResponse(BaseModel):
    """Full resume analysis response"""
    structured_data: ResumeData
    insights: ResumeInsights
    
class ResumeQuestionResponse(BaseModel):
    """Interview questions response"""
    questions: List[InterviewQuestion]
    overview: str = Field("", description="Overview of question strategy")
