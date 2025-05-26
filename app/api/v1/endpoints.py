from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

import asyncio
from app.models.resume import ResumeRequest, ResumeQuestionRequest
from app.models.response import ResumeAnalysisResponse, ResumeQuestionResponse
from app.graph.builder import build_resume_analysis_graph, build_question_generation_graph
from app.services.checkpoint_utils import generate_checkpoint_id, save_checkpoint, load_checkpoint
from app.utils.streaming import create_streaming_response
from app.utils.logger import app_logger

router = APIRouter()

@router.post(
    "/analyze-resume", 
    response_model=ResumeAnalysisResponse,
    summary="Analyze Resume",
    description="""
    Analyzes a resume and extracts structured information with insights.
    
    This endpoint takes raw resume text and returns:
    - Structured resume data (education, work experience, skills)
    - Professional insights about the candidate
    
    Note: This operation may take 15-30 seconds to complete depending on the resume length.
    """
)
async def analyze_resume(request: ResumeRequest):
    """
    Analyze a resume and extract structured information with insights
    """
    try:
        # Build the resume analysis graph
        graph = build_resume_analysis_graph()
        
        # Generate a unique ID for tracking but don't include it in the state
        tracking_id = generate_checkpoint_id()
        
        # Initial state with the resume text - avoid using 'checkpoint_id' as it's reserved
        initial_state = {
            "resume_text": request.resume_text,
            "tracking_id": tracking_id  # Use a different name to avoid reserved names
        }
        
        # Execute the graph
        app_logger.info(f"Starting resume analysis (tracking ID: {tracking_id})")
        result = await graph.ainvoke(initial_state)
        
        # Check for errors
        if "error" in result:
            app_logger.error(f"Resume analysis failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Return structured response
        return ResumeAnalysisResponse(
            structured_data=result["structured_data"],
            insights=result["insights"]
        )
        
    except Exception as e:
        app_logger.error(f"Error in resume analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
@router.post(
    "/analyze-resume-with-streaming-summary", 
    summary="Analyze Resume with Streaming Summary",
    description="""
    Analyzes a resume and streams the summary generation in real-time.
    
    This endpoint streams the summary generation and then returns the final result.
    
    The response uses Server-Sent Events (SSE) format.
    """
)
async def analyze_resume_streaming_summary(request: ResumeRequest):
    """
    Analyze a resume and stream the summary generation in real-time
    """
    try:
        # Build the resume analysis graph
        graph = build_resume_analysis_graph()
        
        # Generate a unique ID for tracking
        tracking_id = generate_checkpoint_id()
        resume_checkpoint_key = f"resume_text_{tracking_id}"
        
        # Initial state with the resume text
        initial_state = {
            "resume_text": request.resume_text,
            "tracking_id": tracking_id,
            "streaming_enabled": True,  # Flag to enable streaming in specific nodes
        }
        
        # Save the state for potential resumption
        await save_checkpoint(resume_checkpoint_key, {
            "resume_text": request.resume_text,
            "tracking_id": tracking_id,
        })

        app_logger.info(f"Starting resume analysis with streaming summary (tracking ID: {tracking_id})")

        # Create an async generator that filters for summary node outputs
        async def stream_summary_generation():
            # Send initial status
            yield {"status": "started", "message": "Analysis started"}
            
            # Get the LangGraph output stream - use astream_events for intermediate results
            async for event in graph.astream_events(
                initial_state, 
                stream_mode="values",  # Stream node outputs
            ):
                # Check if this is from the summary node
                if "summary_node" in str(event):
                    node_name = event.get("langgraph_node", "")
                    state = event.get("value", {})
                    
                    if node_name == "summary_node" and isinstance(state, dict):
                        # Extract the summary text
                        if state.get("structured_data", {}).get("summary"):
                            summary = state["structured_data"]["summary"]
                            yield {
                                "status": "summary_generating", 
                                "message": "Generating summary", 
                                "data": {"partial_summary": summary}
                            }
            
            # After summary is generated, continue with the analysis by resuming from cached state
            final_result = await graph.ainvoke(initial_state)
            
            # Return the complete analysis results
            yield {
                "status": "completed",
                "message": "Analysis complete",
                "data": {
                    "structured_data": final_result.get("structured_data", {}),
                    "insights": final_result.get("insights", {})
                }
            }
                
        # Return a streaming response
        return create_streaming_response(stream_summary_generation())
        
    except Exception as e:
        app_logger.error(f"Error in streaming summary analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/analyze-resume-stream",
    summary="Analyze Resume (Streaming)",
    description="""
    Analyzes a resume and returns results as a stream.
    
    This endpoint streams back progress updates as the resume is being analyzed,
    allowing for a more interactive user experience.
    
    The response is in Server-Sent Events (SSE) format.
    
    Note: To view the stream in Swagger UI, use the "Try it out" feature and view the raw server response.
    """
)
async def analyze_resume_stream(request: ResumeRequest, req: Request = None):
    """
    Analyze a resume and return results as a stream
    """
    try:
        # Build the resume analysis graph in streaming mode
        graph = build_resume_analysis_graph()
        
        # Generate a unique ID for tracking but store outside the state
        tracking_id = generate_checkpoint_id()
        
        # Initial state with the resume text - avoid using 'checkpoint_id' as it's reserved
        initial_state = {
            "resume_text": request.resume_text,
            "tracking_id": tracking_id  # Use a different name to avoid reserved names
        }
        
        # Log the request
        app_logger.info(f"Streaming analysis started (tracking ID: {tracking_id})")
        
        # Start the graph execution as a background task
        task = asyncio.create_task(graph.ainvoke(initial_state))
        
        # Create an async generator that will process the graph and yield updates
        async def generate_stream():
            """Async generator for streaming resume analysis results"""
            # Track what we've already streamed
            streamed_steps = set()
            
            # Stream initial confirmation
            yield {"status": "started", "message": "Resume analysis started"}
            
            while not task.done():
                # Check current checkpoint using tracking ID
                current_state = load_checkpoint(tracking_id)
                current_status = current_state.get("status", "")
                
                # Stream updates for new steps
                if current_status and current_status not in streamed_steps:
                    yield {
                        "status": current_status,
                        "message": f"Completed: {current_status.replace('_', ' ')}"
                    }
                    streamed_steps.add(current_status)
                
                # Wait a bit before checking again
                await asyncio.sleep(0.5)
            
            # Get the final result
            try:
                result = task.result()
                if "error" in result:
                    yield {"status": "error", "message": result["error"]}
                else:
                    # Ensure all Pydantic models are converted to dictionaries
                    # Stream final results with serializable data
                    structured_data = result.get("structured_data", {})
                    insights = result.get("insights", {})
                    
                    if hasattr(structured_data, "dict"):
                        structured_data = structured_data.dict()
                    
                    if hasattr(insights, "dict"):
                        insights = insights.dict()
                    
                    yield {
                        "status": "completed",
                        "message": "Analysis complete",
                        "data": {
                            "structured_data": structured_data,
                            "insights": insights
                        }
                    }
            except Exception as e:
                app_logger.error(f"Error completing streaming analysis: {e}")
                yield {"status": "error", "message": str(e)}
                
        # Create and return the streaming response with the async generator
        return create_streaming_response(generate_stream())
        
    except Exception as e:
        app_logger.error(f"Error in resume analysis stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add a GET endpoint for streaming to make it easier to use with EventSource
@router.get(
    "/analyze-resume-stream",
    summary="Analyze Resume (Streaming GET)",
    description="""
    Analyzes a resume and returns results as a stream using GET request.
    
    This endpoint is designed to work with EventSource in browsers.
    Pass the resume text as a query parameter.
    
    The response is in Server-Sent Events (SSE) format.
    """
)
async def analyze_resume_stream_get(resume_text: str, req: Request = None):
    """
    Analyze a resume and return results as a stream (GET method for EventSource)
    """
    # Create a ResumeRequest from the query parameter
    request = ResumeRequest(resume_text=resume_text)
    
    # Use the same implementation as the POST endpoint
    return await analyze_resume_stream(request, req)

@router.post(
    "/resume-questions", 
    response_model=ResumeQuestionResponse,
    summary="Generate Interview Questions",
    description="""
    Generates tailored interview questions based on a resume and optional job description.
    
    This endpoint analyzes a resume and creates targeted interview questions to help assess the candidate.
    Providing a job description helps tailor the questions to specific role requirements.
    
    You can specify how many questions to generate with the 'num_questions' parameter (default: 5).
    """
)
async def generate_resume_questions(request: ResumeQuestionRequest):
    """
    Generate interview questions based on a resume and optional job description
    """
    try:
        # Build the question generation graph
        graph = build_question_generation_graph()
        
        # Initial state - avoid using reserved names
        initial_state = {
            "resume_text": request.resume_text,
            "job_description": request.job_description,
            "num_questions": request.num_questions,
            "tracking_id": generate_checkpoint_id()  # Use tracking_id instead of checkpoint_id
        }
        
        # Execute the graph
        app_logger.info("Generating interview questions")
        result = await graph.ainvoke(initial_state)
        
        # Check for errors
        if "error" in result:
            app_logger.error(f"Question generation failed: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Prepare overview
        overview = "These questions are tailored to the candidate's background and skills, designed to assess their technical abilities and fit for the role."
        
        # Return structured response
        return ResumeQuestionResponse(
            questions=result["questions"],
            overview=overview
        )
        
    except Exception as e:
        app_logger.error(f"Error in question generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
