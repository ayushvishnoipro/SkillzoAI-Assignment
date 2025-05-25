from typing import Dict, Any, List
from app.services.llm_utils import create_structured_output_chain, get_llm
from app.models.resume import WorkExperience
from app.utils.logger import app_logger
from pydantic import BaseModel

WORK_EXPERIENCE_PROMPT = """
You are a professional resume parser specialized in extracting structured work experience data.

Given the following resume text, extract all work experiences with as much detail as possible.
For each position, extract:
1. Company name
2. Job title/position
3. Start and end dates (use 'Present' if current)
4. Job description/responsibilities
5. Key skills demonstrated
6. Notable achievements (with metrics if available)

Resume text to analyze:
{input}

Analyze the text carefully and identify each separate work experience. Be comprehensive and accurate.
"""

# Updated to use a proper Pydantic model
class WorkExperienceList(BaseModel):
    """List of work experience entries"""
    entries: List[WorkExperience] = []

async def extract_work_experience(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract work experience from resume text
    
    Args:
        state: Current graph state including resume text
        
    Returns:
        Updated state with extracted work experience list
    """
    app_logger.info("Extracting work experience")
    
    # Get cleaned text and relevant sections
    cleaned_text = state.get("cleaned_text", "")
    sections = state.get("sections", {})
    
    # Focus on experience section if available, otherwise use full text
    text_to_analyze = sections.get("experience", cleaned_text)
    
    try:
        # Get LLM with appropriate temperature
        llm = get_llm(temperature=0.2)  # Low temperature for factual extraction
        
        # Create chain to extract structured work experience
        work_exp_chain = create_structured_output_chain(
            WORK_EXPERIENCE_PROMPT,
            WorkExperienceList,
            llm=llm
        )
        
        # Run the chain to get structured output
        result = await work_exp_chain.ainvoke(text_to_analyze)
        
        # Access the entries field
        work_experience_entries = result.entries if hasattr(result, "entries") else []
        
        app_logger.info(f"Extracted {len(work_experience_entries)} work experiences")
        
        # Update the state with extracted work experience
        return {
            **state,
            "work_experience": work_experience_entries,
            "status": "work_experience_extracted"
        }
        
    except Exception as e:
        app_logger.error(f"Error extracting work experience: {e}")
        return {
            **state,
            "error": f"Failed to extract work experience: {str(e)}",
            "status": "error"
        }
