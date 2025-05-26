"""
Node for extracting work experience from resume text
"""
from typing import Dict, Any, List
import asyncio
from app.services.llm_service import call_llm
from app.services.parser import extract_json_from_llm_response
from app.utils.logger import app_logger

async def extract_work_experience(resume_text: str, structured_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract work experience details from resume text
    
    Args:
        resume_text: The raw resume text
        structured_data: The already extracted structured data
        
    Returns:
        List[Dict[str, Any]]: List of work experience entries
    """
    prompt = f"""
    Extract detailed work experience information from the following resume text.
    For each work experience entry, extract:
    - Company name
    - Position/title
    - Start date (formatted as YYYY-MM if available)
    - End date (formatted as YYYY-MM or "Present" if current)
    - Description
    - Skills used (extracted from descriptions)
    - Achievements (if any)
    
    Format as a JSON array of objects.
    
    RESUME TEXT:
    {resume_text}
    """
    
    try:
        response = await call_llm(prompt)
        work_data = extract_json_from_llm_response(response)
        
        # Ensure we have a list
        if not isinstance(work_data, list):
            if isinstance(work_data, dict) and "work_experience" in work_data:
                work_data = work_data["work_experience"]
            else:
                app_logger.warning("Work experience extraction didn't return a list or proper dict")
                return []
        
        app_logger.info(f"Extracted {len(work_data)} work experience entries")
        return work_data
        
    except Exception as e:
        app_logger.error(f"Error extracting work experience: {e}")
        return structured_data.get("work_experience", [])  # Return existing data if available
