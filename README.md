# 🎃 Agentic Syndicate — Polymarket Autonomous Trading - YC Halloween & Hyperspell Hackathon Winner

Agentic Syndicate is an integration of browser automation and an AI multi-agent trading advisor built to discover and analyze Polymarket markets and (optionally) execute trades. It includes:

- A FastAPI Python backend that runs agents and exposes API endpoints.
- A React + TypeScript frontend demo and dashboard.
- A multi-agent decision system (Data Collector, Odds Analyzer, Research, Sentiment) that produces weighted trade recommendations.
- Browser automation powered by Browser-Use for scraping and interaction.

This README gives a concise developer-oriented overview and quick start steps.

## Key features

- Market discovery: find trending and active Polymarket markets using browser automation.
- Multi-agent analysis: multiple specialized agents analyze markets and vote on recommendations.
- Autonomous trading: optional automated execution and portfolio tracking.
- Extensible: add new agents or integrate other data sources / LLMs.

## Quick start

1. Copy and configure environment variables:

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and set BROWSER_USE_API_KEY and any optional provider keys
```

2. Install dependencies and set up the project:

```bash
make setup
```

3. Start backend and frontend:

```bash
make start
```

4. Open the frontend at:

- UI: http://localhost:8080
- API docs (when backend running): http://localhost:8000/docs

## How it works (high level)

1. Discovery: the Data Collector agent uses Browser-Use to navigate Polymarket and extract candidate markets.
2. Analysis: each agent (Odds Analyzer, Research, Sentiment) evaluates the market and returns a vote + confidence.
3. Aggregation: Decision Coordinator weights votes and computes a final recommendation and suggested bet size.
4. Execution (optional): the trading agent executes trades against a connected account or simulation, and updates portfolio state.

## Agents

- Data Collector — scrapes markets, validates data quality and liquidity.
- Odds Analyzer — computes value estimates and expected edge.
- Research Agent — gathers supporting external context (news, events).
- Sentiment Agent — analyzes public opinion signals.
- Decision Coordinator — aggregates agents' outputs and produces final recommendation.

## API (examples)

Run a browser automation task (example):

```bash
curl -X POST http://localhost:8000/api/run-task \
	-H 'Content-Type: application/json' \
	-d '{"task":"Go to example.com and return the title","max_steps":5}'
```

Get a multi-agent market recommendation (example):

```bash
curl -X POST http://localhost:8000/api/decide \
	-H 'Content-Type: application/json' \
	-d '{"market_data": {"market_id": "trump-2024","yes_price": 0.54, "volume_24h": 125000}}'
```

Start autonomous trading (example):

```bash
curl -X POST http://localhost:8000/api/trading/start \
	-H 'Content-Type: application/json' \
	-d '{"markets":["Trump 2024"], "check_interval":300, "min_confidence":0.7}'
```

See `docs/API.md` for full endpoint documentation.

## Development

Backend (run API locally):

```bash
cd backend
source .venv/bin/activate
uvicorn browser_api_server:app --reload --port 8000
```

Frontend (run dev server):

```bash
cd webpage
npm install
npm run dev
```

## Environment & secrets

- Copy `backend/.env.example` to `backend/.env` and set `BROWSER_USE_API_KEY` (required) plus any optional LLM API keys.
- Never commit `.env` or secrets to source control.

## Tests

Run integration tests:

```bash
make test
```

## Contributing

Please read `CONTRIBUTING.md` for contribution guidelines, coding style and PR workflow.

## Notes and safety

- This project can execute trades. Use `dry-run` or sandbox modes for testing before connecting real funds.
- Be mindful of external API rate limits and the legal/regulatory rules for automated trading in your jurisdiction.

## License

MIT — see `LICENSE`.

---

If you'd like, I can:

- Add a short architecture diagram or ASCII flow to the README.
- Add sample unit tests and a CI job to run them.
- Add a safety switch (DRY_RUN env var) and a small script to validate required env vars before starting the backend.

Tell me which of those you'd like next.
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

Environment
-----------

Copy the example env file and add your API keys and configuration:

```bash
cp backend/.env.example backend/.env
# then edit backend/.env and add your BROWSER_USE_API_KEY and any other keys
```

License
-------

MIT — see `LICENSE`.

If you want a shorter or more detailed README, tell me which sections to expand or trim.
│   │   ├── components/            # React components
