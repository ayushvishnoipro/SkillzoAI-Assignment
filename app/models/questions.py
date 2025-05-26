"""
Pydantic models for interview questions
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class InterviewQuestion(BaseModel):
    """Model for an interview question"""
    question: str = Field(..., description="The interview question text")
    difficulty: str = Field(default="Medium", description="Difficulty level (Easy, Medium, Hard)")
    category: str = Field(default="General", description="Question category (e.g., Technical, Behavioral)")
    intent: Optional[str] = Field(default=None, description="Intent or purpose of asking this question")

class QuestionSet(BaseModel):
    """Model for a set of interview questions"""
    questions: List[InterviewQuestion] = Field(..., description="List of interview questions")
    overview: Optional[str] = Field(default=None, description="Overview of the question set")
