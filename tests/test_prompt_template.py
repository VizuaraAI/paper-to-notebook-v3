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
