# 🎃 HalloweenHack# 🎃 HalloweenHack - AI-Powered Browser Automation & Trading System# 🎃 HalloweenHack



AI-powered browser automation + autonomous trading.



This repository bundles:A full-stack application combining AI-powered browser automation with autonomous trading capabilities, featuring a React frontend and FastAPI backend powered by Browser-Use.Browser automation project with React frontend and Browser-Use Python backend.



- Frontend: `webpage/` (React + TypeScript)

- Backend: `backend/` (FastAPI + Browser-Use)

- Docs: `docs/` (API & system guides)## 📋 Table of Contents## 🚀 Quick Start



Quick start

-----------

- [Features](#-features)```bash

Install and run the project locally (recommended):

- [Quick Start](#-quick-start)# First time setup

```bash

make setup- [Project Structure](#-project-structure)make setup

make start

```- [Tech Stack](#️-tech-stack)



Open the UI at http://localhost:8080 and API docs at http://localhost:8000/docs- [API Documentation](#-api-documentation)# Start the project



Common commands- [Development](#-development)make start

---------------

- [Testing](#-testing)```

```bash

make help          # list available commands- [Contributing](#-contributing)

make setup         # install deps

make start         # start backend + frontend- [License](#-license)Then open: **http://localhost:8080**

make start-backend # start backend only

make start-frontend# start frontend only

make test          # run tests

make clean         # clean build artifacts## ✨ Features## 📋 Available Commands

```



Layout

------### 🌐 Browser Automation```bash



```- AI-powered browser automation using Browser-Usemake help          # Show all commands

HalloweenHack/

├── backend/    # Python backend and agents- Natural language task executionmake start         # Start backend + frontend

├── webpage/    # React frontend

├── docs/       # Documentation and API reference- Vision-enabled browsing with screenshot analysismake stop          # Stop all servers

├── scripts/    # Helper shell scripts

├── Makefile- Headless and headed browser modesmake health        # Check backend health

└── README.md

```make test          # Run test automation



Docs & contribution### 🤖 Multi-Agent Trading Systemmake clean         # Clean caches

-------------------

- **Data Collector Agent** - Validates market data quality and liquidity```

See `docs/` for API and system guides. Read `CONTRIBUTING.md` for development and PR guidance.

- **Odds Analyzer Agent** - Identifies value bets and market inefficiencies

License

-------- **Research Agent** - Gathers news and contextual information## 📚 Documentation



MIT — see `LICENSE`.- **Sentiment Agent** - Analyzes social media sentiment



If you want a shorter or more detailed README, tell me which sections to expand or trim.- **Decision Coordinator** - Aggregates agent recommendations using weighted voting- **Getting Started**: See `START_HERE.md`


- **Makefile Help**: See `MAKEFILE_HELP.md`

### 💼 Autonomous Trading- **Browser-Use Guide**: See `QUICKSTART.md`

- Continuous market monitoring

- Automated trade execution## 🌐 URLs

- Real-time portfolio tracking

- Risk management with configurable limits- **React App**: http://localhost:8080

- **API Server**: http://localhost:8000

### 🎨 Modern Web Interface- **API Docs**: http://localhost:8000/docs

- React + TypeScript frontend

- Real-time updates with live agent status## 🛠️ Tech Stack

- Portfolio dashboard with P&L tracking

# 🎃 HalloweenHack

AI-powered browser automation + autonomous trading.

This repository bundles:

- Frontend: `webpage/` (React + TypeScript)
- Backend: `backend/` (FastAPI + Browser-Use)
- Docs: `docs/` (API & system guides)

Quick start
-----------

Install and run the project locally (recommended):

```bash
make setup
make start
```

Open the UI at http://localhost:8080 and API docs at http://localhost:8000/docs

Common commands
---------------

```bash
make help          # list available commands
make setup         # install deps
make start         # start backend + frontend
make start-backend # start backend only
make start-frontend# start frontend only
make test          # run tests
make clean         # clean build artifacts
```

Layout
------

```
HalloweenHack/
├── backend/    # Python backend and agents
├── webpage/    # React frontend
├── docs/       # Documentation and API reference
├── scripts/    # Helper shell scripts
├── Makefile
└── README.md
```

Docs & contribution
-------------------

See `docs/` for API and system guides. Read `CONTRIBUTING.md` for development and PR guidance.

License
-------

MIT — see `LICENSE`.

If you want a shorter or more detailed README, tell me which sections to expand or trim.
│   │   ├── components/            # React components
