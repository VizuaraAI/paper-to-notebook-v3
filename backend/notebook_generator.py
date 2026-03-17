import json
import re

from google import genai
from prompt_template import NOTEBOOK_PROMPT_TEMPLATE


def _extract_json(text: str) -> str:
    """Extract JSON from Gemini response, handling markdown code fences."""
    # Try to find JSON in code fences first
    match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        return match.group(1)
    # Otherwise assume the whole response is JSON
    return text.strip()


def _validate_notebook(nb: dict) -> dict:
    """Ensure notebook has required ipynb structure."""
    if "nbformat" not in nb:
        nb["nbformat"] = 4
    if "nbformat_minor" not in nb:
        nb["nbformat_minor"] = 5
    if "metadata" not in nb:
        nb["metadata"] = {}
    if "cells" not in nb:
        raise ValueError("Notebook JSON missing 'cells' array")

    # Ensure Colab metadata
    nb["metadata"].setdefault("kernelspec", {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    })
    nb["metadata"].setdefault("colab", {"provenance": [], "gpuType": "T4"})
    nb["metadata"].setdefault("accelerator", "GPU")

    # Validate each cell
    for cell in nb["cells"]:
        if cell.get("cell_type") == "code":
            cell.setdefault("execution_count", None)
            cell.setdefault("outputs", [])
        cell.setdefault("metadata", {})
        # Ensure source is a list of strings
        if isinstance(cell.get("source"), str):
            cell["source"] = [cell["source"]]

    return nb


def generate_notebook(paper_text: str, api_key: str) -> dict:
    """Send paper text to Gemini and return a valid .ipynb notebook dict."""
    client = genai.Client(api_key=api_key)

    prompt = NOTEBOOK_PROMPT_TEMPLATE.format(paper_text=paper_text)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    raw_text = response.text
    json_str = _extract_json(raw_text)

    try:
        notebook = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini returned invalid JSON: {e}\nResponse: {raw_text[:500]}")

    return _validate_notebook(notebook)
