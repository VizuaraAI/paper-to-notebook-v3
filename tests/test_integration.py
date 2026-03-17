"""Integration tests for the full pipeline."""
import sys
import os
import json
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import fitz
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _make_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


VALID_NOTEBOOK = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "colab": {"provenance": [], "gpuType": "T4"},
        "accelerator": "GPU",
    },
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": ["# Paper Implementation"]},
        {"cell_type": "code", "metadata": {}, "source": ["print('hello')"], "execution_count": None, "outputs": []},
    ],
}


@patch("main.generate_notebook", return_value=VALID_NOTEBOOK)
def test_full_pdf_pipeline(mock_gen):
    """PDF upload → text extraction → notebook generation → valid ipynb response."""
    pdf = _make_pdf("This is a test research paper about transformers.")
    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("paper.pdf", pdf, "application/pdf")},
        headers={"X-Api-Key": "test-key"},
    )
    assert resp.status_code == 200
    nb = resp.json()

    # Validate notebook structure
    assert nb["nbformat"] == 4
    assert isinstance(nb["cells"], list)
    assert len(nb["cells"]) > 0
    assert nb["cells"][0]["cell_type"] in ("markdown", "code")

    # Verify the extracted text was passed to generate_notebook
    call_args = mock_gen.call_args
    assert "test research paper" in call_args[0][0]
    assert call_args[0][1] == "test-key"


@patch("main.generate_notebook", return_value=VALID_NOTEBOOK)
@patch("main.fetch_arxiv_pdf")
def test_full_arxiv_pipeline(mock_fetch, mock_gen):
    """ArXiv URL → fetch PDF → text extraction → notebook generation → valid ipynb response."""
    mock_fetch.return_value = _make_pdf("Attention mechanism paper content.")
    resp = client.post(
        "/api/arxiv-url",
        json={"url": "https://arxiv.org/abs/1706.03762"},
        headers={"X-Api-Key": "test-key"},
    )
    assert resp.status_code == 200
    nb = resp.json()
    assert nb["nbformat"] == 4
    assert len(nb["cells"]) > 0

    # Verify arXiv URL was fetched
    mock_fetch.assert_called_once_with("https://arxiv.org/abs/1706.03762")


def test_cors_headers():
    """Ensure CORS allows the frontend origin."""
    resp = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


@patch("main.generate_notebook", side_effect=ValueError("Invalid API key"))
def test_error_propagation(mock_gen):
    """Errors from notebook generation are returned as 500 with detail."""
    pdf = _make_pdf("Test paper")
    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("paper.pdf", pdf, "application/pdf")},
        headers={"X-Api-Key": "bad-key"},
    )
    assert resp.status_code == 500
    assert "Invalid API key" in resp.json()["detail"]
