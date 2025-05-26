"""
Node for generating interview questions based on resume and job description
"""
from typing import Dict, Any, List, Optional
import asyncio
from app.services.llm_service import call_llm
from app.services.parser import extract_json_from_llm_response
from app.utils.logger import app_logger

async def generate_questions(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate tailored interview questions based on resume text and job description
    
    Args:
        state: The current workflow state containing resume_text and job_description
        
    Returns:
        Dict[str, Any]: Updated state with generated questions
    """
    resume_text = state.get("resume_text", "")
    job_description = state.get("job_description", "")
    num_questions = state.get("num_questions", 5)
    
    # Create the prompt
    prompt = f"""
    Generate {num_questions} interview questions for a job candidate based on their resume
    {f'and the job description' if job_description else ''}.
    
    For each question:
    1. Create a challenging but fair interview question
    2. Assign a difficulty level (Easy, Medium, Hard)
    3. Categorize the question (e.g., Technical, Behavioral, Problem-solving)
    4. Explain the intent of the question (what you're trying to assess)
    
    Format as a JSON array of objects with these properties:
    - question (string)
    - difficulty (string: Easy, Medium, or Hard)
    - category (string)
    - intent (string)
    
    RESUME:
    {resume_text}
    
    {'JOB DESCRIPTION:' if job_description else ''}
    {job_description if job_description else ''}
    """
    
    try:
        response = await call_llm(prompt)
        questions_data = extract_json_from_llm_response(response)
        
        # Ensure we have a list
        if not isinstance(questions_data, list):
            if isinstance(questions_data, dict) and "questions" in questions_data:
                questions_data = questions_data["questions"]
            else:
                app_logger.warning("Question generation didn't return a list or proper dict")
                questions_data = []
        
        # Limit to requested number
        questions_data = questions_data[:num_questions]
        
        app_logger.info(f"Generated {len(questions_data)} interview questions")
        
        # Update state with questions
        new_state = state.copy()
        new_state["questions"] = questions_data
        return new_state
        
    except Exception as e:
        app_logger.error(f"Error generating interview questions: {e}")
        
        # Update state with error
        new_state = state.copy()
        new_state["error"] = f"Failed to generate questions: {str(e)}"
        new_state["questions"] = []
        return new_state
