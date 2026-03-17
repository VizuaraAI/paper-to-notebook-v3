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

VALID_API_KEY = "test-api-key-12345"


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
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 200
    nb = resp.json()

    assert nb["nbformat"] == 4
    assert isinstance(nb["cells"], list)
    assert len(nb["cells"]) > 0
    assert nb["cells"][0]["cell_type"] in ("markdown", "code")

    call_args = mock_gen.call_args
    assert "test research paper" in call_args[0][0]
    assert call_args[0][1] == VALID_API_KEY


@patch("main.generate_notebook", return_value=VALID_NOTEBOOK)
@patch("main.fetch_arxiv_pdf")
def test_full_arxiv_pipeline(mock_fetch, mock_gen):
    """ArXiv URL → fetch PDF → text extraction → notebook generation → valid ipynb response."""
    mock_fetch.return_value = _make_pdf("Attention mechanism paper content.")
    resp = client.post(
        "/api/arxiv-url",
        json={"url": "https://arxiv.org/abs/1706.03762"},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 200
    nb = resp.json()
    assert nb["nbformat"] == 4
    assert len(nb["cells"]) > 0

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
def test_error_propagation_generic(mock_gen):
    """Errors return generic message, not internal details."""
    pdf = _make_pdf("Test paper")
    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("paper.pdf", pdf, "application/pdf")},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 500
    detail = resp.json()["detail"]
    assert detail == "Notebook generation failed"
    assert "Invalid API key" not in detail


# ---------------------------------------------------------------------------
# New tests — Sprint v3, Task 3
# ---------------------------------------------------------------------------

FAKE_NOTEBOOK = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "colab": {"provenance": [], "gpuType": "T4"},
        "accelerator": "GPU",
    },
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": ["# Generated Notebook"]},
        {
            "cell_type": "code",
            "metadata": {},
            "source": ["print('hello world')"],
            "execution_count": None,
            "outputs": [],
        },
    ],
}


@patch("main.generate_notebook", return_value=FAKE_NOTEBOOK)
def test_full_pdf_upload_pipeline_with_text_extraction(mock_gen):
    """Upload a real PDF, verify text extraction and generate_notebook call."""
    content = "Deep learning paper about attention mechanisms in neural networks."
    pdf = _make_pdf(content)
    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("paper.pdf", pdf, "application/pdf")},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    # (a) status 200
    assert resp.status_code == 200
    nb = resp.json()
    # (b) response has cells and nbformat
    assert "cells" in nb
    assert "nbformat" in nb
    assert nb["nbformat"] == 4
    assert isinstance(nb["cells"], list)
    # (c) generate_notebook called with extracted text containing PDF content
    assert mock_gen.called
    call_args = mock_gen.call_args
    extracted_text = call_args[0][0]
    assert "attention" in extracted_text.lower() or "deep learning" in extracted_text.lower()
    passed_api_key = call_args[0][1]
    assert len(passed_api_key) >= 10
    assert passed_api_key == VALID_API_KEY


@patch("main.generate_notebook", return_value=FAKE_NOTEBOOK)
@patch("main.fetch_arxiv_pdf")
def test_full_arxiv_pipeline_mocked(mock_fetch, mock_gen):
    """ArXiv URL → mocked fetch_arxiv_pdf → text extraction → generate_notebook."""
    arxiv_url = "https://arxiv.org/abs/1706.03762"
    mock_fetch.return_value = _make_pdf("Transformer architecture self-attention paper.")
    resp = client.post(
        "/api/arxiv-url",
        json={"url": arxiv_url},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    # (a) status 200
    assert resp.status_code == 200
    nb = resp.json()
    assert "cells" in nb
    assert "nbformat" in nb
    # (b) fetch_arxiv_pdf called with the URL
    mock_fetch.assert_called_once_with(arxiv_url)
    # (c) generate_notebook called with extracted text
    assert mock_gen.called
    extracted_text = mock_gen.call_args[0][0]
    assert len(extracted_text) > 0


@patch("main.generate_notebook", return_value=FAKE_NOTEBOOK)
def test_large_pdf_text_truncation(mock_gen):
    """Text extracted from a large PDF is truncated to MAX_TEXT_LENGTH (100,000 chars)."""
    # Build a PDF with many pages of text to exceed the 100k char limit
    long_line = "This is a filler sentence for a very large research paper. " * 10
    doc = fitz.open()
    for _ in range(50):
        page = doc.new_page()
        page.insert_text((72, 72), long_line * 20, fontsize=8)
    pdf_bytes = doc.tobytes()
    doc.close()

    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("big_paper.pdf", pdf_bytes, "application/pdf")},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 200
    assert mock_gen.called
    extracted_text = mock_gen.call_args[0][0]
    assert len(extracted_text) <= 100_000


def test_upload_empty_pdf_returns_400():
    """A valid-magic-bytes PDF with no extractable text returns 400."""
    # Build a PDF with no text inserted — fitz creates a blank page
    doc = fitz.open()
    doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()

    resp = client.post(
        "/api/upload-pdf",
        files={"file": ("blank.pdf", pdf_bytes, "application/pdf")},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 400
    assert "No text could be extracted" in resp.json()["detail"]


def test_arxiv_invalid_url_returns_400():
    """An invalid URL posted to /api/arxiv-url returns 400."""
    resp = client.post(
        "/api/arxiv-url",
        json={"url": "https://not-arxiv.com/some/random/page"},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp.status_code == 400


@patch("main.generate_notebook", return_value=FAKE_NOTEBOOK)
@patch("main.fetch_arxiv_pdf")
def test_upload_and_arxiv_independent(mock_fetch, mock_gen):
    """A PDF upload call and an arXiv call in sequence both succeed independently."""
    mock_fetch.return_value = _make_pdf("ArXiv paper on reinforcement learning.")

    # First call: upload-pdf
    pdf = _make_pdf("Supervised learning paper about image classification.")
    resp1 = client.post(
        "/api/upload-pdf",
        files={"file": ("paper.pdf", pdf, "application/pdf")},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp1.status_code == 200
    assert "cells" in resp1.json()

    # Second call: arxiv-url
    resp2 = client.post(
        "/api/arxiv-url",
        json={"url": "https://arxiv.org/abs/1706.03762"},
        headers={"X-Api-Key": VALID_API_KEY},
    )
    assert resp2.status_code == 200
    assert "cells" in resp2.json()

    # Both calls resolved independently without interfering
    assert mock_gen.call_count == 2
    mock_fetch.assert_called_once_with("https://arxiv.org/abs/1706.03762")
