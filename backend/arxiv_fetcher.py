import re
import urllib.request


def parse_arxiv_id(url_or_id: str) -> str:
    """Extract arXiv paper ID from a URL or bare ID string."""
    url_or_id = url_or_id.strip()

    # Match arXiv URL patterns
    match = re.match(
        r"https?://arxiv\.org/(?:abs|pdf)/([0-9]+\.[0-9]+(?:v\d+)?)", url_or_id
    )
    if match:
        return match.group(1)

    # Match bare ID (e.g. 2401.12345 or 2401.12345v2)
    if re.match(r"^[0-9]+\.[0-9]+(?:v\d+)?$", url_or_id):
        return url_or_id

    raise ValueError(f"Could not parse arXiv ID from: {url_or_id}")


def fetch_arxiv_pdf(url_or_id: str) -> bytes:
    """Download the PDF for an arXiv paper and return raw bytes."""
    arxiv_id = parse_arxiv_id(url_or_id)
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    req = urllib.request.Request(pdf_url, headers={"User-Agent": "paper-to-notebook/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()
