"""
Service for parsing LLM outputs into structured Pydantic models
"""
import json
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, ValidationError
import re

from app.models.resume import StructuredData, WorkExperience, Education, Skill
from app.models.insights import Insights
from app.models.questions import InterviewQuestion
from app.utils.logger import app_logger


class ParsingError(Exception):
    """Exception raised for errors during parsing"""
    pass


def extract_json_from_llm_response(text: str) -> Dict[str, Any]:
    """
    Extract JSON content from LLM response which might contain markdown or other text
    """
    # Look for JSON content within markdown code blocks
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(json_pattern, text)
    
    if match:
        json_str = match.group(1)
    else:
        # If no code blocks found, try to find anything that looks like a JSON object
        json_pattern = r'(\{[\s\S]*\})'
        match = re.search(json_pattern, text)
        if match:
            json_str = match.group(1)
        else:
            # Return the original text as a last resort
            json_str = text
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        app_logger.error(f"Failed to parse JSON from LLM response: {e}")
        app_logger.debug(f"Problematic text: {json_str[:200]}...")
        raise ParsingError(f"Failed to parse JSON from LLM response: {e}")


def parse_structured_data(data: Dict[str, Any]) -> StructuredData:
    """
    Parse and validate structured resume data using Pydantic models
    """
    try:
        # Handle work experience
        work_experience = []
        if "work_experience" in data and isinstance(data["work_experience"], list):
            for item in data["work_experience"]:
                work_experience.append(WorkExperience(**item))
        
        # Handle education
        education = []
        if "education" in data and isinstance(data["education"], list):
            for item in data["education"]:
                education.append(Education(**item))
        
        # Create the structured data model
        structured_data = StructuredData(
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            location=data.get("location"),
            summary=data.get("summary"),
            work_experience=work_experience,
            education=education,
            skills=[Skill(name=skill) for skill in data.get("skills", [])] if isinstance(data.get("skills"), list) else []
        )
        
        app_logger.debug("Successfully parsed structured data into Pydantic model")
        return structured_data
        
    except ValidationError as e:
        app_logger.error(f"Validation error while parsing structured data: {e}")
        raise ParsingError(f"Failed to validate structured data: {e}")
    except Exception as e:
        app_logger.error(f"Error parsing structured data: {e}")
        raise ParsingError(f"Error parsing structured data: {e}")


def parse_insights(data: Dict[str, Any]) -> Insights:
    """
    Parse and validate resume insights using Pydantic models
    """
    try:
        insights = Insights(
            strengths=data.get("strengths", []),
            improvement_areas=data.get("improvement_areas", []),
            key_skills=data.get("key_skills", []),
            experience_summary=data.get("experience_summary", ""),
            career_level=data.get("career_level", ""),
            industry_fit=data.get("industry_fit", [])
        )
        
        app_logger.debug("Successfully parsed insights into Pydantic model")
        return insights
        
    except ValidationError as e:
        app_logger.error(f"Validation error while parsing insights: {e}")
        raise ParsingError(f"Failed to validate insights: {e}")
    except Exception as e:
        app_logger.error(f"Error parsing insights: {e}")
        raise ParsingError(f"Error parsing insights: {e}")


def parse_interview_questions(data: Dict[str, Any]) -> List[InterviewQuestion]:
    """
    Parse and validate interview questions using Pydantic models
    """
    try:
        questions = []
        
        if "questions" in data and isinstance(data["questions"], list):
            for item in data["questions"]:
                questions.append(InterviewQuestion(
                    question=item.get("question", ""),
                    difficulty=item.get("difficulty", "Medium"),
                    category=item.get("category", "General"),
                    intent=item.get("intent", "")
                ))
        
        app_logger.debug(f"Successfully parsed {len(questions)} interview questions into Pydantic models")
        return questions
        
    except ValidationError as e:
        app_logger.error(f"Validation error while parsing questions: {e}")
        raise ParsingError(f"Failed to validate questions: {e}")
    except Exception as e:
        app_logger.error(f"Error parsing questions: {e}")
        raise ParsingError(f"Error parsing questions: {e}")
