# Resume Analysis API

An advanced resume analysis system using FastAPI, LangGraph, and LLMs to extract structured information from resumes, generate insights, and create tailored interview questions.

## Features

- **Resume Parsing**: Extract structured data from resume text including work experience, education, skills, and more
- **Resume Insights**: Generate professional insights about the candidate's strengths and improvement areas
- **Interview Questions**: Generate tailored interview questions based on the resume content
- **Streaming Responses**: Stream analysis results in real-time with Server-Sent Events
- **LangGraph Workflow**: Modular, composable graph-based architecture for resume analysis

## Setup

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd resume_analysis_app
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

### Running the API

Start the API server:
```
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Usage

### Analyze Resume

```http
POST /api/v1/analyze-resume
Content-Type: application/json

{
    "resume_text": "Your resume content here..."
}
```

### Generate Interview Questions

```http
POST /api/v1/resume-questions
Content-Type: application/json

{
    "resume_text": "Your resume content here...",
    "job_description": "Optional job description...",
    "num_questions": 5
}
```

### Streaming Analysis

```http
POST /api/v1/analyze-resume-stream
Content-Type: application/json

{
    "resume_text": "Your resume content here..."
}
```

## Project Structure

```
resume_analysis_app/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configuration
│   ├── graph/        # LangGraph components
│   ├── models/       # Pydantic data models
│   ├── services/     # Services for LLM and parsing
│   ├── utils/        # Utility functions
│   ├── main.py       # Main application entrypoint
├── tests/            # Test modules
├── .env              # Environment variables
├── requirements.txt  # Python dependencies
```

## Testing

Run tests:
```
pytest
```

## License

[MIT License](LICENSE)
```
