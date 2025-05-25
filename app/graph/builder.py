from typing import Dict, Any, Optional, Callable, List, TypedDict, Annotated
import os
from langgraph.graph import StateGraph, END, START
from app.utils.logger import app_logger
from app.graph.nodes.start import start_node
from app.graph.nodes.extract_work import extract_work_experience
from app.graph.nodes.extract_education import extract_education
from app.graph.nodes.summary import generate_summary
from app.graph.nodes.insights import generate_insights
from app.graph.nodes.questions import generate_questions
from app.graph.nodes.end import end_node
from pydantic import BaseModel

# Define a state schema using TypedDict for the StateGraph
# Remove 'checkpoint_id' from the schema as it's a reserved name
class ResumeAnalysisState(TypedDict, total=False):
    resume_text: str
    cleaned_text: str
    contact_info: Dict[str, Any]
    sections: Dict[str, str]
    work_experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    summary: str
    insights: Dict[str, Any]
    structured_data: Dict[str, Any]
    questions: List[Dict[str, Any]]
    job_description: Optional[str]
    num_questions: int
    tracking_id: str  # Use tracking_id instead of checkpoint_id
    status: str
    error: Optional[str]
    complete: bool

def should_continue(state: Dict[str, Any]) -> str:
    """Determine the next node to execute based on state"""
    if state.get("error"):
        return "end"
    return state.get("status", "start")

def build_resume_analysis_graph() -> StateGraph:
    """
    Builds the full resume analysis workflow as a LangGraph
    
    Returns:
        StateGraph: The compiled graph for resume analysis
    """
    app_logger.info("Building resume analysis graph")
    
    # Create a new state graph with the defined schema
    workflow = StateGraph(state_schema=ResumeAnalysisState)
    
    # Add all nodes to the graph
    workflow.add_node("start", start_node)
    workflow.add_node("work_experience_extracted", extract_work_experience)
    workflow.add_node("education_extracted", extract_education)
    workflow.add_node("summary_generated", generate_summary)
    workflow.add_node("insights_generated", generate_insights)
    workflow.add_node("end", end_node)
    
    # Add entrypoint - connect START to the start node
    workflow.add_edge(START, "start")
    
    # Define the flow between nodes
    workflow.add_edge("start", "work_experience_extracted")
    workflow.add_edge("work_experience_extracted", "education_extracted")
    workflow.add_edge("education_extracted", "summary_generated")
    workflow.add_edge("summary_generated", "insights_generated")
    workflow.add_edge("insights_generated", "end")
    
    # Set conditional edges for error handling
    workflow.add_conditional_edges(
        "start",
        should_continue,
        {
            "error": "end",
            "processing": "work_experience_extracted"
        }
    )
    
    # Update for newer LangGraph API: Connect end node to END
    workflow.add_edge("end", END)
    
    # Compile the graph
    return workflow.compile()

def build_question_generation_graph() -> StateGraph:
    """
    Builds a focused graph for generating interview questions
    
    Returns:
        StateGraph: The compiled graph for question generation
    """
    app_logger.info("Building question generation graph")
    
    # Create a new state graph with the defined schema
    workflow = StateGraph(state_schema=ResumeAnalysisState)
    
    # Add nodes needed for question generation
    workflow.add_node("start", start_node)
    workflow.add_node("generate_questions", generate_questions)
    workflow.add_node("end", end_node)
    
    # Add entrypoint - connect START to the start node
    workflow.add_edge(START, "start")
    
    # Define simple linear flow
    workflow.add_edge("start", "generate_questions")
    workflow.add_edge("generate_questions", "end")
    
    # Set conditional edges for error handling
    workflow.add_conditional_edges(
        "start",
        should_continue,
        {
            "error": "end",
            "processing": "generate_questions"
        }
    )
    
    # Update for newer LangGraph API: Connect end node to END
    workflow.add_edge("end", END)
    
    # Compile the graph
    return workflow.compile()
