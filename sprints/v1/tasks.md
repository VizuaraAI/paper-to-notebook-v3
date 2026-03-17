# Sprint v1 — Tasks

## Task List

- [x] Task 1: Project setup — backend and frontend scaffolding (P0)
  - Acceptance: Python venv with FastAPI, PyMuPDF, arxiv, google-genai installed; Vite+React+Tailwind frontend bootstrapped; both run without errors
  - Files: `backend/main.py`, `backend/requirements.txt`, `frontend/` (Vite scaffold), `frontend/vite.config.js`
  - Completed: 2026-03-17 — Venv created with all deps, FastAPI health endpoint, React+Vite+Tailwind v4 scaffolded, both build/test green

- [x] Task 2: PDF text extraction module (P0)
  - Acceptance: `extract_text(file_bytes) -> str` function that takes PDF bytes and returns cleaned text; tested with a sample PDF; handles multi-page documents
  - Files: `backend/pdf_extractor.py`, `tests/test_pdf_extractor.py`
  - Completed: 2026-03-17 — PyMuPDF-based extractor with 4 passing tests (single page, multi page, empty, invalid)

- [x] Task 3: ArXiv paper fetcher module (P0)
  - Acceptance: `fetch_arxiv_pdf(url_or_id) -> bytes` function that accepts an arXiv URL (e.g., `https://arxiv.org/abs/2401.12345`) or bare ID, downloads the PDF, and returns raw bytes; tested with a real arXiv ID
  - Files: `backend/arxiv_fetcher.py`, `tests/test_arxiv_fetcher.py`
  - Completed: 2026-03-17 — URL/ID parser + PDF fetcher with 6 passing tests including real arXiv download

- [x] Task 4: Gemini prompt template for notebook generation (P0)
  - Acceptance: A prompt template string that instructs Gemini to generate a notebook following the canonical 8-section structure (Opening, Init, Context, Data Prep, Eval Framework, Reference Impl, Algorithm Impl, Conclusions); returns valid JSON notebook format; prompt stored as a constant
  - Files: `backend/prompt_template.py`, `tests/test_prompt_template.py`
  - Completed: 2026-03-17 — Detailed prompt template with 8 sections, ipynb JSON format spec, Colab metadata, 5 passing tests

- [x] Task 5: Notebook generator module — Gemini API integration (P0)
  - Acceptance: `generate_notebook(paper_text: str, api_key: str) -> dict` function that sends extracted text + prompt to Gemini, parses the response into valid `.ipynb` JSON structure; includes error handling for API failures
  - Files: `backend/notebook_generator.py`, `tests/test_notebook_generator.py`
  - Completed: 2026-03-17 — Gemini integration with JSON extraction, notebook validation, Colab metadata. 6 passing tests

- [x] Task 6: FastAPI endpoints — `/api/upload-pdf` and `/api/arxiv-url` (P0)
  - Acceptance: POST `/api/upload-pdf` accepts multipart file + `X-Api-Key` header, returns `.ipynb` JSON; POST `/api/arxiv-url` accepts JSON body `{url: "..."}` + `X-Api-Key` header, returns `.ipynb` JSON; both return proper error codes (400, 422, 500)
  - Files: `backend/main.py`, `tests/test_api.py`
  - Completed: 2026-03-17 — Both endpoints with validation, error handling, mocked Gemini calls. 7 passing tests

- [x] Task 7: Frontend — API key input and PDF upload form (P0)
  - Acceptance: React page with: Gemini API key text input (masked), file upload button for PDF, text input for arXiv URL, "Generate Notebook" button; form validates that API key is provided and either a file or URL is given
  - Files: `frontend/src/App.jsx`, `frontend/tests/app.spec.js`
  - Completed: 2026-03-17 — Clean form UI with Tailwind, validation, masked API key. 4 Playwright E2E tests passing

- [x] Task 8: Frontend — API integration and notebook download (P0)
  - Acceptance: Clicking "Generate" sends request to backend with correct headers/body; shows loading spinner during generation; on success, triggers `.ipynb` file download; on error, displays error message to user
  - Files: `frontend/src/App.jsx`, `frontend/tests/app.spec.js`
  - Completed: 2026-03-17 — fetch calls to both endpoints, loading spinner, error display, .ipynb download. 7 Playwright tests passing

- [x] Task 9: End-to-end integration testing and polish (P1)
  - Acceptance: Full flow works: upload PDF → get notebook, paste arXiv URL → get notebook; notebook opens in Google Colab without errors; error states handled gracefully (bad API key, invalid PDF, network errors)
  - Files: `tests/test_integration.py`, `.gitignore`
  - Completed: 2026-03-17 — 4 integration tests (full pipelines, CORS, error propagation), .gitignore added. 33 backend + 7 frontend = 40 total tests passing

- [ ] Task 10: Notebook quality refinement — improve prompt and output (P1)
  - Acceptance: Generated notebooks have clear markdown explanations between code cells; code cells are individually runnable; includes pip installs in first cell; includes proper Colab metadata in `.ipynb` structure
  - Files: `backend/prompt_template.py`, `backend/notebook_generator.py`
