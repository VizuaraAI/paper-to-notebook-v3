import logging

from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

from pdf_extractor import extract_text
from arxiv_fetcher import fetch_arxiv_pdf
from notebook_generator import generate_notebook

logger = logging.getLogger("paper_to_notebook")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

MAX_PDF_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_TEXT_LENGTH = 100_000  # ~100K characters

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Paper to Notebook API", version="0.2.0", docs_url=None, redoc_url=None, openapi_url=None)
app.state.limiter = limiter


def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Try again later."})


app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://paper-to-notebook-alb-571744306.us-east-1.elb.amazonaws.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Api-Key"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    return response


class ArxivRequest(BaseModel):
    url: str


def _validate_api_key(api_key: str) -> None:
    if not api_key or len(api_key) < 10:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload-pdf")
@limiter.limit("30/minute")
def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    x_api_key: str = Header(...),
):
    _validate_api_key(x_api_key)

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    pdf_bytes = file.file.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(pdf_bytes) > MAX_PDF_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")

    if not pdf_bytes[:5].startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="File is not a valid PDF")

    try:
        paper_text = extract_text(pdf_bytes)
    except Exception as e:
        logger.exception("PDF text extraction failed")
        raise HTTPException(status_code=400, detail="Failed to extract text from PDF")

    if not paper_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from PDF")

    if len(paper_text) > MAX_TEXT_LENGTH:
        paper_text = paper_text[:MAX_TEXT_LENGTH]

    try:
        notebook = generate_notebook(paper_text, x_api_key)
    except ValueError as e:
        logger.exception("Notebook generation failed")
        raise HTTPException(status_code=500, detail="Notebook generation failed")
    except Exception as e:
        logger.exception("Gemini API error")
        raise HTTPException(status_code=500, detail="Notebook generation failed")

    return JSONResponse(content=notebook)


@app.post("/api/arxiv-url")
@limiter.limit("30/minute")
def arxiv_url(
    request: Request,
    body: ArxivRequest,
    x_api_key: str = Header(...),
):
    _validate_api_key(x_api_key)

    try:
        pdf_bytes = fetch_arxiv_pdf(body.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid arXiv URL or ID")
    except Exception as e:
        logger.exception("Failed to fetch arXiv paper")
        raise HTTPException(status_code=500, detail="Failed to fetch arXiv paper")

    try:
        paper_text = extract_text(pdf_bytes)
    except Exception as e:
        logger.exception("Failed to extract text from arXiv paper")
        raise HTTPException(status_code=500, detail="Failed to extract text from paper")

    if not paper_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from paper")

    if len(paper_text) > MAX_TEXT_LENGTH:
        paper_text = paper_text[:MAX_TEXT_LENGTH]

    try:
        notebook = generate_notebook(paper_text, x_api_key)
    except ValueError as e:
        logger.exception("Notebook generation failed")
        raise HTTPException(status_code=500, detail="Notebook generation failed")
    except Exception as e:
        logger.exception("Gemini API error")
        raise HTTPException(status_code=500, detail="Notebook generation failed")

    return JSONResponse(content=notebook)
