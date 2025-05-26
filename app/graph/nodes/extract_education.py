"""
Node for extracting education information from resume text
"""
from typing import Dict, Any, List
import asyncio
from app.services.llm_service import call_llm
from app.services.parser import extract_json_from_llm_response
from app.utils.logger import app_logger

async def extract_education(resume_text: str, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract education details from resume text
    
    Args:
        resume_text: The raw resume text
        structured_data: The already extracted structured data
        
    Returns:
        List[Dict[str, Any]]: List of education entries
    """
    prompt = f"""
    Extract detailed education information from the following resume text.
    For each education entry, extract:
    - Institution name
    - Degree (e.g., B.S., M.S., Ph.D.)
    - Field of study
    - Start date (year)
    - End date (year or "Present" if ongoing)
    - GPA (if available)
    - Achievements or honors (if any)
    
    Format as a JSON array of objects.
    
    RESUME TEXT:
    {resume_text}
    """
    
    try:
        response = await call_llm(prompt)
        education_data = extract_json_from_llm_response(response)
        
        # Ensure we have a list
        if not isinstance(education_data, list):
            if isinstance(education_data, dict) and "education" in education_data:
                education_data = education_data["education"]
            else:
                app_logger.warning("Education extraction didn't return a list or proper dict")
                return []
        
        app_logger.info(f"Extracted {len(education_data)} education entries")
        return education_data
        
    except Exception as e:
        app_logger.error(f"Error extracting education: {e}")
        return structured_data.get("education", [])  # Return existing data if available
