import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from arxiv_fetcher import parse_arxiv_id, fetch_arxiv_pdf


def test_parse_full_abs_url():
    assert parse_arxiv_id("https://arxiv.org/abs/2401.12345") == "2401.12345"


def test_parse_full_pdf_url():
    assert parse_arxiv_id("https://arxiv.org/pdf/2401.12345") == "2401.12345"


def test_parse_bare_id():
    assert parse_arxiv_id("2401.12345") == "2401.12345"


def test_parse_versioned_url():
    assert parse_arxiv_id("https://arxiv.org/abs/2401.12345v2") == "2401.12345v2"


def test_parse_invalid():
    with pytest.raises(ValueError):
        parse_arxiv_id("https://google.com/not-arxiv")


def test_fetch_real_paper():
    """Fetch a known small paper from arXiv (Attention Is All You Need)."""
    pdf_bytes = fetch_arxiv_pdf("1706.03762")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes[:4] == b"%PDF"
