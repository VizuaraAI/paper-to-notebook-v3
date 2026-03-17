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


# --- v3 edge case tests ---


def test_unicode_characters():
    """PDF with unicode/special characters extracts correctly."""
    pdf = _make_pdf(["Caf\u00e9 na\u00efve r\u00e9sum\u00e9"])
    result = extract_text(pdf)
    assert "Caf\u00e9" in result
    assert "r\u00e9sum\u00e9" in result


def test_multi_page_concatenation_order():
    """Pages are concatenated in order."""
    pdf = _make_pdf(["FIRST_PAGE", "SECOND_PAGE", "THIRD_PAGE"])
    result = extract_text(pdf)
    first_idx = result.index("FIRST_PAGE")
    second_idx = result.index("SECOND_PAGE")
    third_idx = result.index("THIRD_PAGE")
    assert first_idx < second_idx < third_idx


def test_whitespace_normalization():
    """Extracted text is stripped of leading/trailing whitespace."""
    pdf = _make_pdf(["  some text  "])
    result = extract_text(pdf)
    # Result should be stripped (no leading/trailing whitespace)
    assert result == result.strip()


def test_large_text_extraction():
    """PDF with substantial text spread across many pages extracts successfully."""
    pages = [f"Paragraph {i} with some content here." for i in range(20)]
    pdf = _make_pdf(pages)
    result = extract_text(pdf)
    assert len(result) > 200
    assert "Paragraph 0" in result
    assert "Paragraph 19" in result


def test_many_pages():
    """PDF with many pages extracts all content."""
    pages = [f"Content on page {i}" for i in range(10)]
    pdf = _make_pdf(pages)
    result = extract_text(pdf)
    for i in range(10):
        assert f"Content on page {i}" in result
