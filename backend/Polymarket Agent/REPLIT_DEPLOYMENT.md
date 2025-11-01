# Deploying Decision Agent to Replit

This guide shows how to deploy the Polymarket decision agent to Replit for making betting decisions.

## Option 1: Deploy Script to Replit

### Step 1: Create a Replit Project

1. Go to [Replit](https://replit.com) and create a new Python project
2. Upload `polymarket_decision_example.py` to your Replit project
3. Create a `requirements.txt` file:

```
pydantic>=2.0.0
httpx>=0.28.0
python-dotenv>=1.0.0
```

### Step 2: Set Up Environment Variables

In Replit, go to **Secrets** (lock icon in sidebar) and add:

- `REPLIT_API_KEY` - Your Replit API key (optional if running on Replit)
- `PERPLEXITY_API_KEY` - Your Perplexity API key (if needed)

### Step 3: Create a Web Endpoint (Optional)

Create a `main.py` or `server.py` for HTTP access:

```python
from flask import Flask, request, jsonify
import asyncio
from polymarket_decision_example import analyze_market_for_betting, analyze_with_replit

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Endpoint to analyze Polymarket data."""
    data = request.json
    
    # Run analysis
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        decision = loop.run_until_complete(
            analyze_with_replit(data)
        )
        return jsonify(decision.model_dump())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Step 4: Run on Replit

1. Click **Run** button in Replit
2. Your script will be accessible via the Replit URL
3. Make POST requests to `/analyze` with Polymarket data

## Option 2: Use Replit API Directly

If Replit provides an API for code execution, you can call it from your local script:

```python
import httpx
import json

async def analyze_with_replit_api(market_data: dict):
    """Use Replit API to execute analysis code."""
    
    api_key = os.getenv('REPLIT_API_KEY')
    
    # Prepare the analysis code
    code = f"""
from polymarket_decision_example import analyze_market_for_betting
import json

data = {json.dumps(market_data)}
decision = analyze_market_for_betting(data)
print(json.dumps(decision.model_dump()))
"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.replit.com/v1/run',  # Adjust based on actual API
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'code': code,
                'language': 'python3',
            },
        )
        return response.json()
```

## Option 3: Replit Agent/Chat Integration

If Replit has an agent or chat API, you can use it like this:

```python
async def analyze_with_replit_agent(market_data: dict):
    """Use Replit agent/chat API for analysis."""
    
    api_key = os.getenv('REPLIT_API_KEY')
    
    prompt = f"""
Analyze this Polymarket market data and make a betting decision:

{json.dumps(market_data, indent=2)}

Provide a betting decision with reasoning.
"""
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://api.replit.com/v1/chat',  # Adjust based on actual API
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'model': 'replit-model',  # Adjust based on available models
            },
        )
        return response.json()
```

## Testing the Deployment

### Local Testing

```bash
# Test locally first
python polymarket_decision_example.py --input polymarket_data.json

# Test with Replit flag (will use local analysis if API not configured)
python polymarket_decision_example.py --replit --input polymarket_data.json
```

### Test via HTTP (if using Flask server)

```bash
curl -X POST http://your-replit-url.repl.co/analyze \
  -H "Content-Type: application/json" \
  -d @polymarket_data.json
```

## Environment Variables

Create a `.env` file or set in Replit Secrets:

```env
# Required for Perplexity integration (data collection)
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Optional for Replit API calls (if using Replit API)
REPLIT_API_KEY=your_replit_api_key_here

# Browser-Use API key (for data collection)
BROWSER_USE_API_KEY=your_browser_use_api_key_here
```

## Integration Workflow

1. **Data Collection** (runs locally or on server):
   ```bash
   python polymarket_collector.py --query "2024 US Election"
   ```
   - Collects data from Polymarket
   - Adds Perplexity research
   - Saves to `polymarket_data.json`

2. **Decision Making** (runs on Replit):
   ```bash
   # Option A: Run on Replit directly
   python polymarket_decision_example.py --replit
   
   # Option B: Call Replit API from your script
   # (implement based on Replit's actual API)
   
   # Option C: Deploy to Replit and call via HTTP
   curl -X POST http://your-replit-url.repl.co/analyze \
     -H "Content-Type: application/json" \
     -d @polymarket_data.json
   ```

## Notes

- Replit API endpoints may vary - check Replit's documentation for actual endpoints
- The current implementation includes a placeholder for Replit API integration
- You can customize the Replit integration based on Replit's actual API structure
- For production, deploy the decision agent to Replit and access it via HTTP

## Next Steps

1. Check Replit's API documentation for actual endpoints
2. Update `analyze_with_replit()` function with correct API calls
3. Deploy decision agent to Replit
4. Set up automated workflow: data collection → Replit decision → action

