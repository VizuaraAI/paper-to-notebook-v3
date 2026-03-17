import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import fitz  # PyMuPDF
import pytest
from pdf_extractor import extract_text


def _make_pdf(pages: list[str]) -> bytes:
    """Create a simple PDF with the given page texts."""
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_text((72, 72), text, fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_single_page():
    pdf = _make_pdf(["Hello world"])
    result = extract_text(pdf)
    assert "Hello world" in result


def test_multi_page():
    pdf = _make_pdf(["Page one content", "Page two content"])
    result = extract_text(pdf)
    assert "Page one content" in result
    assert "Page two content" in result


def test_empty_pdf():
    pdf = _make_pdf([""])
    result = extract_text(pdf)
    assert isinstance(result, str)


def test_invalid_bytes():
    with pytest.raises(Exception):
        extract_text(b"not a pdf")
