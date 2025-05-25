# Resume Analysis API Architecture

This document explains the architecture of the Resume Analysis API using diagrams to visualize the flow of data through the system.

## API Endpoints Overview

The Resume Analysis API provides three main endpoints:
1. `/api/v1/analyze-resume` - Synchronous resume analysis
2. `/api/v1/analyze-resume-stream` - Streaming resume analysis
3. `/api/v1/resume-questions` - Generate interview questions

## Flow Diagrams

### 1. Analyze Resume Endpoint

This diagram shows the flow of data when using the synchronous resume analysis endpoint:

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI Endpoint
    participant Graph as LangGraph Workflow
    participant LLM as OpenAI LLM
    participant Models as Pydantic Models

    Client->>API: POST /api/v1/analyze-resume<br>{resume_text: "..."}
    Note over API: Create tracking ID
    API->>Graph: Build and invoke graph
    
    Graph->>Graph: start_node (Clean & Extract)
    Graph->>LLM: Extract work experience
    LLM-->>Graph: Return work experience
    
    Graph->>LLM: Extract education
    LLM-->>Graph: Return education
    
    Graph->>LLM: Generate summary
    LLM-->>Graph: Return summary
    
    Graph->>LLM: Generate insights
    LLM-->>Graph: Return insights
    
    Graph->>Graph: end_node (Compile results)
    Graph-->>API: Return structured data
    
    API->>Models: Validate & serialize response
    Models-->>API: ResumeAnalysisResponse
    
    API-->>Client: JSON Response with<br>structured_data and insights
```

### 2. Streaming Resume Analysis Endpoint

This diagram shows the streaming endpoint which provides real-time progress updates:

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI Endpoint
    participant Stream as Stream Generator
    participant Graph as LangGraph Workflow
    participant LLM as OpenAI LLM
    participant Checkpoint as Checkpoint Storage

    Client->>API: POST /api/v1/analyze-resume-stream<br>{resume_text: "..."}
    Note over API: Create tracking ID
    API->>Stream: Create stream generator
    API->>Graph: Start graph execution (async task)
    API-->>Client: Start SSE stream connection
    
    Stream-->>Client: Event: {"status": "started"}
    
    Graph->>Graph: start_node
    Graph->>Checkpoint: Save state
    Stream->>Checkpoint: Poll for updates
    Stream-->>Client: Event: {"status": "processing"}
    
    Graph->>LLM: Extract work experience
    Graph->>Checkpoint: Save state
    Stream->>Checkpoint: Poll for updates
    Stream-->>Client: Event: {"status": "work_experience_extracted"}
    
    Graph->>LLM: Extract education
    Graph->>Checkpoint: Save state
    Stream->>Checkpoint: Poll for updates
    Stream-->>Client: Event: {"status": "education_extracted"}
    
    Graph->>LLM: Generate summary
    Graph->>Checkpoint: Save state
    Stream->>Checkpoint: Poll for updates
    Stream-->>Client: Event: {"status": "summary_generated"}
    
    Graph->>LLM: Generate insights
    Graph->>Checkpoint: Save state
    Stream->>Checkpoint: Poll for updates
    Stream-->>Client: Event: {"status": "insights_generated"}
    
    Graph->>Graph: end_node
    Graph->>Checkpoint: Save final state
    Stream->>Checkpoint: Get final result
    
    Stream-->>Client: Event: {"status": "completed", "data": {...}}
```

### 3. Generate Interview Questions Endpoint

This diagram shows how the interview questions generation endpoint works:

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI Endpoint
    participant Graph as Questions Graph
    participant LLM as OpenAI LLM
    participant Models as Pydantic Models

    Client->>API: POST /api/v1/resume-questions<br>{resume_text: "...", job_description: "..."}
    Note over API: Create tracking ID
    API->>Graph: Build questions graph and invoke
    
    Graph->>Graph: start_node (Clean text)
    
    Graph->>LLM: Generate tailored questions
    Note over LLM: Parse resume & job description
    Note over LLM: Generate questions with<br>difficulty levels & rationales
    LLM-->>Graph: Return QuestionList
    
    Graph->>Graph: end_node (Compile results)
    Graph-->>API: Return questions array
    
    API->>Models: Validate & serialize response
    Models-->>API: ResumeQuestionResponse
    
    API-->>Client: JSON Response with questions array
```

## Internal Components

### LangGraph Architecture

The Resume Analysis API uses LangGraph to orchestrate the resume analysis process. Below is a diagram showing the graph structure:

```mermaid
graph TD
    START((START)) --> A[start_node]
    A --> B[extract_work_experience]
    B --> C[extract_education]
    C --> D[generate_summary]
    D --> E[insights_generated]
    E --> F[end_node]
    F --> END((END))
    
    %% Error handling paths
    A -- error --> F
    B -- error --> F
    C -- error --> F
    D -- error --> F
    E -- error --> F
```

### Data Processing Flow

This diagram shows how the resume data flows through the system:

```mermaid
flowchart TD
    A[Resume Text] --> B[Text Cleaning]
    B --> C[Section Extraction]
    
    C --> D1[Work Experience Extraction]
    C --> D2[Education Extraction]
    C --> D3[Skills Extraction]
    
    D1 & D2 & D3 --> E[Summary Generation]
    E --> F[Insights Generation]
    
    F --> G[Structured Data]
    G --> H[API Response]
```

## API Response Structure

The API returns structured data in JSON format. Here's a simplified view of the response structure:

```mermaid
classDiagram
    class ResumeAnalysisResponse {
        structured_data: ResumeData
        insights: ResumeInsights
    }
    
    class ResumeData {
        name: string
        email: string
        phone: string
        location: string
        summary: string
        work_experience: WorkExperience[]
        education: Education[]
        skills: string[]
        certifications: string[]
        languages: string[]
        projects: object[]
    }
    
    class ResumeInsights {
        strengths: string[]
        improvement_areas: string[]
        key_skills: string[]
        experience_summary: string
        career_level: string
        industry_fit: string[]
    }
    
    class ResumeQuestionResponse {
        questions: InterviewQuestion[]
        overview: string
    }
    
    class InterviewQuestion {
        question: string
        difficulty: string
        category: string
        intent: string
    }
    
    ResumeAnalysisResponse --> ResumeData
    ResumeAnalysisResponse --> ResumeInsights
```

## Conclusion

The Resume Analysis API uses a modular, graph-based architecture to process resumes in a structured manner. The system leverages large language models (LLMs) to extract information, generate insights, and create interview questions. The API offers both synchronous and streaming endpoints for flexibility and real-time progress updates.
