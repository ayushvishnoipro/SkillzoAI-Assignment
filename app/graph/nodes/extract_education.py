from typing import Dict, Any, List
from app.services.llm_utils import create_structured_output_chain, get_llm
from app.models.resume import Education
from app.utils.logger import app_logger
from pydantic import BaseModel

EDUCATION_PROMPT = """
You are an AI assistant that specializes in extracting education information from resumes.

Given the following resume text, extract all education entries with as much detail as possible.
For each education entry, extract:
1. Institution name
2. Degree (e.g., Bachelor's, Master's, Ph.D.)
3. Field of study
4. Start and end dates
5. GPA (if available)
6. Academic achievements or honors

Resume text to analyze:
{input}

Analyze the text carefully and identify each separate education entry. Be comprehensive and accurate.
"""

# Updated to use a proper Pydantic model
class EducationList(BaseModel):
    """List of education entries"""
    entries: List[Education] = []

async def extract_education(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract education information from resume text
    
    Args:
        state: Current graph state including resume text
        
    Returns:
        Updated state with extracted education list
    """
    app_logger.info("Extracting education information")
    
    # Get cleaned text and relevant sections
    cleaned_text = state.get("cleaned_text", "")
    sections = state.get("sections", {})
    
    # Focus on education section if available, otherwise use full text
    text_to_analyze = sections.get("education", cleaned_text)
    
    try:
        # Get LLM with appropriate temperature
        llm = get_llm(temperature=0.2)  # Low temperature for factual extraction
        
        # Create chain to extract structured education data
        education_chain = create_structured_output_chain(
            EDUCATION_PROMPT,
            EducationList,
            llm=llm
        )
        
        # Run the chain to get structured output
        result = await education_chain.ainvoke(text_to_analyze)
        
        # Access the entries field
        education_entries = result.entries if hasattr(result, "entries") else []
        
        app_logger.info(f"Extracted {len(education_entries)} education entries")
        
        # Update the state with extracted education data
        return {
            **state,
            "education": education_entries,
            "status": "education_extracted"
        }
        
    except Exception as e:
        app_logger.error(f"Error extracting education information: {e}")
        return {
            **state,
            "error": f"Failed to extract education: {str(e)}",
            "status": "error"
        }
