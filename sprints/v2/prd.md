# Sprint v2 — PRD: Security Hardening

## Sprint Overview
Harden the Paper-to-Notebook MVP against the 22 security vulnerabilities discovered during security audit (Semgrep, pip-audit, and manual OWASP review). This sprint fixes all HIGH and MEDIUM findings without changing user-facing functionality. The app should behave identically from the user's perspective — same features, same UI — but be resistant to injection, DoS, SSRF, prompt manipulation, and data leakage.

## Security Audit Summary (Input to This Sprint)
| Source | Findings |
|--------|----------|
| Semgrep (SAST) | 1 — Dynamic urllib use → SSRF risk |
| pip-audit | 1 — CVE-2026-24486 in python-multipart 0.0.20 |
| Manual Review | 20 — 5 HIGH, 11 MEDIUM, 4 LOW |
| **Total** | **22 findings** |

### HIGH Findings to Fix
1. No file size limit on PDF upload (DoS)
2. No size limit on ArXiv download (DoS)
3. Prompt injection via PDF content → malicious notebook code
4. API key sent over plaintext HTTP (deployment prep)
5. Auto-download of LLM-generated executable code (no warning/scan)

### MEDIUM Findings to Fix
6. SSRF via urllib redirect following
7. Error messages leak internal details
8. No rate limiting
9. No API key format validation
10. Missing security headers (CSP, X-Frame-Options, etc.)
11. CORS overly permissive (allow_methods=*, allow_headers=*)
12. No PDF magic byte validation
13. No text length limit before Gemini call
14. Untrusted PDF parsing attack surface
15. No timeout on Gemini API call
16. Sync blocking calls in async endpoints

### LOW Findings to Fix
17. Swagger docs exposed by default
18. No logging or monitoring
19. No CSRF protection (inherent via custom headers, but CORS needs tightening)
20. API key in React state

## Goals
- Zero HIGH severity findings remaining
- Zero MEDIUM severity findings remaining
- All v1 tests still pass (no functional regressions)
- New security-focused tests for each fix
- Semgrep re-scan returns 0 findings
- pip-audit re-scan returns 0 vulnerabilities

## User Stories
1. As a user, I want my uploaded PDF to be validated and size-limited, so that malicious or oversized files are rejected.
2. As a user, I want the app to warn me before I run LLM-generated code, so that I can review it for safety.
3. As a developer, I want structured logging and generic error messages, so that internal details are never leaked to attackers.
4. As a developer, I want rate limiting on all endpoints, so that the API cannot be abused.
5. As a user, I want the app to defend against prompt injection, so that malicious PDFs cannot generate harmful notebook code.

## Technical Architecture

### Security Layers Added in v2
```
┌─────────────────────────────────────────────┐
│              React Frontend                  │
│  ┌─────────────────────────────────────┐    │
│  │  Safety warning before download     │ ← NEW
│  │  API key cleared after use          │ ← NEW
│  └─────────────────────────────────────┘    │
└──────────────────┬──────────────────────────┘
                   │ HTTPS-ready
                   ▼
┌─────────────────────────────────────────────┐
│              FastAPI Backend                 │
│                                             │
│  ┌─ Security Middleware ──────────────────┐ │
│  │  • Rate Limiter (slowapi)             │ ← NEW
│  │  • Security Headers (CSP, XFO, etc.)  │ ← NEW
│  │  • Structured Logging                 │ ← NEW
│  │  • CORS (restricted methods/headers)  │ ← FIX
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌─ Input Validation Layer ──────────────┐ │
│  │  • File size limit (50MB)             │ ← NEW
│  │  • PDF magic byte check (%PDF-)       │ ← NEW
│  │  • API key format validation          │ ← NEW
│  │  • Text length limit (100K chars)     │ ← NEW
│  │  • ArXiv URL strict validation        │ ← FIX
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌─ SSRF Protection ────────────────────┐  │
│  │  • Disable redirect following        │ ← NEW
│  │  • Validate URL scheme (https only)  │ ← NEW
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌─ Prompt Injection Defense ────────────┐ │
│  │  • User content in <document> tags    │ ← NEW
│  │  • Anti-injection system instructions │ ← NEW
│  │  • Generated code cell scanning       │ ← NEW
│  └───────────────────────────────────────┘ │
│                                             │
│  ┌─ Async / Timeout Fixes ──────────────┐  │
│  │  • Sync endpoints (def not async def) │ ← FIX
│  │  • Gemini API timeout                 │ ← NEW
│  │  • ArXiv download size limit          │ ← NEW
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### New Dependencies
- `slowapi` — Rate limiting middleware for FastAPI
- Updated `python-multipart>=0.0.22` — CVE fix

## Out of Scope (v2)
- MCP integration — deferred to v3
- Visualization cells in notebooks — deferred to v3
- Deployment (Docker, cloud) — deferred to v3
- User authentication system
- Server-side API key storage
- Notebook sandboxed execution / preview

## Dependencies
- Sprint v1 complete (all 10 tasks done, 40 tests passing)
- Security audit findings (22 total from Semgrep, pip-audit, manual review)
