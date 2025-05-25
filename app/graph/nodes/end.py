from typing import Dict, Any
from app.models.resume import ResumeData
from app.utils.logger import app_logger
from app.services.checkpoint_utils import save_checkpoint

async def end_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Final node in the graph that compiles all results into the final format
    
    Args:
        state: Current graph state with all extracted and generated data
        
    Returns:
        Final state with structured output
    """
    app_logger.info("Finalizing resume analysis")
    
    # Check for errors in previous steps
    if state.get("error"):
        app_logger.error(f"Analysis ended with error: {state.get('error')}")
        return {
            **state,
            "status": "error",
            "complete": True
        }
    
    try:
        # Compile all data into a structured resume data object
        contact_info = state.get("contact_info", {})
        
        # Convert any work experience and education objects to dictionaries
        work_experience = state.get("work_experience", [])
        education = state.get("education", [])
        
        # Ensure we have dictionaries for structured data
        if hasattr(work_experience, 'dict'):
            work_experience = work_experience.dict()
        
        if hasattr(education, 'dict'):
            education = education.dict()
        
        # Ensure each item in lists is also converted to dict
        if isinstance(work_experience, list):
            work_experience = [
                item.dict() if hasattr(item, 'dict') else item 
                for item in work_experience
            ]
        
        if isinstance(education, list):
            education = [
                item.dict() if hasattr(item, 'dict') else item 
                for item in education
            ]
        
        structured_data = ResumeData(
            name=contact_info.get("name"),
            email=contact_info.get("email"),
            phone=contact_info.get("phone"),
            location=contact_info.get("location"),
            summary=state.get("summary", ""),
            work_experience=work_experience,
            education=education,
            skills=state.get("skills", []),
            certifications=state.get("certifications", []),
            languages=state.get("languages", []),
            projects=state.get("projects", [])
        )
        
        # Convert the structured data to a dictionary
        structured_data_dict = structured_data.dict()
        
        # Get insights and ensure it's a dictionary
        insights = state.get("insights", {})
        if hasattr(insights, "dict"):
            insights_dict = insights.dict()
        else:
            insights_dict = insights
            
        # Create final response data
        final_state = {
            **state,
            "structured_data": structured_data_dict,
            "insights": insights_dict,
            "status": "completed",
            "complete": True
        }
        
        # Save checkpoint if tracking_id exists
        if tracking_id := state.get("tracking_id"):
            save_checkpoint(tracking_id, final_state)
            
        app_logger.info("Resume analysis completed successfully")
        
        return final_state
        
    except Exception as e:
        app_logger.error(f"Error in final analysis step: {e}")
        return {
            **state,
            "error": f"Failed to complete analysis: {str(e)}",
            "status": "error",
            "complete": True
        }
