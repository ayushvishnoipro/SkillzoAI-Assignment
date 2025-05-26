"""
Node for extracting structured data from resume text
"""
from typing import Dict, Any, Optional
import asyncio
from app.services.llm_service import call_llm
from app.services.parser import extract_json_from_llm_response
from app.utils.logger import app_logger

async def extract_structured_data(resume_text: str) -> Dict[str, Any]:
    """
    Extract basic structured data from resume text including contact info
    
    Args:
        resume_text: The raw resume text
        
    Returns:
        Dict[str, Any]: Structured data extracted from the resume
    """
    prompt = f"""
    Extract structured information from the following resume text.
    Include:
    - Name
    - Email
    - Phone number
    - Location
    - Empty arrays for work_experience, education, and skills (will be filled in later steps)
    
    Format as a JSON object.
    
    RESUME TEXT:
    {resume_text}
    """
    
    try:
        response = await call_llm(prompt)
        structured_data = extract_json_from_llm_response(response)
        
        # Ensure the basic structure exists
        if not isinstance(structured_data, dict):
            app_logger.warning("Structured data extraction didn't return a dictionary")
            structured_data = {}
        
        # Ensure required fields exist
        for field in ["work_experience", "education", "skills"]:
            if field not in structured_data:
                structured_data[field] = []
        
        app_logger.info("Extracted basic structured data")
        return structured_data
        
    except Exception as e:
        app_logger.error(f"Error extracting structured data: {e}")
        # Return a minimal valid structure
        return {
            "name": None,
            "email": None,
            "phone": None,
            "location": None,
            "work_experience": [],
            "education": [],
            "skills": []
        }
