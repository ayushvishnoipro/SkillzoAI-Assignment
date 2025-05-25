"""
Simple test script for the Resume Analysis API endpoints
"""
import requests
import json
import time
import sys

def test_resume_analysis(resume_text=None):
    """Test the resume analysis endpoint"""
    if resume_text is None:
        resume_text = """John Doe
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
    
    print("Testing /api/v1/analyze-resume endpoint...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/analyze-resume",
            json={"resume_text": resume_text},
            timeout=120  # Long timeout for LLM processing
        )
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success! Resume analyzed.")
            result = response.json()
            print("\nHighlights:")
            print(f"- Name: {result['structured_data']['name']}")
            print(f"- Email: {result['structured_data']['email']}")
            print(f"- Career level: {result['insights']['career_level']}")
            print(f"- Work experiences: {len(result['structured_data']['work_experience'])}")
            print(f"- Education entries: {len(result['structured_data']['education'])}")
            strengths = result['insights']['strengths']
            print(f"- Strengths: {len(strengths)} identified")
            for i, strength in enumerate(strengths[:2], 1):
                print(f"  {i}. {strength}")
            print("  ...")
        else:
            print("Error response:")
            print(response.text)
    except Exception as e:
        print(f"Error testing endpoint: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as file:
            resume_text = file.read()
        test_resume_analysis(resume_text)
    else:
        test_resume_analysis()
