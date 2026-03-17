import fitz  # PyMuPDF


def extract_text(pdf_bytes: bytes) -> str:
    """Extract and return cleaned text from PDF bytes."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages).strip()
