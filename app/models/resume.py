from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class WorkExperience(BaseModel):
    """Work experience model"""
    company: str
    position: str
    start_date: str
    end_date: Optional[str] = "Present"  # Default to Present if current job
    description: str
    skills: List[str] = []
    achievements: List[str] = []
    
class Education(BaseModel):
    """Education model"""
    institution: str
    degree: str
    field_of_study: str
    start_date: str
    end_date: Optional[str] = None
    gpa: Optional[float] = None
    achievements: List[str] = []

class ResumeData(BaseModel):
    """Structured resume data model"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    work_experience: List[WorkExperience] = []
    education: List[Education] = []
    skills: List[str] = []
    certifications: List[str] = []
    languages: List[str] = []
    projects: List[Dict[str, Any]] = []

class ResumeRequest(BaseModel):
    """Resume analysis request model"""
    resume_text: str = Field(..., description="Raw resume text to analyze")
    
class ResumeQuestionRequest(BaseModel):
    """Resume question generation request model"""
    resume_text: str = Field(..., description="Raw resume text")
    job_description: Optional[str] = Field(None, description="Optional job description to tailor questions")
    num_questions: int = Field(5, description="Number of questions to generate")
