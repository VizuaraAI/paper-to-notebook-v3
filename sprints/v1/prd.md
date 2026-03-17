# Sprint v1 — PRD: Paper-to-Notebook MVP

## Sprint Overview
Build a fully functional local tool that takes a research paper (PDF upload or arXiv URL) and generates a detailed, runnable Google Colab notebook. The notebook follows a canonical 8-section pedagogical template covering context, data prep, implementation, experiments, and analysis. No deployment, no MCP, no visualizations in the notebook — just a clean, working pipeline.

## Goals
- User can upload a PDF and receive a downloadable `.ipynb` notebook
- User can paste an arXiv URL and the system fetches + processes the paper
- Generated notebooks follow the canonical 8-section template (no visualization section)
- Notebooks are Colab-ready (installs, GPU checks, seeds, runnable cells)
- Minimal but functional React frontend (upload/URL input → download notebook)
- Gemini API key entered by user in the frontend (no server-side secrets)

## User Stories
1. As a researcher, I want to upload a PDF of a paper so that I get a runnable notebook that implements the paper's key ideas.
2. As a researcher, I want to paste an arXiv URL so that the system fetches the paper and generates a notebook without me downloading the PDF manually.
3. As a user, I want to enter my own Gemini API key so that I don't need server-side configuration.
4. As a user, I want to download the generated `.ipynb` file so I can open it directly in Google Colab.

## Technical Architecture

### Tech Stack
- **Backend**: Python 3.12, FastAPI, PyMuPDF (PDF text extraction), `arxiv` Python package (arXiv fetching), Google Gemini API (notebook generation)
- **Frontend**: React + Vite + Tailwind CSS
- **No database** — stateless request/response

### Component Diagram
```
┌─────────────────────────────────────┐
│           React Frontend            │
│  ┌───────────┐  ┌────────────────┐  │
│  │ PDF Upload │  │ ArXiv URL Input│  │
│  └─────┬─────┘  └───────┬────────┘  │
│        └────────┬────────┘           │
│           API Key Input              │
│          [Generate Button]           │
│          [Download .ipynb]           │
└────────────────┬────────────────────┘
                 │ HTTP POST
                 ▼
┌─────────────────────────────────────┐
│           FastAPI Backend           │
│                                     │
│  /api/upload-pdf    /api/arxiv-url  │
│        │                  │         │
│        ▼                  ▼         │
│  ┌───────────┐   ┌──────────────┐  │
│  │PyMuPDF    │   │arxiv package │  │
│  │extract txt│   │fetch + extract│  │
│  └─────┬─────┘   └──────┬───────┘  │
│        └────────┬────────┘          │
│                 ▼                   │
│  ┌──────────────────────────────┐   │
│  │  Gemini API (notebook gen)   │   │
│  │  Prompt: canonical template  │   │
│  └──────────────┬───────────────┘   │
│                 ▼                   │
│         Return .ipynb JSON          │
└─────────────────────────────────────┘
```

### Data Flow
1. User uploads PDF → backend extracts text with PyMuPDF
2. OR user pastes arXiv URL → backend downloads PDF via `arxiv` package → extracts text
3. Extracted text + canonical template prompt → sent to Gemini API
4. Gemini returns structured notebook content → backend assembles `.ipynb` JSON
5. Frontend receives `.ipynb` → triggers download

### Canonical Notebook Template (7 sections, no visualizations)
1. **Opening** — Paper title, citation, what this notebook teaches
2. **Initialization** — Imports, seed setting, environment check
3. **Context** — What task are we solving? Why it matters
4. **Data Preparation** — Synthetic data generation, print examples
5. **Evaluation Framework** — Define reward/loss function, demonstrate scoring
6. **Reference Implementation** — Simple baseline method, run on 1 example
7. **Algorithm Implementation** — One algorithm per cell, verbose execution, step-by-step prints
8. **Conclusions** — What we learned, why it works, how to extend

## Out of Scope (v1)
- MCP integration (ArXiv MCP server) — deferred to v2
- Visualization cells in generated notebooks — deferred to v2
- Deployment (Docker, cloud hosting) — deferred to v2+
- MCP activity log in frontend
- User authentication or API key storage
- Notebook editing in the browser
- Multiple paper processing / batch mode
- Progress streaming / SSE (simple request-response for now)

## Dependencies
- Google Gemini API (free tier) — user provides their own key
- PyMuPDF (`pymupdf`) — PDF text extraction
- `arxiv` Python package — arXiv paper fetching
- Node.js / npm — frontend tooling
