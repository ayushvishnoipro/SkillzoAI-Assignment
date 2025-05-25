from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI) -> None:
    """Setup CORS for the application"""
    
    origins = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.1:5500",  # VS Code Live Server default
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "file://"  # Allow file:// protocol for local HTML files
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins temporarily for testing
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Type", "Content-Disposition"]
    )
