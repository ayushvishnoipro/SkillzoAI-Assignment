from typing import Iterator, Dict, Any, AsyncIterator
import json
import inspect
import asyncio
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.utils.logger import app_logger

def model_to_dict(obj: Any) -> Any:
    """Convert Pydantic models and other objects to JSON-serializable format"""
    if isinstance(obj, BaseModel):
        return obj.dict()
    elif hasattr(obj, "__dict__"):
        return {k: model_to_dict(v) for k, v in obj.__dict__.items() 
                if not k.startswith("_")}
    elif isinstance(obj, list):
        return [model_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: model_to_dict(v) for k, v in obj.items()}
    else:
        return obj

async def stream_generator_async(iterator: AsyncIterator[Dict[Any, Any]]) -> AsyncIterator[str]:
    """
    Convert an async iterator of dictionaries to a server-sent events stream
    """
    try:
        # Send an initial keep-alive to establish the connection
        yield f": ping\n\n"
        
        async for item in iterator:
            # Ensure all data is JSON serializable
            serializable_item = model_to_dict(item)
            
            # Convert dict to JSON string
            try:
                json_data = json.dumps(serializable_item)
                # Format as SSE (Server-Sent Events)
                yield f"data: {json_data}\n\n"
                app_logger.debug(f"Streamed: {serializable_item.get('status', 'unknown')}")
            except Exception as e:
                app_logger.error(f"Error serializing stream data: {e}")
                yield f"data: {{\"status\": \"error\", \"message\": \"Error serializing response\"}}\n\n"
                
            # Add a small sleep to ensure browser receives the data
            await asyncio.sleep(0.1)
    except Exception as e:
        app_logger.error(f"Error in stream generator: {e}")
        yield f"data: {{\"status\": \"error\", \"message\": \"Stream interrupted\"}}\n\n"

def stream_generator(iterator: Iterator[Dict[Any, Any]]) -> Iterator[str]:
    """
    Convert an iterator of dictionaries to a server-sent events stream
    """
    # Send an initial keep-alive to establish the connection
    yield f": ping\n\n"
    
    for item in iterator:
        try:
            # Ensure all data is JSON serializable
            serializable_item = model_to_dict(item)
            
            # Convert dict to JSON string
            json_data = json.dumps(serializable_item)
            # Format as SSE (Server-Sent Events)
            yield f"data: {json_data}\n\n"
        except Exception as e:
            app_logger.error(f"Error in sync stream generator: {e}")
            yield f"data: {{\"status\": \"error\", \"message\": \"Error in stream\"}}\n\n"

def create_streaming_response(iterator: Any) -> StreamingResponse:
    """
    Create a FastAPI StreamingResponse from an iterator or async iterator
    """
    # Better check to determine if this is an async generator
    is_async_gen = inspect.isasyncgen(iterator) or asyncio.iscoroutine(iterator) or hasattr(iterator, "__aiter__")
    
    if is_async_gen:
        # For async iterator, use the async streaming function
        return StreamingResponse(
            stream_generator_async(iterator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )
    else:
        # For regular iterator
        return StreamingResponse(
            stream_generator(iterator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            }
        )
