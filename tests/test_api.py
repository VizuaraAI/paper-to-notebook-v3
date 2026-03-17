import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import fitz
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_API_KEY = "test-api-key-12345"  # ≥10 chars

FAKE_NOTEBOOK = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {},
    "cells": [{"cell_type": "markdown", "metadata": {}, "source": ["# Test"]}],
}


def _make_pdf(text: str = "Test paper content") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200


# --- /api/upload-pdf tests ---


def test_upload_pdf_missing_api_key():
    pdf = _make_pdf()
    resp = client.post("/api/upload-pdf", files={"file": ("test.pdf", pdf, "application/pdf")})
    assert resp.status_code == 422


def test_upload_pdf_non_pdf_file():
    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("test.txt", b"not a pdf", "text/plain")},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 400
    assert "PDF" in resp.json()["detail"]


@patch("main.generate_notebook", return_value=FAKE_NOTEBOOK)
def test_upload_pdf_success(mock_gen):
    pdf = _make_pdf()
    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("paper.pdf", pdf, "application/pdf")},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "cells" in data
    assert data["nbformat"] == 4
    mock_gen.assert_called_once()


# --- /api/arxiv-url tests ---


def test_arxiv_url_missing_api_key():
    resp = client.post("/api/arxiv-url", json={"url": "2401.12345"})
    assert resp.status_code == 422


def test_arxiv_url_invalid_url():
    resp = client.post(
        "/api/arxiv-url",
        json={"url": "not-a-valid-url"},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 400


@patch("main.generate_notebook", return_value=FAKE_NOTEBOOK)
@patch("main.fetch_arxiv_pdf", return_value=_make_pdf())
def test_arxiv_url_success(mock_fetch, mock_gen):
    resp = client.post(
        "/api/arxiv-url",
        json={"url": "https://arxiv.org/abs/2401.12345"},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "cells" in data
    mock_fetch.assert_called_once()
    mock_gen.assert_called_once()


# --- Security tests (v2) ---


def test_upload_pdf_short_api_key_rejected():
    """API key <10 chars is rejected with 401."""
    pdf = _make_pdf()
    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("paper.pdf", pdf, "application/pdf")},
        headers={"X-Api-Key": "short"},
    )
    assert resp.status_code == 401


def test_upload_pdf_file_too_large():
    """Files >50MB are rejected with 413."""
    # Create a file that's just over the limit header (fake large, starts with %PDF-)
    large_data = b"%PDF-" + b"x" * (50 * 1024 * 1024 + 1)
    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("large.pdf", large_data, "application/pdf")},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 413


def test_upload_pdf_invalid_magic_bytes():
    """Files without %PDF- magic bytes are rejected."""
    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("fake.pdf", b"NOT-A-PDF-FILE-CONTENT", "application/pdf")},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 400
    assert "not a valid PDF" in resp.json()["detail"]


def test_security_headers_present():
    """All responses include security headers."""
    resp = client.get("/api/health")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["Content-Security-Policy"] == "default-src 'none'"


def test_swagger_docs_disabled():
    """Swagger UI and OpenAPI schema are not accessible."""
    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_error_messages_dont_leak_internals():
    """500 errors return generic messages, not exception details."""
    pdf = _make_pdf()
    with patch("main.generate_notebook", side_effect=Exception("Internal secret error: /path/to/file")):
        resp = client.post(
            "/api/upload-pdf",
            files={"file": ("paper.pdf", pdf, "application/pdf")},
            headers={"X-Api-Key": VALID_API_KEY},
        )
    assert resp.status_code == 500
    detail = resp.json()["detail"]
    assert "/path/to/file" not in detail
    assert "Internal secret" not in detail
    assert detail == "Notebook generation failed"


def test_cors_methods_restricted():
    """CORS preflight only allows GET and POST."""
    resp = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "DELETE",
        },
    )
    # DELETE should not be in allowed methods
    allowed = resp.headers.get("access-control-allow-methods", "")
    assert "DELETE" not in allowed
