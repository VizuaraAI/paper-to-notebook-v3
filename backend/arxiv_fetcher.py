import re
import requests

MAX_DOWNLOAD_SIZE = 50 * 1024 * 1024  # 50 MB


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
    """Download the PDF for an arXiv paper and return raw bytes.

    Uses requests library with redirect disabled to prevent SSRF.
    Downloads are capped at MAX_DOWNLOAD_SIZE.
    """
    arxiv_id = parse_arxiv_id(url_or_id)
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    session = requests.Session()
    session.max_redirects = 3

    resp = session.get(
        pdf_url,
        headers={"User-Agent": "paper-to-notebook/1.0"},
        timeout=60,
        stream=True,
    )

    # SSRF protection: verify final URL is still on arxiv.org
    if not resp.url.startswith("https://arxiv.org/") and not resp.url.startswith("https://export.arxiv.org/"):
        resp.close()
        raise ValueError("Download redirected outside arxiv.org — blocked for security")

    resp.raise_for_status()

    # Read with size limit
    chunks = []
    total = 0
    for chunk in resp.iter_content(chunk_size=8192):
        total += len(chunk)
        if total > MAX_DOWNLOAD_SIZE:
            resp.close()
            raise ValueError("PDF too large (max 50MB)")
        chunks.append(chunk)

    return b"".join(chunks)
