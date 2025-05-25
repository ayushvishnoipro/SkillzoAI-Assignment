# Troubleshooting Guide for Resume Analysis API

This guide helps you troubleshoot common issues with the Resume Analysis API.

## Common Errors and Solutions

### Must provide state_schema or input and output

**Error:**
```
Error in resume analysis: Must provide state_schema or input and output
```

**Solution:**
This error occurs with newer versions of LangGraph where a schema definition for the state is required. You can fix it by:

1. Updating the `app/graph/builder.py` file to include a state schema:
   ```python
   from typing import TypedDict, Dict, Any, List, Optional
   
   # Define a state schema
   class ResumeAnalysisState(TypedDict, total=False):
       resume_text: str
       # Add other state fields here
   
   # Then use it when creating the StateGraph
   workflow = StateGraph(state_schema=ResumeAnalysisState)
   ```

2. Or by downgrading to an older version of LangGraph that doesn't require this:
   ```
   pip install langgraph==0.0.14
   ```

### StateGraph.__init__() got an unexpected keyword argument 'name'

**Error:**
```
StateGraph.__init__() got an unexpected keyword argument 'name'
```

**Solution:**
This error occurs with newer versions of LangGraph where the 'name' parameter is no longer supported. You can fix it by:

1. Updating the `app/graph/builder.py` file to remove the 'name' parameter:
   ```python
   # Change this:
   workflow = StateGraph(name="resume_analysis")
   
   # To this:
   workflow = StateGraph()
   ```

2. Or by installing a compatible version of LangGraph:
   ```
   pip install langgraph==0.0.14
   ```

### 'StateGraph' object has no attribute 'set_finish_node'

**Error:**
```
AttributeError: 'StateGraph' object has no attribute 'set_finish_node'
```

**Solution:**
This error occurs when using a version of LangGraph that does not support the `set_finish_node` method. You can fix it by:

1. Updating the `app/graph/builder.py` file to use the `set_final_node` method instead:
   ```python
   # Change this:
   workflow.set_finish_node(node_id="end_node")
   
   # To this:
   workflow.set_final_node(node_id="end_node")
   ```

2. Or by installing a compatible version of LangGraph:
   ```
   pip install langgraph==0.0.14
   ```

### Graph must have an entrypoint: add at least one edge from START to another node

**Error:**
```
Graph must have an entrypoint: add at least one edge from START to another node
```

**Solution:**
This error occurs when the graph does not have a defined entrypoint. You can fix it by:

1. Ensuring that the `START` node has at least one outgoing edge to another node in the graph.
2. Updating the `app/graph/builder.py` file to define the entrypoint:
   ```python
   # Example of adding an edge from START to another node
   workflow.add_edge("START", "first_node")
   ```

### OpenAI API Key Issues

**Error:**
```
openai.error.AuthenticationError: Invalid API key
```

**Solution:**
1. Check if your API key is correctly set in the `.env` file
2. Make sure there are no extra spaces or quotes around the API key
3. Verify that your OpenAI account has sufficient credits
4. Run `python check_setup.py` to validate your API key

### Import Errors

**Error:**
```
ImportError: cannot import name 'X' from 'Y'
```

**Solution:**
This usually happens when package versions are incompatible. Try:
1. Installing exact versions specified in requirements.txt:
   ```
   pip install -r requirements.txt
   ```
2. If using a virtual environment, recreate it:
   ```
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

### Timeout Errors

**Error:**
```
HTTPException: Request timeout or API overloaded
```

**Solution:**
1. The LLM processing can take time, especially for large resumes
2. Try with a shorter resume first to test functionality
3. Check your internet connection
4. OpenAI might be experiencing high traffic - try again later
5. Add a longer timeout in the API calls

### Memory Issues

**Error:**
```
MemoryError or process killed without error message
```

**Solution:**
1. The application might be using too much memory with large resumes
2. Try processing smaller chunks of text
3. Make sure your system has sufficient available memory
4. Close other memory-intensive applications

### Channel names checkpoint_id are reserved

**Error:**
```
Channel names checkpoint_id are reserved
```

**Solution:**
This error occurs when using a reserved channel name in your configuration. You can fix it by:

1. Avoid using `checkpoint_id` as a channel name in your workflow configuration.
2. Update the `app/graph/builder.py` file to use a different channel name:
   ```python
   # Change this:
   workflow.add_channel("checkpoint_id", some_node)
   
   # To this:
   workflow.add_channel("custom_channel_name", some_node)
   ```

### create_structured_output_chain() got an unexpected keyword argument 'temperature'

**Error:**
```
create_structured_output_chain() got an unexpected keyword argument 'temperature'
```

**Solution:**
This error occurs when the `create_structured_output_chain` function is called with an unsupported keyword argument `temperature`. You can fix it by:

1. Updating the function call in your code to remove the `temperature` argument:
   ```python
   # Change this:
   chain = create_structured_output_chain(temperature=0.7)
   
   # To this:
   chain = create_structured_output_chain()
   ```

2. Or by checking the documentation of the library you are using to ensure the correct arguments are passed.

### type object 'SomeList' has no attribute 'model_json_schema'

**Error:**
```
type object 'SomeList' has no attribute 'model_json_schema'
```

**Solution:**
This error occurs when the `SomeList` object does not have the `model_json_schema` attribute. You can fix it by:

1. Checking the version of the library that defines `SomeList` and ensuring it is up-to-date.
2. Reviewing the documentation of the library to confirm the correct usage of `SomeList`.

## Running the Check Setup Utility

We've included a check_setup.py script to help diagnose issues:

```
python check_setup.py
```

This will verify:
- Required dependencies and their versions
- LangGraph compatibility with our code
- File structure
- OpenAI API key validity
- API connectivity

## Still Having Problems?

If you're still experiencing issues after trying these solutions:

1. Check the application logs for more detailed error messages
2. Make sure all required packages are installed with the correct versions
3. Verify that your Python version is 3.9 or higher
4. Try with a simple "Hello World" resume to rule out input-specific issues

## Contact Support

If you still need help, please file an issue on the GitHub repository with:
1. The exact error message
2. Steps to reproduce the issue
3. Your environment details (OS, Python version)
4. Any relevant logs
