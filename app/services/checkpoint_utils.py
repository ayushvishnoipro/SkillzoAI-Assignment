from typing import Dict, Any, Optional
from uuid import uuid4
from pathlib import Path
import json
import os
from pydantic import BaseModel

from app.utils.logger import app_logger

# Default checkpoint directory
DEFAULT_CHECKPOINT_DIR = "checkpoints"

def generate_checkpoint_id() -> str:
    """Generate a unique ID for checkpointing"""
    return str(uuid4())

def serialize_for_json(obj: Any) -> Any:
    """Helper function to make objects JSON serializable"""
    if isinstance(obj, BaseModel):
        return obj.dict()
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    else:
        return obj

def save_checkpoint(checkpoint_id: str, data: Dict[str, Any], checkpoint_dir: Optional[str] = None) -> str:
    """
    Save checkpoint data to disk
    
    Args:
        checkpoint_id: Unique identifier for this checkpoint
        data: Dictionary of data to checkpoint
        checkpoint_dir: Directory to save checkpoints in
        
    Returns:
        Path to the checkpoint file
    """
    dir_path = Path(checkpoint_dir or DEFAULT_CHECKPOINT_DIR)
    dir_path.mkdir(exist_ok=True, parents=True)
    
    file_path = dir_path / f"{checkpoint_id}.json"
    
    try:
        # Serialize all data to ensure JSON compatibility
        serializable_data = serialize_for_json(data)
        
        with open(file_path, 'w') as f:
            json.dump(serializable_data, f)
        app_logger.debug(f"Checkpoint saved: {file_path}")
        return str(file_path)
    except Exception as e:
        app_logger.error(f"Error saving checkpoint: {e}")
        return ""

def load_checkpoint(checkpoint_id: str, checkpoint_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Load checkpoint data from disk
    
    Args:
        checkpoint_id: ID of the checkpoint to load
        checkpoint_dir: Directory where checkpoints are stored
        
    Returns:
        Dictionary of checkpoint data
    """
    dir_path = Path(checkpoint_dir or DEFAULT_CHECKPOINT_DIR)
    file_path = dir_path / f"{checkpoint_id}.json"
    
    if not file_path.exists():
        app_logger.warning(f"Checkpoint not found: {file_path}")
        return {}
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        app_logger.debug(f"Checkpoint loaded: {file_path}")
        return data
    except Exception as e:
        app_logger.error(f"Error loading checkpoint: {e}")
        return {}

def clear_checkpoint(checkpoint_id: str, checkpoint_dir: Optional[str] = None) -> bool:
    """
    Delete a checkpoint file
    
    Args:
        checkpoint_id: ID of the checkpoint to delete
        checkpoint_dir: Directory where checkpoints are stored
        
    Returns:
        True if successful, False otherwise
    """
    dir_path = Path(checkpoint_dir or DEFAULT_CHECKPOINT_DIR)
    file_path = dir_path / f"{checkpoint_id}.json"
    
    if not file_path.exists():
        return True
    
    try:
        os.remove(file_path)
        app_logger.debug(f"Checkpoint deleted: {file_path}")
        return True
    except Exception as e:
        app_logger.error(f"Error deleting checkpoint: {e}")
        return False
