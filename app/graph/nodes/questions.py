from typing import Dict, Any, List, Optional
from app.services.llm_utils import create_structured_output_chain, get_llm
from app.models.response import InterviewQuestion
from app.utils.logger import app_logger
from pydantic import BaseModel

QUESTIONS_PROMPT = """
You are an expert technical interviewer and recruiter.

Based on the following resume information, generate {num_questions} insightful interview questions that will 
help evaluate this candidate thoroughly. Create a mix of technical, behavioral, and experience-based questions.

Resume Information:
{resume_text}

Job Description (if provided):
{job_description}

For each question:
1. Provide the question text
2. Specify the difficulty level (Easy, Medium, Hard)
3. Specify the category (Technical, Behavioral, Experience, Problem-solving, etc.)
4. Explain what the interviewer is trying to assess with this question

The questions should be tailored to this specific candidate's background and skills, and should help assess 
both technical competence and cultural fit. If a job description is provided, ensure the questions evaluate 
the candidate's suitability for that specific role.
"""

# Updated to use proper Pydantic model instead of List inheritance
class QuestionList(BaseModel):
    """List of interview questions"""
    entries: List[InterviewQuestion] = []

async def generate_questions(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate interview questions based on the resume
    
    Args:
        state: Current graph state including resume text, extracted data and optional job description
        
    Returns:
        Updated state with interview questions
    """
    app_logger.info("Generating interview questions")
    
    # Extract necessary information from state
    cleaned_text = state.get("cleaned_text", "")
    job_description = state.get("job_description", "")
    num_questions = state.get("num_questions", 5)
    
    try:
        # Get LLM with specified temperature first
        llm = get_llm(temperature=0.7)  # More creative for diverse questions
        
        # Create chain to generate structured questions
        questions_chain = create_structured_output_chain(
            QUESTIONS_PROMPT,
            QuestionList,
            llm=llm  # Pass the configured LLM
        )
        
        # Run the chain to get structured questions
        result = await questions_chain.ainvoke({
            "resume_text": cleaned_text if cleaned_text else state.get("resume_text", ""),
            "job_description": job_description or "No job description provided",
            "num_questions": num_questions
        })
        
        # Extract questions from the entries field
        questions = result.entries if hasattr(result, "entries") else []
        
        app_logger.info(f"Generated {len(questions)} interview questions")
        
        # Update state with questions
        return {
            **state,
            "questions": questions,
            "status": "questions_generated"
        }
        
    except Exception as e:
        app_logger.error(f"Error generating questions: {e}")
        return {
            **state,
            "error": f"Failed to generate questions: {str(e)}",
            "status": "error"
        }
