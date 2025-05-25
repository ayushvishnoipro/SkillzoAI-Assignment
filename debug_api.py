"""
Debug script to test API endpoints directly
"""
import requests
import json
import sys
import time
import os
from pathlib import Path

# Ensure we can import from our app module
sys.path.append(os.path.dirname(__file__))

def test_analyze_resume():
    """Test the basic resume analysis endpoint"""
    url = "http://localhost:8000/api/v1/analyze-resume"
    
    # Sample resume text
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

    payload = {"resume_text": resume_text}
    headers = {"Content-Type": "application/json"}
    
    print("Testing /api/v1/analyze-resume endpoint...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Success! Response received.")
            print(f"Response size: {len(response.text)} bytes")
            
            # Save response to file for inspection
            with open("debug_response.json", "w") as f:
                json.dump(result, f, indent=2)
            print(f"Response saved to debug_response.json")
            
            # Print key elements
            if "structured_data" in result:
                sd = result["structured_data"]
                print(f"Name: {sd.get('name')}")
                print(f"Email: {sd.get('email')}")
                print(f"Work experiences: {len(sd.get('work_experience', []))}")
            else:
                print("No structured_data in response")
                
        else:
            print(f"Error response: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

def test_stream_endpoint():
    """Test the streaming endpoint with requests"""
    url = "http://localhost:8000/api/v1/analyze-resume-stream"
    
    # Sample resume text
    resume_text = """John Doe
johndoe@email.com | (123) 456-7890 | San Francisco, CA

EXPERIENCE
Software Engineer at Tech Company
Jan 2020 - Present
• Developed and maintained web applications using React and Node.js

EDUCATION
B.S. Computer Science, University of California
2015 - 2019"""

    payload = {"resume_text": resume_text}
    headers = {"Content-Type": "application/json"}
    
    print("Testing streaming endpoint...")
    
    try:
        # Use stream=True to get response incrementally
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                # Process streamed response
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
                                    print(f"Received: {data.get('status')} - {data.get('message', '')}")
                                except json.JSONDecodeError:
                                    print(f"Invalid JSON: {data_json}")
            else:
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"Error: {e}")

def test_generate_questions():
    """Test the question generation endpoint"""
    url = "http://localhost:8000/api/v1/resume-questions"
    
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

    payload = {
        "resume_text": resume_text,
        "job_description": "Software Engineer position requiring React and Node.js experience",
        "num_questions": 3
    }
    
    headers = {"Content-Type": "application/json"}
    
    print("Testing /api/v1/resume-questions endpoint...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Success! Response received.")
            
            # Save response to file for inspection
            with open("debug_questions.json", "w") as f:
                json.dump(result, f, indent=2)
            print(f"Response saved to debug_questions.json")
            
            # Print questions
            if "questions" in result:
                questions = result["questions"]
                print(f"Generated {len(questions)} questions:")
                for i, q in enumerate(questions, 1):
                    print(f"{i}. {q.get('question')} [{q.get('difficulty')}]")
            else:
                print("No questions in response")
                
        else:
            print(f"Error response: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Check if API is running
    try:
        health_check = requests.get("http://localhost:8000/health")
        if health_check.status_code != 200:
            print("API is not running or health check failed")
            sys.exit(1)
    except:
        print("Can't connect to API. Make sure it's running on port 8000")
        sys.exit(1)
    
    # Run tests
    print("====== Starting API tests ======")
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1].lower()
        if test_name == "analyze":
            test_analyze_resume()
        elif test_name == "stream":
            test_stream_endpoint()
        elif test_name == "questions":
            test_generate_questions()
        else:
            print(f"Unknown test: {test_name}")
    else:
        # Run all tests
        test_analyze_resume()
        print("\n" + "="*40 + "\n")
        time.sleep(1)
        test_stream_endpoint()
        print("\n" + "="*40 + "\n")
        time.sleep(1)
        test_generate_questions()
    
    print("\n====== Tests completed ======")
