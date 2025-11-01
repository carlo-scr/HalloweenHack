# 🎯 Makefile Commands

Quick reference for the HalloweenHack project Makefile.

## 📋 Available Commands

```bash
make help          # Show all available commands
make install       # Install all dependencies (backend + frontend)
make setup         # Complete first-time setup
make start         # Start both backend and frontend
make start-backend # Start only the backend server
make start-frontend# Start only the frontend dev server
make stop          # Stop all running servers
make clean         # Clean temporary files and caches
make health        # Check if backend is healthy
make test          # Run a test browser automation task
make dev           # Alias for 'make start'
```

## 🚀 Quick Start

### First Time Setup
```bash
make setup
```

### Start Everything
```bash
make start
```

### Stop Everything
```bash
make stop
# Or press Ctrl+C if running in foreground
```

## 💡 Common Workflows

### Development
```bash
# Install dependencies
make install

# Start project
make start

# In another terminal, check health
make health

# Test automation
make test

# Stop when done
make stop
```

### Clean Start
```bash
# Stop everything
make stop

# Clean caches
make clean

# Start fresh
make start
```

### Separate Backend/Frontend
```bash
# Terminal 1: Backend only
make start-backend

# Terminal 2: Frontend only
make start-frontend
```

## 📍 Default Ports

- **Frontend**: http://localhost:8080
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Troubleshooting

### Port already in use
```bash
make stop
```

### Dependencies out of date
```bash
make install
```

### Clean everything
```bash
make clean
make install
```

## 📚 Full Documentation

See `START_HERE.md` for complete project documentation.
