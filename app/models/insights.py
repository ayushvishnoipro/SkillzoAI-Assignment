"""
Pydantic models for resume insights
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Insights(BaseModel):
    """Model for resume insights"""
    strengths: List[str] = Field(
        default_factory=list, 
        description="Professional strengths identified in the resume"
    )
    improvement_areas: List[str] = Field(
        default_factory=list, 
        description="Areas where the candidate could improve or develop"
    )
    key_skills: List[str] = Field(
        default_factory=list, 
        description="Key skills extracted from the resume"
    )
    experience_summary: Optional[str] = Field(
        default=None, 
        description="Short summary of the candidate's experience"
    )
    career_level: Optional[str] = Field(
        default=None, 
        description="Assessment of career level (Junior, Mid, Senior, etc.)"
    )
    industry_fit: List[str] = Field(
        default_factory=list, 
        description="Industries that would be a good fit for this candidate"
    )
