"""
Pydantic models for resume data
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Skill(BaseModel):
    """Model for a skill"""
    name: str
    level: Optional[str] = None
    years: Optional[int] = None

class WorkExperience(BaseModel):
    """Model for work experience"""
    company: str = Field(..., description="Name of the company")
    position: str = Field(..., description="Job title or position")
    start_date: str = Field(..., description="Start date of employment (YYYY-MM format preferred)")
    end_date: Optional[str] = Field(default="Present", description="End date of employment or 'Present' if current")
    description: Optional[str] = Field(default=None, description="Description of responsibilities and achievements")
    skills: Optional[List[str]] = Field(default_factory=list, description="Skills utilized in this role")
    achievements: Optional[List[str]] = Field(default_factory=list, description="Key achievements in this role")

class Education(BaseModel):
    """Model for education"""
    institution: str = Field(..., description="Name of educational institution")
    degree: Optional[str] = Field(default=None, description="Degree earned (e.g., B.S., M.S., Ph.D.)")
    field_of_study: Optional[str] = Field(default=None, description="Field or major of study")
    start_date: Optional[str] = Field(default=None, description="Start date (year)")
    end_date: Optional[str] = Field(default=None, description="End date (year) or 'Present' if ongoing")
    gpa: Optional[float] = Field(default=None, description="Grade Point Average")
    achievements: Optional[List[str]] = Field(default_factory=list, description="Academic achievements and honors")

class Project(BaseModel):
    """Model for a project"""
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    technologies: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class Certification(BaseModel):
    """Model for a certification"""
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    expires: Optional[str] = None
    url: Optional[str] = None

class StructuredData(BaseModel):
    """Model for structured resume data"""
    name: Optional[str] = Field(default=None, description="Full name of the candidate")
    email: Optional[str] = Field(default=None, description="Contact email address")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    location: Optional[str] = Field(default=None, description="Location/address")
    summary: Optional[str] = Field(default=None, description="Professional summary")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="Work experience entries")
    education: List[Education] = Field(default_factory=list, description="Education entries")
    skills: List[Skill] = Field(default_factory=list, description="Skills")
    certifications: Optional[List[Certification]] = Field(default_factory=list, description="Professional certifications")
    projects: Optional[List[Project]] = Field(default_factory=list, description="Projects")
    languages: Optional[List[str]] = Field(default_factory=list, description="Languages spoken")
    websites: Optional[Dict[str, str]] = Field(default_factory=dict, description="Professional websites (e.g. LinkedIn, GitHub)")

class ResumeRequest(BaseModel):
    """Model for resume analysis request"""
    resume_text: str = Field(..., description="Raw resume text to analyze")

class ResumeQuestionRequest(BaseModel):
    """Model for resume question generation request"""
    resume_text: str = Field(..., description="Raw resume text")
    job_description: Optional[str] = Field(default=None, description="Job description to match against")
    num_questions: int = Field(default=5, ge=1, le=10, description="Number of questions to generate")
