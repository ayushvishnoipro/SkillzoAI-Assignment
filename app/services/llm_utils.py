from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from typing import Any, Dict, Type, TypeVar, Optional, List, Union
from pydantic import BaseModel

from app.core.config import settings
from app.utils.logger import app_logger

T = TypeVar("T", bound=BaseModel)

def get_llm(model: Optional[str] = None, temperature: float = 0.1, streaming: bool = False):
    """Get a LangChain LLM instance with the specified parameters"""
    model_name = model or settings.LLM_MODEL
    
    try:
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name=model_name,
            temperature=temperature,
            streaming=streaming,
        )
    except Exception as e:
        app_logger.error(f"Error initializing LLM: {e}")
        raise

def create_structured_output_chain(
    prompt_template: str,
    output_class: Type[T],
    llm=None,
    include_raw: bool = False
) -> Any:
    """
    Create a LangChain chain that produces structured output using a Pydantic model
    
    Args:
        prompt_template: The template for the prompt
        output_class: The Pydantic class to parse the output into
        llm: Optional LLM instance (will create default if not provided)
        include_raw: Whether to include the raw LLM output in the result
        
    Returns:
        A LangChain chain that can be invoked with input variables
    """
    if llm is None:
        llm = get_llm()
    
    parser = PydanticOutputParser(pydantic_object=output_class)
    
    prompt = PromptTemplate(
        template=f"{prompt_template}\n\n{{format_instructions}}",
        input_variables=["input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    if include_raw:
        chain = (
            {"input": RunnablePassthrough()}
            | prompt
            | {"raw_output": RunnablePassthrough(), "structured_output": llm | parser}
        )
    else:
        chain = prompt | llm | parser
        
    return chain
