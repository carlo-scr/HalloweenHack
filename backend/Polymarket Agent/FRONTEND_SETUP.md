# Frontend Integration Guide

This guide shows how to connect the Polymarket API server to your frontend.

## Quick Start

### 1. Start the API Server

```bash
# Install Flask if not already installed
pip install flask flask-cors

# Start the server
python api_server.py
```

The server will start on `http://localhost:5000`

### 2. Use the Example Frontend

Open `frontend_example.html` in your browser. It provides a complete UI for:
- Collecting market data
- Making decisions
- Viewing history
- Updating outcomes

### 3. API Endpoints

All endpoints are available at `http://localhost:5000/api/*`

## API Endpoints

### 1. Health Check
```javascript
GET /api/health

// Response
{
  "status": "ok",
  "service": "Polymarket API Server",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 2. Collect Market Data
```javascript
POST /api/collect

// Request
{
  "market_identifier": "2024 US Presidential Election",
  "method": "search",  // "search", "url", or "id"
  "headless": true
}

// Response
{
  "success": true,
  "data": { /* market data */ },
  "message": "Market data collected successfully"
}
```

### 3. Make Decision
```javascript
POST /api/decide

// Request
{
  "market_id": "market-123",  // Optional, uses latest if not provided
  "use_replit": false,
  "market_data": { /* optional, provide market data directly */ }
}

// Response
{
  "success": true,
  "decision": { /* decision data */ },
  "market_data": { /* market data */ },
  "message": "Decision made successfully"
}
```

### 4. Collect and Decide (All-in-One)
```javascript
POST /api/collect-and-decide

// Request
{
  "market_identifier": "2024 US Presidential Election",
  "method": "search",
  "use_replit": false,
  "headless": true
}

// Response
{
  "success": true,
  "market": { /* market data */ },
  "decision": { /* decision data */ },
  "message": "Market data collected and decision made successfully"
}
```

### 5. Get All Markets
```javascript
GET /api/markets?limit=10&category=Politics

// Response
{
  "success": true,
  "markets": [ /* array of markets */ ],
  "count": 10
}
```

### 6. Get All Decisions
```javascript
GET /api/decisions?limit=10&market_id=market-123

// Response
{
  "success": true,
  "decisions": [ /* array of decisions */ ],
  "count": 10
}
```

### 7. Update Decision Outcome
```javascript
POST /api/outcome

// Request
{
  "decision_id": "market-123",
  "was_correct": true,
  "actual_outcome": "Option A won",
  "actual_return": 25.5
}

// Response
{
  "success": true,
  "message": "Outcome updated in Hyperspell"
}
```

## Frontend Integration Examples

### React Example

```jsx
import React, { useState } from 'react';

function PolymarketAgent() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const collectAndDecide = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/collect-and-decide', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          market_identifier: query,
          method: 'search',
          headless: true,
        }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter market query"
      />
      <button onClick={collectAndDecide} disabled={loading}>
        {loading ? 'Processing...' : 'Collect & Decide'}
      </button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}
```

### Vue.js Example

```vue
<template>
  <div>
    <input v-model="query" placeholder="Enter market query" />
    <button @click="collectAndDecide" :disabled="loading">
      {{ loading ? 'Processing...' : 'Collect & Decide' }}
    </button>
    <pre v-if="result">{{ JSON.stringify(result, null, 2) }}</pre>
  </div>
</template>

<script>
export default {
  data() {
    return {
      query: '',
      loading: false,
      result: null,
    };
  },
  methods: {
    async collectAndDecide() {
      this.loading = true;
      try {
        const response = await fetch('http://localhost:5000/api/collect-and-decide', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            market_identifier: this.query,
            method: 'search',
            headless: true,
          }),
        });
        this.result = await response.json();
      } catch (error) {
        this.result = { error: error.message };
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
```

### Next.js Example

```typescript
// pages/api/polymarket/collect.ts
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const response = await fetch('http://localhost:5000/api/collect-and-decide', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });
    
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}

// Component
import { useState } from 'react';

export default function PolymarketAgent() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const res = await fetch('/api/polymarket/collect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        market_identifier: query,
        method: 'search',
      }),
    });
    
    const data = await res.json();
    setResult(data);
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter market query"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Processing...' : 'Collect & Decide'}
      </button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </form>
  );
}
```

### Vanilla JavaScript (Fetch API)

```javascript
// Collect and decide
async function collectAndDecide(marketQuery) {
  const response = await fetch('http://localhost:5000/api/collect-and-decide', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      market_identifier: marketQuery,
      method: 'search',
      headless: true,
    }),
  });
  
  const data = await response.json();
  return data;
}

// Get all markets
async function getMarkets() {
  const response = await fetch('http://localhost:5000/api/markets?limit=10');
  const data = await response.json();
  return data.markets;
}

// Get all decisions
async function getDecisions() {
  const response = await fetch('http://localhost:5000/api/decisions?limit=10');
  const data = await response.json();
  return data.decisions;
}

// Update outcome
async function updateOutcome(decisionId, wasCorrect, actualOutcome, actualReturn) {
  const response = await fetch('http://localhost:5000/api/outcome', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      decision_id: decisionId,
      was_correct: wasCorrect,
      actual_outcome: actualOutcome,
      actual_return: actualReturn,
    }),
  });
  
  const data = await response.json();
  return data;
}
```

## CORS Configuration

The API server includes CORS by default, so frontends on different origins can access it. If you need to restrict origins, modify `api_server.py`:

```python
from flask_cors import CORS

# Allow specific origins
CORS(app, origins=["http://localhost:3000", "https://yourdomain.com"])

# Or allow all (default)
CORS(app)
```

## Error Handling

All endpoints return a consistent error format:

```json
{
  "success": false,
  "error": "Error message here"
}
```

Always check the `success` field before using the response data.

## Production Deployment

### 1. Use Production WSGI Server

```bash
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

### 2. Environment Variables

Set in production:
```bash
export BROWSER_USE_API_KEY=your_key
export PERPLEXITY_API_KEY=your_key
export HYPERSPELL_API_KEY=your_key
export REPLIT_API_KEY=your_key  # Optional
```

### 3. Database Integration

Replace in-memory storage with a database (PostgreSQL, MongoDB, etc.):

```python
# Example with SQLite
import sqlite3

def init_db():
    conn = sqlite3.connect('polymarket.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS markets (
            id TEXT PRIMARY KEY,
            data TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
```

## Security Considerations

1. **API Keys**: Never expose API keys in frontend code
2. **Authentication**: Add authentication for production use
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Validation**: Validate all inputs on the server side
5. **HTTPS**: Use HTTPS in production

## Example: Full Workflow

```javascript
// Complete workflow example
async function fullWorkflow(marketQuery) {
  // 1. Collect and decide
  const result = await collectAndDecide(marketQuery);
  
  if (result.success) {
    console.log('Market:', result.market);
    console.log('Decision:', result.decision);
    
    // 2. Later, when market resolves, update outcome
    const outcome = await updateOutcome(
      result.decision.market_id,
      true,  // was correct
      'Option A won',
      25.5   // 25.5% return
    );
    
    console.log('Outcome updated:', outcome);
  }
}
```

## Next Steps

1. Customize the frontend to match your design
2. Add real-time updates (WebSockets)
3. Add charts and visualizations
4. Implement user authentication
5. Add database persistence

