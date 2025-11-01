# 🎯 Quick Start - Browser-Use Integration

**Everything is now in your HalloweenHack project!**

## ⚡ Start in 2 Commands

```bash
# Terminal 1: Start backend
./start-backend.sh

# Terminal 2: Start React
cd swarm-bet-canvas-65985-main && npm run dev
```

---

## 📂 Project Structure (Updated)

```
HalloweenHack/
├── browser-use copy/              ← Python backend (MOVED HERE!)
│   ├── browser_api_server.py     ← FastAPI server
│   ├── .env                       ← API key configured ✅
│   └── .venv/                     ← Virtual environment
│
├── swarm-bet-canvas-65985-main/  ← React frontend
│   └── src/
│       ├── services/browserUseApi.ts
│       └── components/BrowserUseDemo.tsx
│
├── setup-backend.sh               ← One-time setup
├── start-backend.sh               ← Start server
├── QUICKSTART.md                  ← Full guide
└── BROWSER_USE_SETUP.md           ← Reference
```

---

## 🚀 First Time Setup

```bash
./setup-backend.sh
```

That's it! API key already configured.

---

## 🎨 Use in React

### Option 1: Demo Component
```typescript
import { BrowserUseDemo } from '@/components/BrowserUseDemo';

export default function Page() {
  return <BrowserUseDemo />;
}
```

### Option 2: Direct API Call
```typescript
import { runBrowserTask } from '@/services/browserUseApi';

const result = await runBrowserTask({
  task: "Go to Hacker News and get top post",
  max_steps: 10
});
```

---

## 🔗 Important Links

- **API Server**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health
- **React App**: http://localhost:5173

---

## 🧪 Quick Test

```bash
# Test backend
curl http://localhost:8000/health

# Run a task
curl -X POST http://localhost:8000/api/run-task \
  -H "Content-Type: application/json" \
  -d '{"task": "Go to example.com", "max_steps": 3}'
```

---

## 📍 All Paths (Updated!)

| What | Where |
|------|-------|
| Backend | `browser-use copy/browser_api_server.py` |
| .env | `browser-use copy/.env` |
| React | `swarm-bet-canvas-65985-main/` |
| Setup | `./setup-backend.sh` |
| Start | `./start-backend.sh` |

---

**Need help?** Check `QUICKSTART.md` or `BROWSER_USE_SETUP.md`
