# Resume Analysis Streamlit UI

This Streamlit app provides a clean, interactive user interface for the Resume Analysis API. It allows users to input resume text, analyze it, and view structured data, insights, and interview questions.

## Features

- Multiple input methods (text input, file upload, sample resume)
- Real-time streaming updates during analysis
- Organized display of resume components:
  - Contact information
  - Summary
  - Work experience
  - Education
  - Skills
- Insights visualization
- Interview question generation (when job description is provided)
- Raw JSON view for developers

## Setup and Usage

### Prerequisites

- Python 3.8+
- The Resume Analysis API running at http://localhost:8000

### Installation

1. Install the required packages:
   ```bash
   pip install -r streamlit_requirements.txt
   ```

### Running the App

1. Make sure the Resume Analysis API is running
2. Start the Streamlit app:
   ```bash
   cd ui
   streamlit run streamlit_app.py
   ```
3. Open your browser at http://localhost:8501

## Using the App

1. Choose an input method from the sidebar:
   - Text Input: Paste resume text directly
   - File Upload: Upload a .txt resume file
   - Sample Resume: Use the provided example

2. (Optional) Add a job description to generate tailored interview questions

3. Choose the analysis type:
   - Standard: Regular analysis with all features
   - Streaming: See real-time progress of the analysis

4. Click "Analyze Resume" to start the process

5. View the results in the various tabs:
   - Structured Data: Contact information, summary, work experience, education, skills
   - Insights: Strengths, improvement areas, career level, industry fit
   - Interview Questions: AI-generated questions based on the resume and job description
   - Raw JSON: Complete API response for developers

## Troubleshooting

- If you see a warning that the API is offline, make sure the Resume Analysis API is running at http://localhost:8000
- For file uploads, currently only .txt files are fully supported
- If the analysis takes too long, try refreshing the page and using the standard analysis mode instead of streaming
