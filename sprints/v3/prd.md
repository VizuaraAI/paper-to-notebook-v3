# Sprint v3 — PRD: Testing, CI/CD & Deployment

## Sprint Overview
Make the Paper-to-Notebook app production-ready by adding comprehensive tests following the testing pyramid (~70% unit, ~20% integration, ~10% E2E), a GitHub Actions CI/CD pipeline that runs tests and security scans on every push/PR, and Docker + Terraform infrastructure for containerized cloud deployment. No functional changes — same app, same features, just proven, pipelined, and deployable.

## Current State (End of v2)
| Metric | Value |
|--------|-------|
| Backend tests (pytest) | 52 (unit + integration + security) |
| Frontend tests (Playwright) | 10 E2E tests |
| CI/CD pipeline | None |
| Docker | None |
| Infrastructure-as-code | None |
| GitHub remote | Not configured |
| Semgrep findings | 0 |
| pip-audit vulnerabilities | 0 |

### Existing Test Files
- `tests/test_pdf_extractor.py` — 4 unit tests
- `tests/test_arxiv_fetcher.py` — 9 tests (5 unit + 3 security + 1 real network)
- `tests/test_prompt_template.py` — 8 unit tests
- `tests/test_notebook_generator.py` — 12 tests (6 unit + 6 safety scanning)
- `tests/test_api.py` — 14 tests (3 endpoint + 7 security + 4 integration-like)
- `tests/test_health.py` — 1 test
- `tests/test_integration.py` — 4 integration tests
- `frontend/tests/app.spec.js` — 10 Playwright E2E tests

## Goals
- Testing pyramid coverage: ~70% unit | ~20% integration | ~10% E2E
- All backend modules have thorough unit tests with edge cases
- E2E tests cover the full user flow with screenshots at each step
- GitHub Actions pipeline runs pytest, Playwright, semgrep, and pip-audit on every push/PR
- Multi-service Docker Compose setup for local development
- Terraform config for AWS ECS deployment
- Zero functional regressions

## User Stories
1. As a developer, I want comprehensive unit tests for every backend module, so that I can refactor with confidence.
2. As a developer, I want integration tests that verify the full API pipeline with mocked external services, so that I catch endpoint regressions.
3. As a developer, I want E2E browser tests that simulate real user flows with screenshots, so that I can visually verify the UI works.
4. As a developer, I want a CI/CD pipeline that runs all tests and security scans on every push, so that broken or insecure code never reaches main.
5. As a developer, I want Docker Compose to spin up the entire app locally with one command, so that onboarding is instant.
6. As a developer, I want Terraform configs for cloud deployment, so that infrastructure is versioned and reproducible.

## Technical Architecture

### Testing Pyramid
```
                    ┌─────────────┐
                    │  E2E (10%)  │  Playwright — full user flows
                    │  ~10 tests  │  Screenshots at each step
                    ├─────────────┤
                    │ Integration │  FastAPI TestClient + mocked Gemini
                    │   (20%)     │  Full request/response cycle
                    │  ~15 tests  │
                    ├─────────────┤
                    │             │
                    │  Unit (70%) │  Pure function tests, edge cases
                    │  ~50 tests  │  pdf_extractor, arxiv_fetcher,
                    │             │  prompt_template, notebook_generator
                    └─────────────┘
```

### CI/CD Pipeline (GitHub Actions)
```
  Push / PR to main
         │
         ▼
  ┌──────────────────────────────────────────────┐
  │              GitHub Actions                   │
  │                                              │
  │  Job 1: BACKEND TESTS                        │
  │  ├── Setup Python 3.12 + pip install         │
  │  ├── pytest tests/ (52+ tests)               │
  │  └── Upload test results                     │
  │                                              │
  │  Job 2: E2E TESTS (parallel with Job 1)      │
  │  ├── Setup Node 20 + npm install             │
  │  ├── Install Playwright + Chromium           │
  │  ├── Start backend + frontend                │
  │  ├── npx playwright test                     │
  │  └── Upload screenshots as artifacts         │
  │                                              │
  │  Job 3: SECURITY SCAN (parallel)             │
  │  ├── semgrep --config auto backend/          │
  │  └── pip-audit                               │
  │                                              │
  │  All jobs must pass for merge ✅              │
  └──────────────────────────────────────────────┘
```

### Docker Architecture
```
  docker-compose.yml
  ┌─────────────────────────────────────────┐
  │                                         │
  │  ┌─────────────┐    ┌───────────────┐  │
  │  │  frontend   │    │   backend     │  │
  │  │  (Vite)     │───▶│  (FastAPI)    │  │
  │  │  port 5173  │    │  port 8000    │  │
  │  └─────────────┘    └───────────────┘  │
  │                                         │
  └─────────────────────────────────────────┘
```

### Terraform (AWS ECS Fargate)
```
  ┌─────────────────────────────────────────┐
  │              AWS                         │
  │                                         │
  │  ┌─ ECR ──────────────────────────────┐ │
  │  │  Container images (backend/frontend)│ │
  │  └────────────────────────────────────┘ │
  │                                         │
  │  ┌─ ECS Fargate ──────────────────────┐ │
  │  │  Backend service  (2 tasks)        │ │
  │  │  Frontend service (2 tasks)        │ │
  │  └────────────────────────────────────┘ │
  │                                         │
  │  ┌─ ALB ──────────────────────────────┐ │
  │  │  Application Load Balancer         │ │
  │  │  Routes /api/* → backend           │ │
  │  │  Routes /* → frontend              │ │
  │  └────────────────────────────────────┘ │
  │                                         │
  │  ┌─ VPC + Security Groups ────────────┐ │
  │  │  Private subnets for ECS           │ │
  │  │  Public subnets for ALB            │ │
  │  └────────────────────────────────────┘ │
  └─────────────────────────────────────────┘
```

## Out of Scope (v3)
- MCP integration
- Visualization cells in notebooks
- User authentication system
- Server-side API key storage
- Notebook sandboxed execution / preview
- Actually running `terraform apply` (config only, verified with `terraform validate`)
- Production domain / SSL certificate setup
- Monitoring / alerting (Datadog, Sentry, etc.)

## Dependencies
- Sprint v2 complete (all 10 tasks done, 52 backend tests + 10 Playwright tests passing)
- GitHub account (for remote repo + Actions)
- Docker Desktop installed locally
- Terraform CLI installed locally
