"""
Streamlit UI for Resume Analysis API
"""
import streamlit as st
import requests
import json
import time
from io import StringIO
import pandas as pd

# API Configuration
API_BASE = "http://localhost:8000/api/v1"
API_ANALYZE = f"{API_BASE}/analyze-resume"
API_STREAM = f"{API_BASE}/analyze-resume-stream"
API_QUESTIONS = f"{API_BASE}/resume-questions"

# Sample resume for testing
SAMPLE_RESUME = """John Doe
johndoe@email.com | (123) 456-7890 | San Francisco, CA

EXPERIENCE
Software Engineer at Tech Company
Jan 2020 - Present
• Developed and maintained web applications using React and Node.js
• Collaborated with cross-functional teams to deliver high-quality products

EDUCATION
B.S. Computer Science, University of California
2015 - 2019 | GPA: 3.8

SKILLS
JavaScript, Python, React, Node.js, SQL, AWS"""

def check_api_status():
    """Check if the API is available"""
    try:
        response = requests.get(f"{API_BASE.split('/api')[0]}/health", timeout=2)
        if response.status_code == 200:
            return True
        return False
    except requests.RequestException:
        return False

def display_contact_info(data):
    """Display contact information"""
    if not data:
        st.info("No contact information available")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Name:**", data.get("name", "Not specified"))
        st.write("**Email:**", data.get("email", "Not specified"))
    with col2:
        st.write("**Phone:**", data.get("phone", "Not specified"))
        st.write("**Location:**", data.get("location", "Not specified"))

def display_work_experience(experiences):
    """Display work experience"""
    if not experiences or len(experiences) == 0:
        st.info("No work experience found")
        return
    
    for i, exp in enumerate(experiences):
        with st.expander(f"{exp.get('position', 'Role')} at {exp.get('company', 'Company')}", expanded=(i == 0)):
            st.write(f"**Duration:** {exp.get('start_date', '')} - {exp.get('end_date', 'Present')}")
            st.write(f"**Description:** {exp.get('description', 'No description available')}")
            
            if exp.get('skills') and len(exp.get('skills')) > 0:
                st.write("**Skills used:**")
                skills_cols = st.columns(3)
                for idx, skill in enumerate(exp.get('skills')):
                    skills_cols[idx % 3].markdown(f"- {skill}")

def display_education(education_list):
    """Display education information"""
    if not education_list or len(education_list) == 0:
        st.info("No education information found")
        return
    
    for edu in education_list:
        degree = f"{edu.get('degree', '')} in {edu.get('field_of_study', 'Not specified')}"
        with st.expander(f"{degree} - {edu.get('institution', 'Institution')}"):
            st.write(f"**Duration:** {edu.get('start_date', '')} - {edu.get('end_date', 'Present')}")
            if edu.get('gpa'):
                st.write(f"**GPA:** {edu.get('gpa')}")

def display_skills(skills):
    """Display skills as a tag cloud"""
    if not skills or len(skills) == 0:
        st.info("No skills information available")
        return
    
    # Display as multi-column list
    cols = st.columns(3)
    for i, skill in enumerate(skills):
        cols[i % 3].markdown(f"- {skill}")

def display_insights(insights):
    """Display insights about the resume"""
    if not insights:
        st.info("No insights available")
        return
    
    # Career level
    st.subheader("Career Level")
    st.write(insights.get("career_level", "Not specified"))
    
    # Experience summary
    if "experience_summary" in insights:
        st.subheader("Experience Summary")
        st.write(insights.get("experience_summary", ""))
    
    # Strengths
    st.subheader("Strengths")
    strengths = insights.get("strengths", [])
    if strengths:
        for strength in strengths:
            st.markdown(f"- {strength}")
    else:
        st.info("No strengths identified")
    
    # Improvement Areas
    st.subheader("Areas for Improvement")
    improvements = insights.get("improvement_areas", [])
    if improvements:
        for area in improvements:
            st.markdown(f"- {area}")
    else:
        st.info("No improvement areas identified")
    
    # Industry Fit
    st.subheader("Industry Fit")
    industries = insights.get("industry_fit", [])
    if industries:
        cols = st.columns(3)
        for i, industry in enumerate(industries):
            cols[i % 3].markdown(f"- {industry}")
    else:
        st.info("No industry fit information available")

def display_questions(questions_data):
    """Display interview questions"""
    if not questions_data or "questions" not in questions_data or not questions_data["questions"]:
        st.info("No interview questions available")
        return
    
    # Overview
    if "overview" in questions_data:
        st.write(questions_data["overview"])
    
    # Questions
    for i, q in enumerate(questions_data["questions"]):
        # Determine difficulty badge color
        difficulty = q.get("difficulty", "Medium").lower()
        if difficulty == "easy":
            difficulty_color = "green"
        elif difficulty == "hard":
            difficulty_color = "red"
        else:
            difficulty_color = "orange"
            
        # Create expandable card for each question
        with st.expander(f"Q{i+1}: {q.get('question', 'Question not specified')}"):
            st.markdown(f"**Category:** {q.get('category', 'General')}")
            st.markdown(f"**Difficulty:** :{difficulty_color}[{q.get('difficulty', 'Medium')}]")
            st.markdown(f"**Intent:** {q.get('intent', 'Not specified')}")

def analyze_resume(resume_text, job_description=None):
    """Send resume text to API for analysis"""
    with st.spinner("Analyzing resume..."):
        try:
            # First call the analysis endpoint
            analysis_response = requests.post(
                API_ANALYZE,
                json={"resume_text": resume_text},
                timeout=60  # Longer timeout for analysis
            )
            
            if analysis_response.status_code != 200:
                st.error(f"Analysis failed: {analysis_response.text}")
                return None
            
            analysis_data = analysis_response.json()
            
            # If job description is provided, also get interview questions
            if job_description:
                questions_response = requests.post(
                    API_QUESTIONS,
                    json={
                        "resume_text": resume_text,
                        "job_description": job_description,
                        "num_questions": 5
                    },
                    timeout=60
                )
                
                if questions_response.status_code == 200:
                    analysis_data["questions_data"] = questions_response.json()
            
            return analysis_data
            
        except requests.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return None

def stream_analyze_resume(resume_text):
    """Stream resume analysis with progress updates"""
    progress_bar = st.progress(0)
    status_placeholder = st.empty()
    
    params = {"resume_text": resume_text}
    final_data = None
    
    try:
        with requests.get(API_STREAM, params=params, stream=True) as response:
            if response.status_code != 200:
                st.error(f"Stream request failed: {response.text}")
                return None
            
            # Process the streaming response
            buffer = ""
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    text = chunk.decode('utf-8')
                    buffer += text
                    lines = buffer.split('\n\n')
                    buffer = lines.pop() if lines else ""
                    
                    for line in lines:
                        if line.startswith("data: "):
                            data_json = line[6:]  # Remove "data: " prefix
                            try:
                                data = json.loads(data_json)
                                
                                # Update progress based on status
                                status = data.get("status", "")
                                message = data.get("message", "Processing...")
                                
                                # Update progress bar
                                if status == "started":
                                    progress_bar.progress(10)
                                elif status == "processing":
                                    progress_bar.progress(20)
                                elif status == "work_experience_extracted":
                                    progress_bar.progress(40)
                                elif status == "education_extracted":
                                    progress_bar.progress(60)
                                elif status == "summary_generated":
                                    progress_bar.progress(80)
                                elif status == "insights_generated":
                                    progress_bar.progress(90)
                                elif status == "completed":
                                    progress_bar.progress(100)
                                    final_data = data.get("data")
                                    status_placeholder.success("Analysis complete!")
                                elif status == "error":
                                    progress_bar.progress(100)
                                    status_placeholder.error(f"Error: {message}")
                                    
                                # Update status message
                                status_placeholder.info(message)
                                
                            except json.JSONDecodeError:
                                status_placeholder.warning(f"Received invalid JSON: {data_json[:100]}...")
        
        return final_data
        
    except requests.RequestException as e:
        status_placeholder.error(f"Stream request failed: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Resume Analyzer",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("Resume Analysis Dashboard")
    st.write("Upload a resume to extract structured data, insights, and interview questions.")
    
    # Check API status and display a warning if not available
    api_available = check_api_status()
    if not api_available:
        st.warning("⚠️ The Resume Analysis API appears to be offline. Make sure it's running at http://localhost:8000")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("Input")
        input_method = st.radio("Resume Input Method:", ["Text Input", "File Upload", "Sample Resume"])
        
        resume_text = ""
        if input_method == "Text Input":
            resume_text = st.text_area("Paste Resume Text:", height=300)
        elif input_method == "File Upload":
            uploaded_file = st.file_uploader("Upload Resume:", type=["txt", "pdf", "docx"])
            if uploaded_file:
                # Currently only handle text files properly
                if uploaded_file.type == "text/plain":
                    resume_text = StringIO(uploaded_file.getvalue().decode("utf-8")).read()
                else:
                    st.warning("Currently only .txt files are fully supported")
        else:  # Sample Resume
            resume_text = SAMPLE_RESUME
            st.text_area("Sample Resume:", value=SAMPLE_RESUME, height=300, disabled=True)
        
        # Job description for interview questions
        st.divider()
        job_description = st.text_area("Job Description (Optional):", 
                                     help="Providing a job description will generate more targeted interview questions.")
        
        # Analysis type
        analysis_type = st.radio("Analysis Type:", ["Standard", "Streaming"])
        
        # Analysis button
        analyze_button = st.button("Analyze Resume", type="primary", disabled=not resume_text or not api_available)
    
    # Main content area for results
    if analyze_button and resume_text:
        if analysis_type == "Standard":
            # Normal synchronous analysis
            data = analyze_resume(resume_text, job_description if job_description else None)
            if data:
                # Create tabs for different sections
                tab1, tab2, tab3, tab4 = st.tabs(["Structured Data", "Insights", "Interview Questions", "Raw JSON"])
                
                with tab1:  # Structured Data
                    st.subheader("Contact Information")
                    display_contact_info(data.get("structured_data", {}))
                    
                    st.subheader("Summary")
                    summary = data.get("structured_data", {}).get("summary")
                    if summary:
                        st.write(summary)
                    else:
                        st.info("No summary available")
                    
                    st.subheader("Work Experience")
                    display_work_experience(data.get("structured_data", {}).get("work_experience", []))
                    
                    st.subheader("Education")
                    display_education(data.get("structured_data", {}).get("education", []))
                    
                    st.subheader("Skills")
                    display_skills(data.get("insights", {}).get("key_skills", []))
                
                with tab2:  # Insights
                    display_insights(data.get("insights", {}))
                
                with tab3:  # Interview Questions
                    if "questions_data" in data:
                        display_questions(data.get("questions_data", {}))
                    elif job_description:
                        st.info("Questions could not be generated. Please try again.")
                    else:
                        st.info("Provide a job description to generate interview questions")
                
                with tab4:  # Raw JSON
                    st.json(data)
        
        else:  # Streaming analysis
            data = stream_analyze_resume(resume_text)
            if data:
                # Show results after streaming completes
                st.subheader("Analysis Results")
                
                # Create tabs for different sections
                tab1, tab2, tab3 = st.tabs(["Structured Data", "Insights", "Raw JSON"])
                
                with tab1:  # Structured Data
                    st.subheader("Contact Information")
                    display_contact_info(data.get("structured_data", {}))
                    
                    st.subheader("Summary")
                    summary = data.get("structured_data", {}).get("summary")
                    if summary:
                        st.write(summary)
                    else:
                        st.info("No summary available")
                    
                    st.subheader("Work Experience")
                    display_work_experience(data.get("structured_data", {}).get("work_experience", []))
                    
                    st.subheader("Education")
                    display_education(data.get("structured_data", {}).get("education", []))
                    
                    st.subheader("Skills")
                    display_skills(data.get("insights", {}).get("key_skills", []))
                
                with tab2:  # Insights
                    display_insights(data.get("insights", {}))
                
                with tab3:  # Raw JSON
                    st.json(data)

if __name__ == "__main__":
    main()
