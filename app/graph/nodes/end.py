"""
End node for LangGraph workflows
"""
from typing import Dict, Any
from app.services.checkpoint_utils import save_checkpoint
import asyncio

async def end_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Finalize the workflow and clean up the state
    
    Args:
        state: The current workflow state
        
    Returns:
        Dict[str, Any]: The finalized state
    """
    # Create a new state dict
    new_state = state.copy()
    
    # Mark as complete
    new_state["complete"] = True
    
    # Set final status
    if "error" in new_state:
        new_state["status"] = "error"
    else:
        new_state["status"] = "completed"
    
    # Save checkpoint if tracking_id is available
    if "tracking_id" in new_state:
        await save_checkpoint(new_state["tracking_id"], new_state)
    
    return new_state
