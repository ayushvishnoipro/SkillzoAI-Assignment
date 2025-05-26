"""
Utilities for managing checkpoints and state persistence
"""
from typing import Dict, Any, Optional
import uuid
import json
import os
import tempfile
from datetime import datetime
from app.utils.logger import app_logger

# In-memory storage for checkpoints
_checkpoints = {}

def generate_checkpoint_id() -> str:
    """
    Generate a unique checkpoint ID
    
    Returns:
        str: Unique ID for checkpoint tracking
    """
    return f"ckpt-{uuid.uuid4()}"

async def save_checkpoint(checkpoint_id: str, state: Dict[str, Any]) -> None:
    """
    Save a checkpoint with the given ID
    
    Args:
        checkpoint_id: Unique identifier for the checkpoint
        state: State dictionary to save
    """
    try:
        # Create a copy to avoid modification issues
        state_copy = state.copy()
        
        # Add timestamp
        state_copy['timestamp'] = datetime.now().isoformat()
        
        # Store in memory
        _checkpoints[checkpoint_id] = state_copy
        app_logger.debug(f"Checkpoint saved: {checkpoint_id}")
        
        # Optionally save to disk for persistence
        # This could be replaced with database storage in a production system
        try:
            checkpoint_dir = os.path.join(tempfile.gettempdir(), "resume_analysis_checkpoints")
            os.makedirs(checkpoint_dir, exist_ok=True)
            
            checkpoint_path = os.path.join(checkpoint_dir, f"{checkpoint_id}.json")
            with open(checkpoint_path, 'w') as f:
                json.dump(state_copy, f)
        except Exception as e:
            app_logger.warning(f"Failed to persist checkpoint to disk: {e}")
    except Exception as e:
        app_logger.error(f"Error saving checkpoint: {e}")

def load_checkpoint(checkpoint_id: str) -> Optional[Dict[str, Any]]:
    """
    Load a checkpoint by ID
    
    Args:
        checkpoint_id: Unique identifier for the checkpoint
        
    Returns:
        Optional[Dict[str, Any]]: The checkpoint state or None if not found
    """
    # First try in-memory cache
    if checkpoint_id in _checkpoints:
        return _checkpoints[checkpoint_id]
    
    # Fall back to disk storage if not in memory
    try:
        checkpoint_dir = os.path.join(tempfile.gettempdir(), "resume_analysis_checkpoints")
        checkpoint_path = os.path.join(checkpoint_dir, f"{checkpoint_id}.json")
        
        if os.path.exists(checkpoint_path):
            with open(checkpoint_path, 'r') as f:
                state = json.load(f)
                # Cache in memory for future access
                _checkpoints[checkpoint_id] = state
                return state
    except Exception as e:
        app_logger.error(f"Error loading checkpoint from disk: {e}")
    
    return None

def clear_checkpoint(checkpoint_id: str) -> bool:
    """
    Clear a checkpoint by ID
    
    Args:
        checkpoint_id: Unique identifier for the checkpoint
        
    Returns:
        bool: True if successfully cleared, False otherwise
    """
    try:
        # Remove from in-memory storage
        if checkpoint_id in _checkpoints:
            del _checkpoints[checkpoint_id]
        
        # Remove from disk if exists
        checkpoint_dir = os.path.join(tempfile.gettempdir(), "resume_analysis_checkpoints")
        checkpoint_path = os.path.join(checkpoint_dir, f"{checkpoint_id}.json")
        
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)
        
        return True
    except Exception as e:
        app_logger.error(f"Error clearing checkpoint: {e}")
        return False
