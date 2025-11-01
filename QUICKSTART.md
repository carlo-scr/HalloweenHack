# 🚀 Browser-Use Integration Quick Start

Complete setup guide for integrating browser-use into your React project using the existing **browser-use copy**.

> **TL;DR**: Run `./setup-backend.sh` then `./start-backend.sh` - API key already configured!

## Project Structure

```
HalloweenHack/
├── webpage/                         # Your React frontend
│   └── src/
│       ├── services/
│       │   └── browserUseApi.ts     # ✅ Created - API client
│       └── components/
│           └── BrowserUseDemo.tsx   # ✅ Created - Example component
│
└── browser-use copy/                # ✅ Browser-use with backend (MOVED HERE!)
    ├── browser_api_server.py        # ✅ Created - FastAPI server
    ├── requirements.txt             # Python dependencies (updated)
    ├── .env                         # Already configured!
    └── browser_use/                 # Browser-use library
```

## Step 1: Set Up Python Backend

### 1.1 Navigate to Browser-Use Directory

```bash
cd "browser-use copy"
```

### 1.2 Install Missing Dependencies

```bash
# Activate existing virtual environment (if it exists)
source .venv/bin/activate

# Or create a new one if needed
# python3 -m venv .venv
# source .venv/bin/activate

# Install FastAPI and uvicorn (already has browser-use)
pip install fastapi uvicorn[standard]

# Make sure browser-use is installed in development mode
pip install -e .
```

### 1.3 Check Environment Configuration

Your `.env` file is already configured! Just verify it has:

```bash
cat .env
```

Should show:
```env
BROWSER_USE_API_KEY=bu_3ul9VldaYW2rvJ2yVwifUGtFqFIDkHhUOYDbRvEzh0A
```

(Optional) Add these for more control:
```env
BROWSER_HEADLESS=false
FRONTEND_URL=http://localhost:5173
```

### 1.4 Start the Backend

```bash
python browser_api_server.py
```

You should see:
```
🚀 Starting Browser-Use API Server on http://0.0.0.0:8000
📚 API Documentation: http://localhost:8000/docs
❤️  Health Check: http://localhost:8000/health
```

✅ **Test it**: Visit http://localhost:8000/health

---

## Step 2: Use in React Frontend

### Option A: Use the Demo Component (Quickest)

1. Import the demo component in any page:

```typescript
// In src/pages/Index.tsx or any component
import { BrowserUseDemo } from '@/components/BrowserUseDemo';

export default function Index() {
  return (
    <div>
      <BrowserUseDemo />
    </div>
  );
}
```

2. Start your React dev server:

```bash
# From browser-use directory, navigate to your React app
cd ../webpage
npm run dev
```

### Option B: Build Your Own Integration

Use the API service directly:

```typescript
import { runBrowserTask } from '@/services/browserUseApi';

// In your component
const handleAutomation = async () => {
  const result = await runBrowserTask({
    task: "Go to Hacker News and get the top post",
    max_steps: 10,
    headless: false
  });
  
  console.log('Result:', result.final_result);
  console.log('URLs visited:', result.urls_visited);
};
```

---

## Step 3: Test the Integration

### Test from React UI

1. Open http://localhost:5173 (your React app)
2. Find the BrowserUseDemo component
3. Try an example task: "Go to Hacker News and find the top post"
4. Click "Run Browser Task"
5. Watch the browser automation happen!

### Test from Command Line

```bash
# Test health endpoint
curl http://localhost:8000/health

# Run a task
curl -X POST http://localhost:8000/api/run-task \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Go to example.com and extract the heading",
    "max_steps": 5,
    "headless": false
  }'
```

---

## 🎯 Example Tasks You Can Run

```typescript
// Search and extract data
await runBrowserTask({
  task: "Search Google for 'browser automation' and return first 3 titles"
});

// Navigate and interact
await runBrowserTask({
  task: "Go to Hacker News, find the top post, and return its title and URL"
});

// Complex workflows
await runBrowserTask({
  task: "Go to GitHub, search for 'browser-use', and return the star count"
});
```

---

## 📁 Files Created/Updated

### Backend Files (in browser-use copy)
- ✅ `browser_api_server.py` - NEW FastAPI server with endpoints
- ✅ `requirements.txt` - UPDATED with FastAPI/uvicorn
- ✅ `.env` - ALREADY CONFIGURED with API key!

### Frontend Files (in swarm-bet-canvas-65985-main)
- ✅ `src/services/browserUseApi.ts` - TypeScript API client
- ✅ `src/components/BrowserUseDemo.tsx` - Example React component

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Make sure you're in the browser-use copy directory
cd "browser-use copy"

# Activate virtual environment
source .venv/bin/activate

# Check dependencies installed
pip list | grep -E "browser-use|fastapi|uvicorn"
```

### CORS errors
Make sure `.env` has the correct `FRONTEND_URL`:
```env
FRONTEND_URL=http://localhost:5173
```

### "Backend Offline" in React
1. Check backend is running: http://localhost:8000/health
2. Check CORS configuration in `main.py`
3. Check browser console for errors

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Then restart backend
python browser_api_server.py
```

---

## 🚀 Next Steps

### Production Deployment

1. **Use sandboxes** (recommended for production):
```python
from browser_use import sandbox, ChatBrowserUse

@sandbox(cloud_profile_id='your-profile-id')
async def production_task(browser):
    # Your automation code
    pass
```

2. **Or deploy backend + frontend separately**:
   - Backend: Deploy to Railway, Render, or AWS
   - Frontend: Deploy to Vercel, Netlify, or Cloudflare Pages
   - Update `VITE_BROWSER_USE_API_URL` in React to point to production backend

### Add Authentication

Add API key validation to your FastAPI endpoints:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("INTERNAL_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")
```

### Monitor Usage

Track your browser-use API usage at:
https://cloud.browser-use.com/dashboard

---

## 📚 Resources

- **Browser-Use Docs**: https://docs.browser-use.com
- **Your API Key**: Already configured in `.env`!
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Backend Location**: `browser-use copy/` (in your project root)

---

## 💡 Tips

1. **Start with `headless: false`** to see what's happening
2. **Use lower `max_steps`** (5-10) for faster testing
3. **Check `/docs`** endpoint for interactive API testing
4. **Monitor browser console** for API errors
5. **Read backend logs** for debugging task execution

---

## ✅ Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Backend health check passes
- [ ] `.env` file configured with API key
- [ ] React app running on http://localhost:5173
- [ ] Demo component renders without errors
- [ ] Can successfully run a test task

---

Need help? Check the detailed README in `browser-use-backend/README.md` or visit https://docs.browser-use.com
