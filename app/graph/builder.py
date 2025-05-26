"""
Builder functions for constructing LangGraph workflows
"""
from typing import Dict, Any, Optional, Callable, List, TypedDict, Annotated
import os
import uuid
from datetime import datetime
import asyncio

from langgraph.graph import StateGraph, END, START

from app.utils.logger import app_logger
from app.graph.nodes.start import start_node
from app.graph.nodes.extract_work import extract_work_experience
from app.graph.nodes.extract_education import extract_education
from app.graph.nodes.summary import generate_summary
from app.graph.nodes.insights import generate_insights
from app.graph.nodes.questions import generate_questions
from app.graph.nodes.end import end_node
from app.graph.nodes.structure import extract_structured_data
from app.services.checkpoint_utils import save_checkpoint
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
    streaming_enabled: bool  # Flag to enable streaming for specific nodes

def should_continue(state: Dict[str, Any]) -> str:
    """Determine the next node to execute based on state"""
    if state.get("error"):
        return "end"
    return state.get("status", "start")

def build_resume_analysis_graph():
    """
    Build the resume analysis graph with custom state management to enable streaming
    """
    # Create a new StateGraph instance with proper state schema
    workflow = StateGraph(state_schema=ResumeAnalysisState)
    
    # Define node functions with streaming updates
    async def process_resume_text(state: Dict[str, Any]):
        """Process the input resume text"""
        # Save checkpoint with status for streaming
        tracking_id = state.get("tracking_id")
        if tracking_id:
            new_state = state.copy()
            new_state["status"] = "processing"
            await save_checkpoint(tracking_id, new_state)
            
        # Return state unchanged for next step
        return state
    
    async def extract_structure(state: Dict[str, Any]):
        """Extract structured data from the resume"""
        result = await extract_structured_data(state["resume_text"])
        
        # Update state with structured data
        new_state = state.copy()
        new_state["structured_data"] = result
        
        return new_state
        
    async def process_work_experience(state: Dict[str, Any]):
        """Extract and process work experience"""
        if "structured_data" not in state:
            return state
            
        # Extract work experience
        result = await extract_work_experience(state["resume_text"], state["structured_data"])
        
        # Update state
        new_state = state.copy()
        new_state["structured_data"]["work_experience"] = result
        
        # Save checkpoint with status for streaming
        tracking_id = state.get("tracking_id")
        if tracking_id:
            new_state["status"] = "work_experience_extracted"
            await save_checkpoint(tracking_id, new_state)
            
        return new_state
        
    async def process_education(state: Dict[str, Any]):
        """Extract and process education"""
        if "structured_data" not in state:
            return state
            
        # Extract education
        result = await extract_education(state["resume_text"], state["structured_data"])
        
        # Update state
        new_state = state.copy()
        new_state["structured_data"]["education"] = result
        
        # Save checkpoint with status for streaming
        tracking_id = state.get("tracking_id")
        if tracking_id:
            new_state["status"] = "education_extracted"
            await save_checkpoint(tracking_id, new_state)
            
        return new_state
        
    async def process_summary(state: Dict[str, Any]):
        """Generate professional summary"""
        if "structured_data" not in state:
            return state
            
        # Generate summary
        summary = await generate_summary(state["structured_data"])
        
        # Update state
        new_state = state.copy()
        new_state["structured_data"]["summary"] = summary
        
        # Save checkpoint with status for streaming
        tracking_id = state.get("tracking_id")
        if tracking_id:
            new_state["status"] = "summary_generated"
            await save_checkpoint(tracking_id, new_state)
            
        return new_state
        
    async def process_insights(state: Dict[str, Any]):
        """Generate professional insights"""
        if "structured_data" not in state:
            return state
            
        # Generate insights
        insights = await generate_insights(state["structured_data"])
        
        # Update state
        new_state = state.copy()
        new_state["insights"] = insights
        
        # Save checkpoint with status for streaming
        tracking_id = state.get("tracking_id")
        if tracking_id:
            new_state["status"] = "insights_generated"
            await save_checkpoint(tracking_id, new_state)
            
        return new_state
    
    # Add nodes - Use different names for nodes to avoid conflicts with state keys
    workflow.add_node("process_text", process_resume_text)
    workflow.add_node("extract_structure", extract_structure)
    workflow.add_node("work_exp_node", process_work_experience)  # Renamed from work_experience
    workflow.add_node("edu_node", process_education)  # Renamed from education to edu_node
    workflow.add_node("summary_node", process_summary)  # Renamed from summary to summary_node
    workflow.add_node("insights_node", process_insights)  # Renamed from insights to insights_node
    
    # Define edges - update edge connections to use new node names
    workflow.add_edge("process_text", "extract_structure")
    workflow.add_edge("extract_structure", "work_exp_node")
    workflow.add_edge("work_exp_node", "edu_node")  # Updated
    workflow.add_edge("edu_node", "summary_node")  # Updated
    workflow.add_edge("summary_node", "insights_node")  # Updated
    workflow.add_edge("insights_node", END)  # Updated
    
    # Set the entry point
    workflow.set_entry_point("process_text")
    
    # Create a compiled graph - remove the checkpointing parameter
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
