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
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Import browser-use (local version)
import sys
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

try:
    from browser_use import Agent, Browser
    from browser_use.llm.browser_use.chat import ChatBrowserUse
except ImportError as e:
    print(f"Error importing browser_use: {e}")
    print(f"Python path: {sys.path}")
    raise

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
        "http://localhost:8080",  # Add port 8080 for Vite
        "http://localhost:8081",
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
            },
            {
                "name": "Polymarket - Top Markets",
                "task": "Go to Polymarket.com and get the top 3 trending markets with their current prices",
                "max_steps": 8
            }
        ]
    }

@app.post("/api/polymarket/collect")
async def collect_polymarket_data(
    market_url: str = None,
    market_id: str = None,
    search_query: str = None
):
    """
    Collect data from a Polymarket market.
    
    Args:
        market_url: Full URL to the market (e.g., https://polymarket.com/event/...)
        market_id: Market ID (e.g., "will-trump-win-2024")
        search_query: Search query to find a market
        
    Returns:
        Structured market data including prices, volume, outcomes, etc.
    """
    try:
        # Import the Polymarket collector
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Polymarket Agent"))
        from polymarket_collector import collect_market_data
        
        # Determine method and identifier
        if market_url:
            method = 'url'
            identifier = market_url
        elif market_id:
            method = 'id'
            identifier = market_id
        elif search_query:
            method = 'search'
            identifier = search_query
        else:
            raise HTTPException(
                status_code=400,
                detail="Must provide market_url, market_id, or search_query"
            )
        
        # Collect the data
        market_data = await collect_market_data(
            market_identifier=identifier,
            method=method,
            headless=True
        )
        
        # Return as dict
        return market_data.dict()
        
    except Exception as e:
        print(f"Error collecting Polymarket data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect market data: {str(e)}"
        )

@app.get("/api/polymarket/trending")
async def get_trending_polymarket():
    """
    Get trending Polymarket markets.
    
    Returns:
        List of trending markets with basic info
    """
    try:
        # Use browser-use to scrape trending markets
        llm = ChatBrowserUse()
        browser = Browser(headless=True)
        
        agent = Agent(
            task="""Go to https://polymarket.com and extract the top 5 trending markets.
            
For each market, extract:
- Title/question
- Current prices for each outcome
- Total volume
- URL to the market

Return the data as a JSON array.""",
            llm=llm,
            browser=browser,
            use_vision=True
        )
        
        history = await agent.run(max_steps=8)
        result = history.final_result()
        
        # Try to parse as JSON
        try:
            import json
            markets = json.loads(str(result))
            return {"markets": markets, "success": True}
        except:
            return {"markets": [], "raw_result": str(result), "success": False}
            
    except Exception as e:
        print(f"Error getting trending markets: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trending markets: {str(e)}"
        )

@app.post("/api/polymarket/analyze")
async def analyze_market_with_agents(request: dict):
    """
    Multi-agent analysis of a Polymarket market.
    
    Uses multiple AI agents to analyze the market and provide
    a collective trading recommendation.
    
    Args:
        request: JSON body with either market_query or market_url
        
    Returns:
        Collective decision from all agents with recommendation
    """
    try:
        from multi_agent_decision import DecisionCoordinator
        
        market_query = request.get("market_query")
        market_url = request.get("market_url")
        
        if not market_query and not market_url:
            raise HTTPException(
                status_code=400,
                detail="Must provide market_query or market_url"
            )
        
        identifier = market_query or market_url
        
        # Run multi-agent analysis
        coordinator = DecisionCoordinator()
        decision = await coordinator.make_decision(identifier)
        
        return decision.dict()
        
    except Exception as e:
        print(f"Error in multi-agent analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent analysis failed: {str(e)}"
        )


# ==================== AUTONOMOUS TRADING ENDPOINTS ====================

# Global agent instance
autonomous_agent = None

class AgentConfig(BaseModel):
    """Configuration for autonomous trading agent."""
    markets: list[str] = Field(default=["Trump 2024", "Bitcoin $100k by 2025"])
    check_interval: int = Field(default=300, description="Seconds between checks")
    min_confidence: float = Field(default=0.7, ge=0, le=1)
    min_consensus: float = Field(default=0.6, ge=0, le=1)
    max_position_size: float = Field(default=500.0, gt=0)


@app.post("/api/trading/start")
async def start_autonomous_trading(config: AgentConfig = None):
    """
    Start the autonomous trading agent.
    
    The agent will:
    1. Monitor specified markets
    2. Use multi-agent analysis
    3. Execute trades autonomously
    4. Update portfolio in real-time
    """
    global autonomous_agent
    
    if autonomous_agent and autonomous_agent.running:
        return {
            "success": False,
            "message": "Agent already running",
            "status": "running"
        }
    
    try:
        from autonomous_trading_agent import AutonomousTradingAgent
        
        if config is None:
            config = AgentConfig()
        
        # Create agent
        autonomous_agent = AutonomousTradingAgent(
            markets_to_monitor=config.markets,
            check_interval=config.check_interval,
            min_confidence=config.min_confidence,
            min_consensus=config.min_consensus,
            max_position_size=config.max_position_size,
        )
        
        # Start in background
        asyncio.create_task(autonomous_agent.start())
        
        # Give it a moment to start
        await asyncio.sleep(1)
        
        return {
            "success": True,
            "message": "Autonomous trading agent started",
            "status": "running",
            "config": config.dict(),
            "portfolio": autonomous_agent.portfolio.dict()
        }
        
    except Exception as e:
        print(f"Error starting agent: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start agent: {str(e)}"
        )


@app.post("/api/trading/stop")
async def stop_autonomous_trading():
    """Stop the autonomous trading agent."""
    global autonomous_agent
    
    if not autonomous_agent or not autonomous_agent.running:
        return {
            "success": False,
            "message": "Agent not running",
            "status": "stopped"
        }
    
    try:
        autonomous_agent.stop()
        
        return {
            "success": True,
            "message": "Autonomous trading agent stopped",
            "status": "stopped",
            "final_portfolio": autonomous_agent.portfolio.dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop agent: {str(e)}"
        )


@app.get("/api/trading/status")
async def get_trading_status():
    """Get current status of autonomous trading agent."""
    global autonomous_agent
    
    if not autonomous_agent:
        return {
            "running": False,
            "message": "Agent not initialized"
        }
    
    return {
        "running": autonomous_agent.running,
        "portfolio": autonomous_agent.portfolio.dict(),
        "markets_monitored": autonomous_agent.markets_to_monitor,
        "config": {
            "check_interval": autonomous_agent.check_interval,
            "min_confidence": autonomous_agent.min_confidence,
            "min_consensus": autonomous_agent.min_consensus,
            "max_position_size": autonomous_agent.max_position_size,
        }
    }


@app.get("/api/portfolio")
async def get_portfolio():
    """Get current portfolio state."""
    global autonomous_agent
    
    if not autonomous_agent:
        # Load from disk
        from pathlib import Path
        import json
        
        portfolio_path = Path("data/portfolio.json")
        if portfolio_path.exists():
            return json.loads(portfolio_path.read_text())
        else:
            return {
                "total_value": 10000.0,
                "cash": 10000.0,
                "active_positions": [],
                "closed_positions": [],
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "total_trades": 0,
                "winning_trades": 0,
                "last_updated": datetime.now().isoformat()
            }
    
    return autonomous_agent.portfolio.dict()


@app.get("/api/portfolio/positions")
async def get_active_positions():
    """Get active trading positions."""
    global autonomous_agent
    
    if not autonomous_agent:
        from pathlib import Path
        import json
        
        portfolio_path = Path("data/portfolio.json")
        if portfolio_path.exists():
            portfolio = json.loads(portfolio_path.read_text())
            return {"positions": portfolio.get("active_positions", [])}
        return {"positions": []}
    
    return {"positions": autonomous_agent.portfolio.active_positions}


@app.get("/api/portfolio/history")
async def get_trade_history():
    """Get complete trade history."""
    from pathlib import Path
    import json
    
    history_path = Path("data/trades_history.json")
    if history_path.exists():
        return {"trades": json.loads(history_path.read_text())}
    
    return {"trades": []}


@app.post("/api/portfolio/close/{trade_id}")
async def close_position(trade_id: str, final_price: float, resolved_outcome: str):
    """
    Manually close a position (for testing/demo).
    
    In production, this would be triggered by market resolution.
    """
    global autonomous_agent
    
    if not autonomous_agent:
        raise HTTPException(
            status_code=400,
            detail="Agent not running"
        )
    
    try:
        autonomous_agent.portfolio.close_trade(trade_id, final_price, resolved_outcome)
        autonomous_agent._save_portfolio()
        
        return {
            "success": True,
            "message": "Position closed",
            "portfolio": autonomous_agent.portfolio.dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to close position: {str(e)}"
        )


# Main entry point
if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
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
