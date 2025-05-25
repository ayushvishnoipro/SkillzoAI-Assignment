from typing import Dict, Any, Tuple
from app.services.parser_utils import clean_resume_text, extract_contact_info, extract_sections
from app.utils.logger import app_logger

async def start_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Start node that initializes the graph execution and prepares data.
    
    Args:
        state: Current graph state including resume_text to analyze
        
    Returns:
        Updated state with cleaned text and initial extracted data
    """
    app_logger.info("Starting resume analysis graph execution")
    
    # Extract resume text from state
    resume_text = state.get("resume_text", "")
    
    if not resume_text:
        return {
            **state,
            "error": "No resume text provided",
            "status": "error"
        }
    
    # Clean and normalize the resume text
    cleaned_text = clean_resume_text(resume_text)
    
    # Extract basic contact information
    contact_info = extract_contact_info(cleaned_text)
    
    # Extract sections for further processing
    sections = extract_sections(cleaned_text)
    
    app_logger.info("Initial resume data prepared for processing")
    
    # Return updated state
    return {
        **state,
        "cleaned_text": cleaned_text,
        "contact_info": contact_info,
        "sections": sections,
        "status": "processing"
    }
