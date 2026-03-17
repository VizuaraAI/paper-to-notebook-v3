# Paper to Notebook

AI-powered tool that converts research paper PDFs into runnable Google Colab Jupyter notebooks.

## Project Overview
- Users upload a PDF or paste an arXiv URL
- The app extracts text, sends it to Gemini, and generates a structured .ipynb notebook
- Notebooks include implementations, explanations, visualizations, and are Colab-ready
- ArXiv integration via MCP server (Model Context Protocol)

## Tech Stack
- **Backend**: Python, FastAPI, PyMuPDF (text extraction), Gemini API (notebook generation)
- **Frontend**: React + Vite + Tailwind CSS
- **MCP**: ArXiv MCP server (`arxiv-mcp-server`) for fetching papers by URL/ID
- **API Key**: Gemini API key entered by the user in the frontend (sent via `X-Api-Key` header)

## Sprint Workflow
This project follows a sprint-based development process:
- `/prd v1` — Define requirements, create PRD and atomic tasks
- `/dev v1` — Implement tasks one at a time using TDD
- `/walkthrough v1` — Generate sprint review report

Sprint artifacts live in `sprints/vN/` (prd.md, tasks.md, walkthrough.md).

## Project Structure
```
paper-to-notebook/
├── sprints/           ← Sprint artifacts (PRD, tasks, walkthrough)
├── backend/           ← FastAPI server
│   ├── main.py        ← API endpoints
│   ├── pdf_extractor.py
│   ├── notebook_generator.py
│   └── mcp_clients.py ← ArXiv MCP client
├── frontend/          ← React + Vite app
│   └── src/
│       ├── App.jsx
│       └── main.jsx
├── tests/             ← Test suite
└── CLAUDE.md          ← This file
```

## Key Technical Decisions
- Gemini (free tier) instead of Claude API for notebook generation
- ArXiv MCP server via Python `mcp` SDK (stdio transport)
- MCP Activity Log in the frontend for transparency (polls `/api/mcp/activity`)
- API key passed from frontend via header (no server-side .env required)

## MCP Integration Notes
- ArXiv MCP server binary lives at `venv/bin/arxiv-mcp-server` — always use the full path
- MCP client uses `mcp` Python SDK with `StdioServerParameters`
- The `mcp` package requires Python 3.10+ — use `python3.12` for the venv
- Activity log: every MCP tool call is logged with timestamp, server, tool, params, timing
- Frontend polls `/api/mcp/activity?since_id=0` every 1 second (full log, not incremental)

## Commands
```bash
# Backend
cd backend && ../venv/bin/python -m uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Tests
cd backend && ../venv/bin/python -m pytest
cd frontend && npx vitest run
```
