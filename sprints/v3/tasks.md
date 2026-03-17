# Sprint v3 — Tasks: Testing, CI/CD & Deployment

## Task List

### Testing Pyramid

- [x] Task 1: Add unit tests for pdf_extractor and arxiv_fetcher edge cases (P0)
  - Acceptance: `test_pdf_extractor.py` has tests for: huge text extraction, special characters/unicode in PDF, multi-page concatenation order, whitespace normalization. `test_arxiv_fetcher.py` has tests for: versioned IDs (v1, v2, v3), whitespace-padded input, HTTP error responses (404, 500), connection timeout handling. Total new unit tests: ≥8. All pass.
  - Files: `tests/test_pdf_extractor.py`, `tests/test_arxiv_fetcher.py`
  - Completed: 2026-03-17 — 5 new pdf_extractor tests (unicode, order, whitespace, large, many pages) + 4 new arxiv tests (versioned IDs, whitespace, 404, timeout). 60 total backend tests pass.

- [x] Task 2: Add unit tests for prompt_template and notebook_generator edge cases (P0)
  - Acceptance: `test_prompt_template.py` has tests for: very long paper text (100K chars), special characters in paper text (LaTeX, curly braces), empty paper text. `test_notebook_generator.py` has tests for: notebook with no code cells (only markdown), notebook with mixed source types (string vs list), `_scan_code_cells` with multiple dangerous patterns in one cell, `_extract_json` with malformed JSON. Total new unit tests: ≥8. All pass.
  - Files: `tests/test_prompt_template.py`, `tests/test_notebook_generator.py`
  - Completed: 2026-03-17 — 4 new prompt_template tests + 5 new notebook_generator tests. 29 tests in those files, all pass.

- [x] Task 3: Add integration tests for full API pipeline with mocked Gemini (P0)
  - Acceptance: `tests/test_integration.py` has tests for: full PDF upload → extract → generate pipeline (Gemini mocked); full arXiv URL → fetch → extract → generate pipeline (both arXiv fetch and Gemini mocked); concurrent requests don't interfere; large PDF with text truncation flows through correctly; rate limiter resets between test cases. Total new integration tests: ≥6. All pass.
  - Files: `tests/test_integration.py`
  - Completed: 2026-03-17 — 6 new integration tests (pipeline, arxiv mocked, truncation, empty PDF, invalid URL, independence). 10 total integration tests pass.

- [x] Task 4: Add E2E Playwright tests for UI flows with mocked API (P0)
  - Acceptance: New E2E tests in `frontend/tests/app.spec.js` covering: (1) PDF upload flow with file chooser (mocked API); (2) error handling flow — server returns 500, shows error message; (3) safety notice visible and confirmation dialog works; (4) form resets after successful generation. Screenshots at each step saved to `frontend/tests/screenshots/`. These tests run in CI (no API key needed). Total new E2E tests: ≥4. All pass.
  - Files: `frontend/tests/app.spec.js`, `frontend/tests/screenshots/`
  - Completed: 2026-03-17 — 4 new E2E tests (PDF upload, server error, form reset, loading spinner). Fixed existing download test missing dialog handler. 14/14 pass.

- [x] Task 5: Real E2E quality test — live Gemini call with notebook validation (P0)
  - Acceptance: New test file `frontend/tests/quality.spec.js` with a single test: (1) opens browser in **headed mode** (visible); (2) fills arXiv URL with `https://arxiv.org/abs/1706.03762` (Attention Is All You Need); (3) **waits for the user to manually type their Gemini API key** (test pauses with a 120-second timeout on the API key field becoming non-empty); (4) clicks Generate; (5) takes screenshots: before submit, during loading spinner, after completion; (6) intercepts the download, saves the `.ipynb` to `frontend/tests/output/`; (7) validates the notebook: valid JSON with `nbformat: 4`, has `cells` array, has 20+ cells, contains all 8 section keywords (Opening/Introduction, Initialization/Setup, Context/Problem, Data, Evaluation, Baseline/Reference, Algorithm/Implementation, Conclusion), code cells parse as valid Python (`child_process.execSync('python3 -c "import ast; ast.parse(...)"`), no empty source arrays, first cell is safety disclaimer. Test is in a separate file so it can be run independently: `npx playwright test tests/quality.spec.js --headed`. NOT run in CI. Playwright config updated to exclude `quality.spec.js` from default test runs.
  - Files: `frontend/tests/quality.spec.js`, `frontend/playwright.config.js`, `frontend/tests/output/`
  - Completed: 2026-03-17 — quality.spec.js with 9 validations (JSON, nbformat, cell count, sections, Python syntax, safety disclaimer, etc.). Excluded from default runs via testIgnore in playwright config.

### CI/CD Pipeline

- [x] Task 6: Initialize GitHub repository and push codebase (P0)
  - Acceptance: GitHub repo created via `gh repo create`; all code pushed to `main` branch; `.gitignore` updated to exclude `venv/`, `node_modules/`, `__pycache__/`, `.env`, `*.pyc`; `git remote -v` shows the GitHub remote; `gh repo view` works
  - Files: `.gitignore`
  - Completed: 2026-03-17 — Repo at https://github.com/VizuaraAI/paper-to-notebook, all code pushed to main

- [x] Task 7: Create GitHub Actions CI pipeline (P0)
  - Acceptance: `.github/workflows/ci.yml` runs on push and PR to main. Three parallel jobs: (1) `backend-tests` — sets up Python 3.12, installs requirements, runs `pytest tests/ -v`; (2) `e2e-tests` — sets up Node 20, installs deps + Playwright browsers, starts backend + frontend, runs `npx playwright test`, uploads screenshots as artifacts; (3) `security` — runs `semgrep --config auto backend/` and `pip-audit`. All jobs must pass. Workflow validated with `actionlint` or manual review.
  - Files: `.github/workflows/ci.yml`
  - Completed: 2026-03-17 — 3 parallel jobs: backend-tests (pytest), e2e-tests (Playwright + screenshots artifact), security (semgrep + pip-audit)

- [ ] Task 8: Verify CI pipeline runs green on GitHub (P0)
  - Acceptance: Push a commit that triggers the CI pipeline; verify all 3 jobs pass on GitHub Actions; download Playwright screenshot artifacts from the Actions run; if any job fails, fix the issue and re-push until green
  - Files: `.github/workflows/ci.yml` (if fixes needed)

### Docker & Infrastructure

- [x] Task 9: Create Dockerfiles for backend and frontend (P1)
  - Acceptance: `backend/Dockerfile` — Python 3.12-slim base, installs requirements, copies backend code, runs uvicorn on port 8000, non-root user. `frontend/Dockerfile` — Node 20-alpine base, multi-stage build (install → build → serve with nginx), serves on port 80. Both images build successfully with `docker build`. Images are reasonably sized (<500MB backend, <100MB frontend).
  - Files: `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`
  - Completed: 2026-03-17 — Backend (Python 3.12-slim, non-root user), Frontend (multi-stage Node+nginx), nginx.conf with API proxy, .dockerignore files

- [x] Task 10: Create docker-compose.yml for local development (P1)
  - Acceptance: `docker-compose.yml` at project root defines two services: `backend` (builds from `backend/Dockerfile`, port 8000, healthcheck on `/api/health`) and `frontend` (builds from `frontend/Dockerfile`, port 5173→80, depends_on backend). `docker compose up --build` starts both services; frontend can reach backend at `http://backend:8000`; `docker compose down` stops cleanly. Includes `.dockerignore` files.
  - Files: `docker-compose.yml`, `backend/.dockerignore`, `frontend/.dockerignore`
  - Completed: 2026-03-17 — docker-compose.yml with backend (healthcheck on /api/health) + frontend (depends_on backend healthy), nginx proxies /api/ to backend

- [x] Task 11: Create Terraform config for AWS ECS Fargate deployment (P2)
  - Acceptance: `infra/main.tf` defines: VPC with public/private subnets, ECR repositories for backend and frontend images, ECS cluster with Fargate, two ECS services (backend + frontend) with task definitions, ALB routing `/api/*` to backend and `/*` to frontend, security groups (ALB public, ECS private). `infra/variables.tf` for configurable values (region, instance count). `infra/outputs.tf` outputs the ALB DNS name. Config validates with `terraform validate` (or is syntactically correct if Terraform CLI not installed).
  - Files: `infra/main.tf`, `infra/variables.tf`, `infra/outputs.tf`
  - Completed: 2026-03-17 — VPC, ECR, ALB (/api/* → backend, /* → frontend), ECS Fargate (2 tasks each), CloudWatch logs, IAM role, security groups
