from typing import Dict, Any, List
from app.services.llm_utils import create_structured_output_chain, get_llm
from app.models.response import ResumeInsights
from app.utils.logger import app_logger

INSIGHTS_PROMPT = """
You are an expert resume analyst and career coach with years of experience evaluating resumes.

Based on the following resume information, provide detailed insights about the candidate's profile,
including strengths, areas for improvement, key skills, experience level, and industry fit.

Work Experience:
{work_experience}

Education:
{education}

Summary:
{summary}

Additional Information:
{resume_text}

Analyze this profile thoroughly and provide insights in the following areas:
1. Strengths (3-5 points)
2. Areas for improvement (2-3 points)
3. Key skills (technical and soft skills)
4. Brief summary of experience level
5. Career level (Entry, Mid, Senior, Executive)
6. Industries where this candidate would be a good fit
"""

async def generate_insights(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate insights about the resume
    
    Args:
        state: Current graph state including extracted resume data
        
    Returns:
        Updated state with resume insights
    """
    app_logger.info("Generating resume insights")
    
    # Extract necessary information from state
    work_experience = state.get("work_experience", [])
    education = state.get("education", [])
    summary = state.get("summary", "")
    cleaned_text = state.get("cleaned_text", "")
    
    # Format work experience for the prompt
    work_exp_text = "\n\n".join([
        f"{item.position} at {item.company}, {item.start_date} - {item.end_date}\n{item.description}" 
        for item in work_experience
    ]) if work_experience else "No work experience provided"
    
    # Format education for the prompt
    education_text = "\n\n".join([
        f"{item.degree} in {item.field_of_study} from {item.institution}, {item.start_date} - {item.end_date or 'Present'}" 
        for item in education
    ]) if education else "No education provided"
    
    try:
        # Get LLM with specified temperature first
        llm = get_llm(temperature=0.4)  # More creative but still professional
        
        # Create chain to generate structured insights, passing the LLM instance
        insights_chain = create_structured_output_chain(
            INSIGHTS_PROMPT,
            ResumeInsights,
            llm=llm  # Pass the configured LLM
        )
        
        # Run the chain to get structured insights
        input_data = {
            "work_experience": work_exp_text,
            "education": education_text,
            "summary": summary,
            "resume_text": cleaned_text
        }
        
        insights = await insights_chain.ainvoke(input_data)
        
        app_logger.info("Resume insights generated successfully")
        
        # Update state with insights
        return {
            **state,
            "insights": insights,
            "status": "insights_generated"
        }
        
    except Exception as e:
        app_logger.error(f"Error generating insights: {e}")
        return {
            **state,
            "error": f"Failed to generate insights: {str(e)}",
            "status": "error"
        }
