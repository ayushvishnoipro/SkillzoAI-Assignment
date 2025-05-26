"""
Start node for LangGraph workflows
"""
from typing import Dict, Any, Tuple
from app.services.parser_utils import clean_resume_text, extract_contact_info, extract_sections
from app.services.checkpoint_utils import save_checkpoint
from app.utils.logger import app_logger
import asyncio

async def start_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize the workflow and set up initial state
    
    Args:
        state: The current state with input parameters
        
    Returns:
        Dict[str, Any]: Updated state
    """
    app_logger.info("Starting resume analysis graph execution")
    
    # Create a new state dict
    new_state = state.copy()
    
    # Extract resume text from state
    resume_text = new_state.get("resume_text", "")
    
    if not resume_text:
        return {
            **new_state,
            "error": "No resume text provided",
            "status": "error"
        }
    
    # Clean and normalize the resume text
    cleaned_text = clean_resume_text(resume_text)
    
    # Extract basic contact information
    contact_info = extract_contact_info(cleaned_text)
    
    # Extract sections for further processing
    sections = extract_sections(cleaned_text)
    
    # Set status to processing
    new_state["status"] = "processing"
    
    # Clear any previous errors
    if "error" in new_state:
        del new_state["error"]
    
    # Save checkpoint if tracking_id is available
    if "tracking_id" in new_state:
        await save_checkpoint(new_state["tracking_id"], new_state)
    
    app_logger.info("Initial resume data prepared for processing")
    
    # Return updated state
    return {
        **new_state,
        "cleaned_text": cleaned_text,
        "contact_info": contact_info,
        "sections": sections
    }
