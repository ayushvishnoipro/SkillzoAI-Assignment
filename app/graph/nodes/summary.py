from typing import Dict, Any, List
from app.services.llm_utils import get_llm
from app.utils.logger import app_logger
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

SUMMARY_PROMPT = """
You are an expert resume analyst and professional summarizer.

Based on the following resume information, create a concise, professional summary of the candidate's 
background, skills, and qualifications in the third person. The summary should be about 3-4 sentences 
and highlight the most impressive and relevant aspects of their background.

Work Experience:
{work_experience}

Education:
{education}

Additional resume information:
{resume_text}

Write a concise, professional summary that captures the essence of this candidate's background:
"""

async def generate_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a professional summary based on extracted resume data
    
    Args:
        state: Current graph state including extracted work and education
        
    Returns:
        Updated state with professional summary
    """
    app_logger.info("Generating resume summary")
    
    # Extract necessary information from state
    work_experience = state.get("work_experience", [])
    education = state.get("education", [])
    cleaned_text = state.get("cleaned_text", "")
    
    # Format work experience for the prompt
    work_exp_text = "\n\n".join([
        f"{item.position} at {item.company}, {item.start_date} - {item.end_date}" 
        for item in work_experience
    ]) if work_experience else "No work experience provided"
    
    # Format education for the prompt
    education_text = "\n\n".join([
        f"{item.degree} in {item.field_of_study} from {item.institution}, {item.start_date} - {item.end_date or 'Present'}" 
        for item in education
    ]) if education else "No education provided"
    
    try:
        # Create LLM chain for summary generation
        llm = get_llm(temperature=0.5)  # Use higher temperature for creative summary
        
        prompt = PromptTemplate(
            template=SUMMARY_PROMPT,
            input_variables=["work_experience", "education", "resume_text"]
        )
        
        chain = prompt | llm | StrOutputParser()
        
        # Generate summary
        summary = await chain.ainvoke({
            "work_experience": work_exp_text,
            "education": education_text,
            "resume_text": cleaned_text
        })
        
        app_logger.info("Resume summary generated successfully")
        
        # Update state with summary
        return {
            **state,
            "summary": summary,
            "status": "summary_generated"
        }
        
    except Exception as e:
        app_logger.error(f"Error generating summary: {e}")
        return {
            **state,
            "error": f"Failed to generate summary: {str(e)}",
            "status": "error"
        }
