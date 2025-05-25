from fastapi import FastAPI, HTTPException
import uvicorn
import os
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import pathlib

from app.api.v1 import endpoints
from app.core.config import settings
from app.core.cors import setup_cors
from app.utils.logger import app_logger

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API for analyzing resumes and generating insights and interview questions",
    docs_url="/docs",  # Standard Swagger UI path
    redoc_url="/redoc",  # ReDoc path
)

# Setup CORS middleware
setup_cors(app)

# Include API routers
app.include_router(endpoints.router, prefix="/api/v1", tags=["resume-analysis"])

# Mount static files for UI if the folder exists
ui_path = pathlib.Path("ui")
if ui_path.exists() and ui_path.is_dir():
    app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")
    app_logger.info("UI files mounted at /ui")

@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "documentation": "/docs",
        "ui": "/ui" if ui_path.exists() and ui_path.is_dir() else None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_status": "operational"
    }

# Custom OpenAPI to add examples
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API for analyzing resumes and generating insights and interview questions. Use the Swagger UI to test the API endpoints.",
        routes=app.routes,
    )
    
    # Add example for resume analysis
    if "paths" in openapi_schema and "/api/v1/analyze-resume" in openapi_schema["paths"]:
        openapi_schema["paths"]["/api/v1/analyze-resume"]["post"]["requestBody"]["content"]["application/json"]["example"] = {
            "resume_text": "John Doe\njohndoe@email.com | (123) 456-7890 | San Francisco, CA\n\nEXPERIENCE\nSoftware Engineer at Tech Company\nJan 2020 - Present\n• Developed and maintained web applications using React and Node.js\n• Collaborated with cross-functional teams to deliver high-quality products\n\nEDUCATION\nB.S. Computer Science, University of California\n2015 - 2019 | GPA: 3.8\n\nSKILLS\nJavaScript, Python, React, Node.js, SQL, AWS"
        }
    
    # Add example for streaming analysis
    if "paths" in openapi_schema and "/api/v1/analyze-resume-stream" in openapi_schema["paths"]:
        openapi_schema["paths"]["/api/v1/analyze-resume-stream"]["post"]["requestBody"]["content"]["application/json"]["example"] = {
            "resume_text": "John Doe\njohndoe@email.com | (123) 456-7890 | San Francisco, CA\n\nEXPERIENCE\nSoftware Engineer at Tech Company\nJan 2020 - Present\n• Developed and maintained web applications using React and Node.js\n• Collaborated with cross-functional teams to deliver high-quality products\n\nEDUCATION\nB.S. Computer Science, University of California\n2015 - 2019 | GPA: 3.8\n\nSKILLS\nJavaScript, Python, React, Node.js, SQL, AWS"
        }
    
    # Add example for question generation
    if "paths" in openapi_schema and "/api/v1/resume-questions" in openapi_schema["paths"]:
        openapi_schema["paths"]["/api/v1/resume-questions"]["post"]["requestBody"]["content"]["application/json"]["example"] = {
            "resume_text": "John Doe\njohndoe@email.com | (123) 456-7890 | San Francisco, CA\n\nEXPERIENCE\nSoftware Engineer at Tech Company\nJan 2020 - Present\n• Developed and maintained web applications using React and Node.js\n• Collaborated with cross-functional teams to deliver high-quality products\n\nEDUCATION\nB.S. Computer Science, University of California\n2015 - 2019 | GPA: 3.8\n\nSKILLS\nJavaScript, Python, React, Node.js, SQL, AWS",
            "job_description": "We are looking for a Full Stack Developer with experience in React and Node.js. The ideal candidate will have experience with AWS cloud services and database design.",
            "num_questions": 3
        }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    app_logger.error(f"Unhandled exception: {exc}")
    return HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    # Start the API server when script is run directly
    port = int(os.getenv("PORT", 8000))
    app_logger.info(f"Starting {settings.APP_NAME} on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
