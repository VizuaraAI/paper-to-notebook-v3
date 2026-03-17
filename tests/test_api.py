import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import fitz
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

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
        headers={"X-Api-Key": "fake-key"},
    )
    assert resp.status_code == 400
    assert "PDF" in resp.json()["detail"]


@patch("main.generate_notebook", return_value=FAKE_NOTEBOOK)
def test_upload_pdf_success(mock_gen):
    pdf = _make_pdf()
    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("paper.pdf", pdf, "application/pdf")},
        headers={"X-Api-Key": "fake-key"},
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
        headers={"X-Api-Key": "fake-key"},
    )
    assert resp.status_code == 400


@patch("main.generate_notebook", return_value=FAKE_NOTEBOOK)
@patch("main.fetch_arxiv_pdf", return_value=_make_pdf())
def test_arxiv_url_success(mock_fetch, mock_gen):
    resp = client.post(
        "/api/arxiv-url",
        json={"url": "https://arxiv.org/abs/2401.12345"},
        headers={"X-Api-Key": "fake-key"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "cells" in data
    mock_fetch.assert_called_once()
    mock_gen.assert_called_once()
