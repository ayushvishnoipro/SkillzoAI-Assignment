"""
Node for generating professional insights from resume data
"""
from typing import Dict, Any, List, Optional
import asyncio
from app.services.llm_service import call_llm
from app.services.parser import extract_json_from_llm_response
from app.utils.logger import app_logger

async def generate_insights(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate professional insights based on the structured resume data
    
    Args:
        structured_data: The structured resume data
        
    Returns:
        Dict[str, Any]: Insights including strengths, improvement areas, key skills, etc.
    """
    # Prepare a condensed version of the structured data for the prompt
    work_experience = "\n".join([
        f"- {exp.get('position')} at {exp.get('company')} ({exp.get('start_date')} to {exp.get('end_date')}): {exp.get('description', 'No description')}"
        for exp in structured_data.get("work_experience", [])
    ])
    
    education = "\n".join([
        f"- {edu.get('degree')} in {edu.get('field_of_study')} from {edu.get('institution')} ({edu.get('start_date')} to {edu.get('end_date')})"
        for edu in structured_data.get("education", [])
    ])
    
    # Create the prompt
    prompt = f"""
    Analyze the following resume information and provide professional insights. 
    Include:
    1. A list of professional strengths (4-5 items)
    2. Areas for improvement (1-2 items)
    3. Key skills (both explicit and implicit from experience)
    4. A brief experience summary (one sentence)
    5. Career level assessment (Junior, Mid, Senior, Executive)
    6. Industry fit (3-4 relevant industries)
    
    Format the response as a JSON object with the following keys:
    - strengths (array of strings)
    - improvement_areas (array of strings)
    - key_skills (array of strings)
    - experience_summary (string)
    - career_level (string)
    - industry_fit (array of strings)
    
    RESUME INFORMATION:
    Work Experience:
    {work_experience}
    
    Education:
    {education}
    
    Summary: {structured_data.get("summary", "Not provided")}
    """
    
    try:
        response = await call_llm(prompt)
        insights = extract_json_from_llm_response(response)
        app_logger.info("Generated professional insights")
        return insights
        
    except Exception as e:
        app_logger.error(f"Error generating insights: {e}")
        # Return a minimal valid structure
        return {
            "strengths": [],
            "improvement_areas": [],
            "key_skills": [],
            "experience_summary": "Could not generate experience summary.",
            "career_level": "Unknown",
            "industry_fit": []
        }
