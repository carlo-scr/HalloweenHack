# 🧪 Backend Verification Guide

## Quick Verification Commands

### 1. Check if servers are running
```bash
# Check backend (port 8000)
curl http://localhost:8000/health

# Check frontend (port 8080)
curl http://localhost:8080
```

### 2. Test the backend API
```bash
# Health check
make health

# Quick API test
python3 quick_test.py

# Full test suite
make test
```

### 3. Manual browser task test
```bash
curl -X POST http://localhost:8000/api/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Go to example.com and tell me the page title",
    "max_steps": 3,
    "headless": true
  }' | python3 -m json.tool
```

## Test Results Reference

### ✅ Successful Response
```json
{
  "success": true,
  "message": "Task completed successfully",
  "task": "Go to example.com",
  "steps_taken": 2,
  "final_result": "The page title is: Example Domain",
  "urls_visited": ["https://example.com"],
  "error": null
}
```

### ❌ Error Response
```json
{
  "success": false,
  "message": "Task execution failed",
  "task": "...",
  "error": "Error message here"
}
```

## Example Tasks to Test

### 1. Simple Navigation
```json
{
  "task": "Go to example.com",
  "max_steps": 2,
  "headless": true
}
```

### 2. Search Task
```json
{
  "task": "Go to Hacker News and find the top post title",
  "max_steps": 5,
  "headless": false
}
```

### 3. Data Extraction
```json
{
  "task": "Go to github.com/trending and get the name of the first repository",
  "max_steps": 5,
  "headless": true
}
```

## Verification Checklist

- [ ] Backend runs without errors: `make start-backend`
- [ ] Health endpoint responds: `curl localhost:8000/health`
- [ ] API docs accessible: Open http://localhost:8000/docs
- [ ] Simple task completes: Run `python3 quick_test.py`
- [ ] Frontend connects: Open http://localhost:8080
- [ ] Full test passes: `make test`

## Common Issues

### Issue: "Internal Server Error"
**Solution:** Check backend logs, ensure `.env` has `BROWSER_USE_API_KEY`

### Issue: "Connection refused"
**Solution:** Backend not running, run `make start-backend`

### Issue: "LLM not configured"
**Solution:** Add API key to `backend/.env`:
```bash
BROWSER_USE_API_KEY=bu_your_key_here
```

### Issue: Browser automation fails
**Solution:** 
1. Try with `headless: false` to see what's happening
2. Reduce `max_steps` to debug faster
3. Check task is clear and specific

## Monitoring

### View Backend Logs
```bash
# If running in background
tail -f /tmp/backend.log

# If running with make start
# Logs appear in terminal
```

### Check Running Processes
```bash
# See what's on port 8000
lsof -i :8000

# See what's on port 8080
lsof -i :8080
```

### Stop Everything
```bash
make stop
```

## Advanced Testing

### Test with Python Script
```python
import asyncio
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from browser_use import Agent, Browser
from browser_use.llm.browser_use.chat import ChatBrowserUse

async def test_agent():
    llm = ChatBrowserUse()
    browser = Browser(headless=True)
    agent = Agent(
        task="Go to example.com",
        llm=llm,
        browser=browser
    )
    
    history = await agent.run(max_steps=3)
    print(f"Result: {history.final_result()}")

asyncio.run(test_agent())
```

### Test from React Frontend
1. Open http://localhost:8080
2. Enter task: "Go to example.com"
3. Click "Run Task"
4. Check results appear

## Success Indicators

✅ Backend responds to health check  
✅ API returns 200 status for tasks  
✅ Browser automation completes tasks  
✅ Frontend can communicate with backend  
✅ No errors in logs  

## Next Steps After Verification

1. Try more complex tasks
2. Integrate into your React app
3. Build custom automation workflows
4. Monitor API usage and costs
