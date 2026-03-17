import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from unittest.mock import patch, MagicMock
from arxiv_fetcher import parse_arxiv_id, fetch_arxiv_pdf, MAX_DOWNLOAD_SIZE


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


def test_fetch_rejects_redirect_outside_arxiv():
    """SSRF protection: redirect to a non-arxiv domain must raise ValueError."""
    mock_response = MagicMock()
    mock_response.url = "https://evil.com/malicious"
    mock_response.iter_content.return_value = iter([b"%PDF-fake"])

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    with patch("arxiv_fetcher.requests.Session", return_value=mock_session):
        with pytest.raises(ValueError, match="redirected outside arxiv.org"):
            fetch_arxiv_pdf("2401.12345")


def test_fetch_rejects_oversized_pdf():
    """Download size limit: a response exceeding 50 MB must raise ValueError."""
    # Each chunk is 1 MB; 51 chunks will push the total past MAX_DOWNLOAD_SIZE.
    chunk = b"x" * (1024 * 1024)  # 1 MB
    oversized_chunks = iter([chunk] * 51)

    mock_response = MagicMock()
    mock_response.url = "https://arxiv.org/pdf/2401.12345.pdf"
    mock_response.iter_content.return_value = oversized_chunks

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    with patch("arxiv_fetcher.requests.Session", return_value=mock_session):
        with pytest.raises(ValueError, match="PDF too large"):
            fetch_arxiv_pdf("2401.12345")


def test_parse_rejects_non_arxiv_urls():
    """URL validation: non-arxiv URLs that embed a valid-looking ID must raise ValueError."""
    non_arxiv_urls = [
        "https://evil.com/pdf/2401.12345",
        "https://notarxiv.org/abs/2401.12345",
        "http://arxiv.org.evil.com/abs/2401.12345",
        "https://evil.com/abs/2401.12345v2",
    ]
    for url in non_arxiv_urls:
        with pytest.raises(ValueError):
            parse_arxiv_id(url)


# --- v3 edge case tests ---


def test_parse_versioned_ids():
    """Parse various version suffixes."""
    assert parse_arxiv_id("2401.12345v1") == "2401.12345v1"
    assert parse_arxiv_id("2401.12345v3") == "2401.12345v3"
    assert parse_arxiv_id("https://arxiv.org/abs/2401.12345v10") == "2401.12345v10"


def test_parse_whitespace_padded_input():
    """Input with leading/trailing whitespace is handled."""
    assert parse_arxiv_id("  2401.12345  ") == "2401.12345"
    assert parse_arxiv_id("\n2401.12345\t") == "2401.12345"
    assert parse_arxiv_id("  https://arxiv.org/abs/2401.12345  ") == "2401.12345"


def test_fetch_http_404_error():
    """HTTP 404 from arxiv raises an exception."""
    mock_response = MagicMock()
    mock_response.url = "https://arxiv.org/pdf/9999.99999.pdf"
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    with patch("arxiv_fetcher.requests.Session", return_value=mock_session):
        with pytest.raises(Exception):
            fetch_arxiv_pdf("9999.99999")


def test_fetch_connection_timeout():
    """Connection timeout raises an exception."""
    import requests as req

    mock_session = MagicMock()
    mock_session.get.side_effect = req.exceptions.Timeout("Connection timed out")

    with patch("arxiv_fetcher.requests.Session", return_value=mock_session):
        with pytest.raises(req.exceptions.Timeout):
            fetch_arxiv_pdf("2401.12345")


def test_fetch_real_paper():
    """Fetch a known small paper from arXiv (Attention Is All You Need)."""
    pdf_bytes = fetch_arxiv_pdf("1706.03762")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes[:4] == b"%PDF"
