# 📡 API Reference

Complete API documentation for the HalloweenHack backend.

## Base URL

- Development: `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

Currently, the API does not require authentication. API keys are configured server-side in the `.env` file.

## Endpoints

### Health & Status

#### GET /health

Check if the API is healthy and running.

**Response:**
```json
{
  "status": "ok",
  "service": "Browser-Use API Server",
  "timestamp": "2025-11-02T10:30:00Z"
}
```

**Status Codes:**
- `200` - API is healthy

---

### Browser Automation

#### POST /api/run-task

Execute a browser automation task using natural language.

**Request Body:**
```typescript
{
  task: string;           // Natural language task description
  max_steps?: number;     // Maximum steps (default: 10)
  headless?: boolean;     // Run in headless mode (default: true)
  use_vision?: boolean;   // Enable screenshot analysis (default: true)
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Go to example.com and get the page title",
    "max_steps": 5,
    "headless": true,
    "use_vision": true
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Task completed successfully",
  "steps_taken": 3,
  "final_result": "Example Domain",
  "urls_visited": ["https://example.com"],
  "execution_time": 12.5
}
```

**Status Codes:**
- `200` - Task completed successfully
- `400` - Invalid request parameters
- `500` - Server error during task execution

---

### Trading System

#### POST /api/trading/start

Start the autonomous trading agent.

**Request Body:**
```json
{
  "markets": ["Market identifier 1", "Market identifier 2"],
  "check_interval": 300,      // Seconds between checks (default: 300)
  "min_confidence": 0.7,      // Minimum confidence level (0-1)
  "min_consensus": 0.6,       // Minimum agent consensus (0-1)
  "max_position_size": 500    // Maximum USD per position
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/trading/start \
  -H "Content-Type: application/json" \
  -d '{
    "markets": ["Trump 2024", "Bitcoin $100k"],
    "check_interval": 300,
    "min_confidence": 0.7,
    "min_consensus": 0.6,
    "max_position_size": 500
  }'
```

**Response:**
```json
{
  "status": "started",
  "agent_id": "trading_agent_001",
  "config": {
    "markets": ["Trump 2024", "Bitcoin $100k"],
    "check_interval": 300,
    "min_confidence": 0.7,
    "min_consensus": 0.6,
    "max_position_size": 500
  },
  "message": "Autonomous trading agent started successfully"
}
```

**Status Codes:**
- `200` - Agent started successfully
- `400` - Invalid configuration
- `409` - Agent already running

---

#### POST /api/trading/stop

Stop the autonomous trading agent.

**Response:**
```json
{
  "status": "stopped",
  "message": "Autonomous trading agent stopped",
  "final_stats": {
    "total_trades": 15,
    "winning_trades": 9,
    "total_pnl": 234.50
  }
}
```

**Status Codes:**
- `200` - Agent stopped successfully
- `404` - No agent running

---

#### GET /api/trading/status

Get the current status of the autonomous trading agent.

**Response:**
```json
{
  "is_running": true,
  "agent_id": "trading_agent_001",
  "uptime_seconds": 3600,
  "last_check": "2025-11-02T10:25:00Z",
  "next_check": "2025-11-02T10:30:00Z",
  "recent_activity": [
    {
      "timestamp": "2025-11-02T10:20:00Z",
      "action": "analyzed_market",
      "market": "Trump 2024",
      "result": "no_action"
    }
  ]
}
```

**Status Codes:**
- `200` - Status retrieved successfully

---

#### GET /api/portfolio

Get the current portfolio status.

**Response:**
```json
{
  "total_value": 10234.50,
  "cash_available": 5000.00,
  "positions_value": 5234.50,
  "total_pnl": 234.50,
  "total_pnl_percent": 2.34,
  "positions": [
    {
      "market_id": "trump-2024",
      "market_name": "Trump 2024 Election",
      "side": "YES",
      "shares": 100,
      "avg_price": 0.52,
      "current_price": 0.54,
      "value": 54.00,
      "pnl": 2.00,
      "pnl_percent": 3.85
    }
  ],
  "win_rate": 0.60,
  "total_trades": 15,
  "winning_trades": 9
}
```

**Status Codes:**
- `200` - Portfolio retrieved successfully

---

### Market Data & Analysis

#### POST /api/collect

Collect market data from Polymarket.

**Request Body:**
```json
{
  "market_identifier": "Trump 2024",
  "method": "search",    // "search" | "url" | "id"
  "headless": true
}
```

**Response:**
```json
{
  "success": true,
  "market_data": {
    "market_id": "trump-2024-election",
    "title": "Trump to win 2024 Presidential Election",
    "yes_price": 0.54,
    "no_price": 0.46,
    "volume_24h": 125000,
    "liquidity": 500000,
    "last_updated": "2025-11-02T10:30:00Z"
  }
}
```

**Status Codes:**
- `200` - Data collected successfully
- `400` - Invalid market identifier
- `404` - Market not found
- `500` - Collection error

---

#### POST /api/decide

Get multi-agent trading recommendation.

**Request Body:**
```json
{
  "market_data": {
    "market_id": "trump-2024",
    "title": "Trump 2024",
    "yes_price": 0.54,
    "no_price": 0.46,
    "volume_24h": 125000
  },
  "use_research": false,      // Optional: Include research agent
  "use_sentiment": false      // Optional: Include sentiment agent
}
```

**Response:**
```json
{
  "final_recommendation": "YES",
  "aggregate_confidence": 0.72,
  "consensus_level": 0.85,
  "suggested_bet_size": 8.5,
  "agent_decisions": [
    {
      "agent_name": "Data Collector",
      "confidence": 0.8,
      "recommendation": "YES",
      "reasoning": "High liquidity and volume",
      "key_factors": ["Volume: $125k", "Liquidity: $500k"]
    },
    {
      "agent_name": "Odds Analyzer",
      "confidence": 0.75,
      "recommendation": "YES",
      "reasoning": "Value bet detected",
      "key_factors": ["Undervalued by 10%", "Low margin"]
    }
  ],
  "risk_assessment": {
    "level": "medium",
    "factors": ["Market volatility", "Volume adequate"]
  }
}
```

**Status Codes:**
- `200` - Analysis completed
- `400` - Invalid market data

---

#### GET /api/decisions

Get all stored trading decisions.

**Response:**
```json
{
  "decisions": [
    {
      "id": "decision_001",
      "timestamp": "2025-11-02T10:30:00Z",
      "market_id": "trump-2024",
      "recommendation": "YES",
      "confidence": 0.72,
      "executed": true,
      "outcome": "pending"
    }
  ],
  "total": 42
}
```

---

#### GET /api/markets

Get all collected market data.

**Response:**
```json
{
  "markets": [
    {
      "market_id": "trump-2024",
      "title": "Trump 2024",
      "collected_at": "2025-11-02T10:30:00Z",
      "yes_price": 0.54,
      "no_price": 0.46
    }
  ],
  "total": 25
}
```

---

#### POST /api/outcome

Update the outcome of a trading decision.

**Request Body:**
```json
{
  "decision_id": "decision_001",
  "outcome": "win",        // "win" | "loss" | "pending"
  "pnl": 15.50,
  "notes": "Market moved as expected"
}
```

**Response:**
```json
{
  "success": true,
  "decision_id": "decision_001",
  "updated_outcome": "win",
  "updated_stats": {
    "total_wins": 10,
    "total_losses": 5,
    "win_rate": 0.67
  }
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error description",
  "detail": "Detailed error message",
  "status_code": 400
}
```

### Common Error Codes

- `400` - Bad Request: Invalid input parameters
- `404` - Not Found: Resource not found
- `409` - Conflict: Operation conflicts with current state
- `500` - Internal Server Error: Server-side error
- `503` - Service Unavailable: Service temporarily unavailable

---

## Rate Limiting

Currently, there are no rate limits. However, be mindful of:
- Browser automation tasks can be resource-intensive
- Market data collection may be limited by external APIs
- Autonomous trading checks are throttled by `check_interval`

---

## WebSocket Support

WebSocket support for real-time updates is planned but not yet implemented.

---

## SDK & Client Libraries

### TypeScript/JavaScript

See `webpage/src/services/browserUseApi.ts` for a complete TypeScript client implementation.

**Example Usage:**
```typescript
import { runBrowserTask, checkHealth } from '@/services/browserUseApi';

// Check health
const health = await checkHealth();

// Run task
const result = await runBrowserTask({
  task: "Go to example.com",
  max_steps: 5,
  headless: true
});
```

### Python

```python
import httpx
import asyncio

async def run_task(task: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/run-task",
            json={"task": task, "max_steps": 10}
        )
        return response.json()

# Usage
result = asyncio.run(run_task("Go to example.com"))
```

---

## Examples

### Example 1: Simple Browser Task
```bash
curl -X POST http://localhost:8000/api/run-task \
  -H "Content-Type: application/json" \
  -d '{"task": "Search Google for browser automation", "max_steps": 5}'
```

### Example 2: Market Analysis
```bash
# Collect market data
curl -X POST http://localhost:8000/api/collect \
  -H "Content-Type: application/json" \
  -d '{"market_identifier": "Trump 2024", "method": "search"}'

# Get trading recommendation
curl -X POST http://localhost:8000/api/decide \
  -H "Content-Type: application/json" \
  -d '{
    "market_data": {
      "market_id": "trump-2024",
      "yes_price": 0.54,
      "volume_24h": 125000
    }
  }'
```

### Example 3: Start Autonomous Trading
```bash
curl -X POST http://localhost:8000/api/trading/start \
  -H "Content-Type: application/json" \
  -d '{
    "markets": ["Trump 2024"],
    "check_interval": 300,
    "min_confidence": 0.7
  }'
```

---

For interactive API documentation, visit **http://localhost:8000/docs** when the server is running.
