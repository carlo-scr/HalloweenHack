"""
Browser-Use FastAPI Backend Server

A REST API server for browser automation using browser-use.
Can be used with any frontend framework (React, Vue, etc.).

Usage:
    python browser_api_server.py
    
    Or with uvicorn:
    uvicorn browser_api_server:app --reload --host 0.0.0.0 --port 8000

Endpoints:
    GET  /              - API information
    GET  /health        - Health check
    POST /api/run-task  - Execute browser automation task
    GET  /api/examples  - Get example tasks
"""

import asyncio
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Import browser-use (local version)
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from browser_use import Agent, Browser, ChatBrowserUse

# Initialize FastAPI app
app = FastAPI(
    title="Browser-Use API",
    description="REST API for browser automation using browser-use",
    version="1.0.0"
)

# Configure CORS for frontend
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        frontend_url,
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class BrowserTask(BaseModel):
    """Browser automation task request."""
    task: str = Field(..., description="Natural language task description")
    max_steps: int = Field(default=10, ge=1, le=100, description="Maximum steps")
    use_vision: bool = Field(default=True, description="Use vision/screenshots")
    headless: bool = Field(default=False, description="Run browser headless")

class TaskResponse(BaseModel):
    """Task execution response."""
    success: bool
    message: str
    task: str
    steps_taken: Optional[int] = None
    final_result: Optional[str] = None
    urls_visited: Optional[list[str]] = None
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    browser_use_available: bool
    llm_configured: bool

# Helper function
def is_llm_configured() -> bool:
    """Check if at least one LLM API key is configured."""
    return any([
        os.getenv("BROWSER_USE_API_KEY"),
        os.getenv("OPENAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("GOOGLE_API_KEY"),
    ])

# API Endpoints
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Browser-Use API Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "run_task": "/api/run-task",
            "examples": "/api/examples",
            "docs": "/docs"
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        browser_use_available=True,
        llm_configured=is_llm_configured()
    )

@app.post("/api/run-task", response_model=TaskResponse)
async def run_browser_task(task_request: BrowserTask):
    """
    Execute a browser automation task.
    
    Args:
        task_request: Task configuration
        
    Returns:
        TaskResponse with execution results
    """
    
    # Validate LLM configured
    if not is_llm_configured():
        raise HTTPException(
            status_code=500,
            detail="No LLM API key configured. Set BROWSER_USE_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY"
        )
    
    try:
        # Initialize LLM (ChatBrowserUse is recommended)
        llm = ChatBrowserUse()
        
        # Alternative LLM options:
        # from browser_use import ChatOpenAI
        # llm = ChatOpenAI(model="gpt-4.1-mini")
        
        # from browser_use import ChatAnthropic
        # llm = ChatAnthropic(model="claude-sonnet-4-0")
        
        # from browser_use import ChatGoogle
        # llm = ChatGoogle(model="gemini-flash-latest")
        
        # Create browser
        browser = Browser(
            headless=task_request.headless or os.getenv("BROWSER_HEADLESS", "false").lower() == "true"
        )
        
        # Create agent
        agent = Agent(
            task=task_request.task,
            llm=llm,
            browser=browser,
            use_vision=task_request.use_vision,
        )
        
        # Run agent
        history = await agent.run(max_steps=task_request.max_steps)
        
        # Extract results
        final_result = history.final_result()
        urls_visited = history.urls()
        is_successful = history.is_successful()
        
        return TaskResponse(
            success=is_successful if is_successful is not None else True,
            message="Task completed successfully",
            task=task_request.task,
            steps_taken=history.number_of_steps(),
            final_result=str(final_result) if final_result else None,
            urls_visited=urls_visited,
        )
        
    except Exception as e:
        print(f"Error executing task: {str(e)}")
        
        return TaskResponse(
            success=False,
            message="Task execution failed",
            task=task_request.task,
            error=str(e)
        )

@app.get("/api/examples")
async def get_examples():
    """Get example tasks."""
    return {
        "examples": [
            {
                "name": "Search Hacker News",
                "task": "Go to Hacker News and find the top 3 posts",
                "max_steps": 5
            },
            {
                "name": "Search Google",
                "task": "Search Google for 'browser automation' and return the first result title",
                "max_steps": 5
            },
            {
                "name": "Extract Product Info",
                "task": "Go to https://example.com and extract the main heading",
                "max_steps": 3
            }
        ]
    }

# Main entry point
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print(f"🚀 Starting Browser-Use API Server on http://{host}:{port}")
    print(f"📚 API Documentation: http://localhost:{port}/docs")
    print(f"❤️  Health Check: http://localhost:{port}/health")
    
    uvicorn.run(
        "browser_api_server:app",
        host=host,
        port=port,
        reload=True
    )
