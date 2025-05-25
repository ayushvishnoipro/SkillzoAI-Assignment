# Testing the Resume Analysis API with Swagger UI

This guide explains how to use the Swagger UI to test the Resume Analysis API endpoints.

## Accessing Swagger UI

1. First, make sure the API server is running:
   ```
   python -m app.main
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:8000/docs
   ```

   This will load the Swagger UI interface showing all available endpoints.

## Testing the API Endpoints

### 1. Analyze Resume Endpoint

This endpoint processes a resume and returns structured data with insights.

1. Click on the `/api/v1/analyze-resume` endpoint to expand it
2. Click the "Try it out" button
3. In the request body, you'll see a pre-filled example with a sample resume text. You can keep this or replace it with your own resume text.
4. Click "Execute" to send the request
5. The API will process the resume (this may take 15-30 seconds)
6. When complete, you'll see the response with:
   - HTTP status code (should be 200 for success)
   - Response body containing structured resume data and insights

### 2. Generate Interview Questions Endpoint

This endpoint generates custom interview questions based on a resume.

1. Click on the `/api/v1/resume-questions` endpoint to expand it
2. Click the "Try it out" button
3. In the request body, you'll see:
   - `resume_text`: The resume content (pre-filled with an example)
   - `job_description`: Optional job description to tailor questions (you can add your own)
   - `num_questions`: Number of questions to generate (default is 5)
4. Click "Execute" to send the request
5. The API will generate questions (this may take 10-20 seconds)
6. When complete, you'll see the response with:
   - HTTP status code (should be 200 for success)
   - Response body containing the generated questions and an overview

### 3. Streaming Resume Analysis Endpoint

This endpoint shows progress as the resume is analyzed.

1. Click on the `/api/v1/analyze-resume-stream` endpoint to expand it
2. Click the "Try it out" button
3. In the request body, provide the resume text (an example is pre-filled)
4. Click "Execute" to send the request
5. Unlike the other endpoints, this one returns a stream of updates
6. In the response section, you'll see:
   - HTTP status code (should be 200 for success)
   - The raw server response showing progress updates

**Note**: Swagger UI doesn't render Server-Sent Events (SSE) in a user-friendly way. You'll see the raw event data. To properly view the stream, you might want to implement a simple web client that consumes the stream.

## Sample Resumes for Testing

For convenience, here are sample resumes you can use for testing:

### Software Developer Resume
```
John Smith
john.smith@email.com | (555) 123-4567 | San Francisco, CA | linkedin.com/in/johnsmith

SUMMARY
Software developer with 5 years of experience creating web applications with JavaScript, React, and Node.js. Passionate about clean code and user experience.

EXPERIENCE
Senior Software Developer | TechCorp Inc.
June 2020 - Present
• Developed a React-based dashboard that increased user engagement by 35%
• Led a team of 3 developers to rebuild the company's main product
• Implemented CI/CD pipeline reducing deployment time by 50%

Software Developer | WebSolutions LLC
March 2018 - May 2020
• Built RESTful APIs using Node.js and Express
• Maintained and enhanced legacy PHP applications
• Collaborated with design team to implement responsive UI components

EDUCATION
B.S. Computer Science | University of California, Berkeley
2014 - 2018 | GPA: 3.8

SKILLS
Programming: JavaScript, TypeScript, Python, PHP
Frontend: React, Redux, HTML5, CSS3, SASS
Backend: Node.js, Express, REST APIs, GraphQL
Database: MongoDB, PostgreSQL, MySQL
DevOps: Docker, AWS, GitHub Actions, Jenkins
```

### Data Scientist Resume
```
Sarah Johnson
sarah.j@email.com | (555) 987-6543 | New York, NY

SUMMARY
Data scientist with 4+ years of experience applying statistical modeling and machine learning to solve business problems. Expertise in Python, SQL, and data visualization.

EXPERIENCE
Senior Data Scientist | DataInsights Corp
January 2021 - Present
• Built predictive models that increased marketing ROI by 25%
• Created a customer segmentation system using clustering algorithms
• Developed NLP models to analyze customer feedback across 100K+ reviews

Data Analyst | Analytics Partners
July 2018 - December 2020
• Designed dashboards for executive team using Tableau
• Performed A/B testing on website features
• Extracted and cleaned data from various sources using SQL and Python

EDUCATION
M.S. Data Science | New York University
2016 - 2018

B.A. Mathematics | Cornell University
2012 - 2016 | GPA: 3.9

SKILLS
Programming: Python, R, SQL
Machine Learning: Scikit-learn, TensorFlow, PyTorch
Data Processing: Pandas, NumPy, PySpark
Visualization: Tableau, PowerBI, Matplotlib, Seaborn
Big Data: Hadoop, Spark, AWS EMR
```

## Troubleshooting

If you encounter any issues while testing:

1. Check the API server logs for detailed error messages
2. Ensure your OpenAI API key in the `.env` file is valid
3. For large resumes, the processing might take longer than expected
4. If you get a 500 error, it might be due to rate limiting from the LLM provider

## Next Steps

After testing with Swagger UI, you might want to:

1. Integrate the API with your frontend application
2. Create custom API clients for specific use cases
3. Implement authentication for production use
