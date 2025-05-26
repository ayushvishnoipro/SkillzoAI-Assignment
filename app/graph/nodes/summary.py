"""
Node for generating a professional summary from resume data
"""
from typing import Dict, Any, Optional, List, AsyncGenerator
import asyncio
from app.services.llm_service import call_llm, stream_llm_response
from app.utils.logger import app_logger

async def generate_summary(structured_data: Dict[str, Any]) -> str:
    """
    Generate a professional summary based on the structured resume data
    
    Args:
        structured_data: The structured resume data
        
    Returns:
        str: Professional summary paragraph
    """
    # Check if streaming is enabled in the state
    streaming_enabled = structured_data.get("streaming_enabled", False)
    
    # Extract relevant information for the summary
    name = structured_data.get("name", "The candidate")
    
    # Create a compact representation of work experience
    work_exp = []
    for exp in structured_data.get("work_experience", []):
        work_exp.append(f"{exp.get('position', 'role')} at {exp.get('company', 'a company')}")
    
    # Create a compact representation of education
    education = []
    for edu in structured_data.get("education", []):
        education.append(f"{edu.get('degree', '')} in {edu.get('field_of_study', 'a field')} from {edu.get('institution', 'an institution')}")
    
    # Create the prompt
    prompt = f"""
    Create a concise professional summary paragraph for a resume based on the following information:
    
    Name: {name}
    Work Experience: {', '.join(work_exp) if work_exp else 'Not provided'}
    Education: {', '.join(education) if education else 'Not provided'}
    
    The summary should be a single paragraph highlighting key qualifications and experience.
    Write in third-person perspective.
    """
    
    try:
        # Use streaming version if requested
        if streaming_enabled:
            app_logger.info("Using streaming summary generation")
            # Get full response as final result for the state
            response = await call_llm(prompt)
        else:
            # Use standard non-streaming call
            response = await call_llm(prompt)
            
        # Clean up the response - remove quotes if present and trim
        summary = response.strip()
        if summary.startswith('"') and summary.endswith('"'):
            summary = summary[1:-1]
            
        app_logger.info("Generated professional summary")
        return summary
        
    except Exception as e:
        app_logger.error(f"Error generating summary: {e}")
        return "Professional summary not available."
