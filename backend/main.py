from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from pdf_extractor import extract_text
from arxiv_fetcher import fetch_arxiv_pdf
from notebook_generator import generate_notebook

app = FastAPI(title="Paper to Notebook API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ArxivRequest(BaseModel):
    url: str


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    x_api_key: str = Header(...),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        paper_text = extract_text(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text from PDF: {e}")

    if not paper_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from PDF")

    try:
        notebook = generate_notebook(paper_text, x_api_key)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Notebook generation failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")

    return JSONResponse(content=notebook)


@app.post("/api/arxiv-url")
async def arxiv_url(
    body: ArxivRequest,
    x_api_key: str = Header(...),
):
    try:
        pdf_bytes = fetch_arxiv_pdf(body.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch arXiv paper: {e}")

    try:
        paper_text = extract_text(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {e}")

    if not paper_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from paper")

    try:
        notebook = generate_notebook(paper_text, x_api_key)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Notebook generation failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")

    return JSONResponse(content=notebook)
