import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from prompt_template import NOTEBOOK_PROMPT_TEMPLATE


def test_template_has_placeholder():
    assert "{paper_text}" in NOTEBOOK_PROMPT_TEMPLATE


def test_template_has_all_sections():
    for section in [
        "Opening",
        "Initialization",
        "Context",
        "Data Preparation",
        "Evaluation Framework",
        "Reference Implementation",
        "Algorithm Implementation",
        "Conclusions",
    ]:
        assert section in NOTEBOOK_PROMPT_TEMPLATE, f"Missing section: {section}"


def test_template_format_works():
    result = NOTEBOOK_PROMPT_TEMPLATE.format(paper_text="Test paper content")
    assert "Test paper content" in result
    assert "{paper_text}" not in result


def test_template_mentions_colab():
    assert "Colab" in NOTEBOOK_PROMPT_TEMPLATE


def test_template_mentions_ipynb_format():
    assert "nbformat" in NOTEBOOK_PROMPT_TEMPLATE


def test_template_has_user_document_delimiters():
    result = NOTEBOOK_PROMPT_TEMPLATE.format(paper_text="Test content")
    assert "<user_document>" in result
    assert "</user_document>" in result
    assert "<user_document>\nTest content\n</user_document>" in result


def test_template_has_anti_injection_instructions():
    assert "ignore previous instructions" in NOTEBOOK_PROMPT_TEMPLATE.lower() or "prompt injection" in NOTEBOOK_PROMPT_TEMPLATE.lower()
    assert "DATA" in NOTEBOOK_PROMPT_TEMPLATE


def test_template_has_security_instructions():
    assert "Security Instructions" in NOTEBOOK_PROMPT_TEMPLATE


def test_template_with_very_long_paper_text():
    """Template works with 100K character paper text."""
    long_text = "x" * 100_000
    result = NOTEBOOK_PROMPT_TEMPLATE.format(paper_text=long_text)
    assert long_text in result
    assert len(result) > 100_000


def test_template_with_latex_special_chars():
    """Template handles LaTeX and special characters in paper text."""
    latex_text = r"The loss function is $\mathcal{L} = \sum_{i=1}^{N} \log p(x_i | \theta)$"
    result = NOTEBOOK_PROMPT_TEMPLATE.format(paper_text=latex_text)
    assert latex_text in result


def test_template_with_curly_braces_in_text():
    """Template handles curly braces in paper text (Python format string edge case)."""
    # Curly braces in paper_text should work since we use .format(paper_text=...)
    text_with_braces = "The set {1, 2, 3} is defined as..."
    # This would fail if template had unescaped braces
    # Our template uses {{ }} for literal braces in JSON examples
    result = NOTEBOOK_PROMPT_TEMPLATE.format(paper_text=text_with_braces)
    assert text_with_braces in result


def test_template_with_empty_paper_text():
    """Template works with empty paper text."""
    result = NOTEBOOK_PROMPT_TEMPLATE.format(paper_text="")
    assert "<user_document>" in result
    assert "</user_document>" in result
