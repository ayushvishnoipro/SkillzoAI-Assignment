"""
Service for interacting with the language model
"""
import os
import openai
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.utils.logger import app_logger

# Initialize the OpenAI client
client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

async def call_llm(prompt: str, model: Optional[str] = None) -> str:
    """
    Call the language model with the given prompt
    
    Args:
        prompt: The text prompt to send to the model
        model: Optional model override, uses settings.MODEL_NAME by default
        
    Returns:
        str: The model's response text
    """
    try:
        # Use configured model or default to GPT-4
        model_name = model or settings.MODEL_NAME or "gpt-4o"
        
        app_logger.debug(f"Calling LLM with model: {model_name}")
        
        # Call the OpenAI API - fixed to properly use async/await
        # We need to create() instead of create.async() since the OpenAI client already manages async
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a professional resume analyzer. Provide accurate, structured information based on the resume text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # Lower temperature for more consistent output
            max_tokens=2000,  # Allow for longer responses
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content
        
        app_logger.debug(f"LLM response received, length: {len(response_text)}")
        return response_text
        
    except Exception as e:
        app_logger.error(f"LLM API call failed: {str(e)}")
        raise
