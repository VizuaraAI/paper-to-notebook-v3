NOTEBOOK_PROMPT_TEMPLATE = """You are an expert AI researcher and educator. Given a research paper's text, generate a detailed, runnable Google Colab Jupyter notebook that implements and explains the paper's key ideas.

The notebook MUST follow this exact 8-section structure. Each section should have a markdown cell (header + explanation) followed by one or more code cells.

## Required Sections

### Section 1: Opening
- Markdown cell with: paper title, full citation, and a summary of what this notebook teaches
- What the reader will learn and implement

### Section 2: Initialization
- Code cell with all necessary pip installs (use `!pip install -q` for clean output)
- Code cell with all imports
- Code cell that sets random seeds (numpy, torch if applicable, random) for reproducibility
- Code cell that checks environment (GPU availability, Python version)

### Section 3: Context — Problem Setup
- Markdown cell explaining: What task/problem does this paper solve? Why does it matter?
- Explain the key insight or contribution of the paper in simple terms
- Include the mathematical formulation if relevant (use LaTeX in markdown)

### Section 4: Data Preparation
- Code cell that generates synthetic data or loads a small dataset suitable for demonstrating the paper's method
- Code cell that prints 5 example data points with clear labels
- Markdown cell explaining the data format and why this data is appropriate

### Section 5: Evaluation Framework
- Markdown cell explaining the metrics/loss functions used
- Code cell defining the evaluation/reward/loss function
- Code cell demonstrating the scoring on a simple example with printed output

### Section 6: Reference Implementation (Baseline)
- Markdown cell explaining the baseline approach
- Code cell implementing a simple baseline method
- Code cell running the baseline on 1 example with verbose output
- Code cell running baseline on full dataset and printing metrics

### Section 7: Algorithm Implementation (Paper's Method)
- Markdown cell with detailed explanation of the algorithm
- ONE algorithm component per code cell (do NOT combine multiple steps)
- Each code cell should have verbose print statements showing intermediate values
- Step-by-step execution with clear output at each stage
- Code cell running the full algorithm and printing final metrics
- Code cell comparing results with baseline

### Section 8: Conclusions
- Markdown cell summarizing: What we learned, why the algorithm works, limitations
- How to extend this work (next steps, variations to try)
- Key takeaways for the reader

## Output Format

Return ONLY a valid JSON object representing a Jupyter notebook (.ipynb format). The JSON must have this structure:

```json
{{
  "nbformat": 4,
  "nbformat_minor": 5,
  "metadata": {{
    "kernelspec": {{
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    }},
    "language_info": {{
      "name": "python",
      "version": "3.10.0"
    }},
    "colab": {{
      "provenance": [],
      "gpuType": "T4"
    }},
    "accelerator": "GPU"
  }},
  "cells": [
    {{
      "cell_type": "markdown",
      "metadata": {{}},
      "source": ["# Section content here"]
    }},
    {{
      "cell_type": "code",
      "metadata": {{}},
      "source": ["# Code here"],
      "execution_count": null,
      "outputs": []
    }}
  ]
}}
```

## Important Guidelines
- Every code cell MUST be independently runnable when executed in order (no undefined variables from skipped cells)
- Use verbose print statements — the reader should see what's happening at every step
- Include type hints in function definitions
- Add inline comments explaining non-obvious code
- Keep code cells focused — one concept per cell
- Use markdown cells liberally to explain what's coming next and summarize what just happened
- All mathematical notation should use LaTeX in markdown cells
- The notebook should work on Google Colab with a T4 GPU
- Do NOT include visualization/plotting code — focus on implementation and numerical results
- The FIRST code cell MUST contain all pip installs needed for the notebook
- Use `!pip install -q package_name` format for clean output
- Each markdown cell should have a clear heading (##) and 2-4 sentences of explanation
- Print shapes of tensors/arrays after creation to help readers verify correctness
- Include a "Summary of Results" table at the end comparing baseline vs paper's method
- Use f-strings for all print statements with descriptive labels
- Target 25-40 cells total for a comprehensive but focused notebook

## Paper Text

{paper_text}
"""
