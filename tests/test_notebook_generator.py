import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from notebook_generator import _extract_json, _validate_notebook, _scan_code_cells, SAFETY_DISCLAIMER_CELL, DANGEROUS_PATTERNS


def test_extract_json_from_code_fence():
    text = '```json\n{"cells": []}\n```'
    assert _extract_json(text) == '{"cells": []}'


def test_extract_json_bare():
    text = '{"cells": []}'
    assert _extract_json(text) == '{"cells": []}'


def test_extract_json_with_surrounding_text():
    text = 'Here is the notebook:\n```json\n{"cells": [{"cell_type": "code"}]}\n```\nDone!'
    result = _extract_json(text)
    assert '"cells"' in result


def test_validate_notebook_adds_defaults():
    nb = {"cells": [{"cell_type": "code", "source": "print('hi')"}]}
    result = _validate_notebook(nb)
    assert result["nbformat"] == 4
    assert result["nbformat_minor"] == 5
    assert "colab" in result["metadata"]
    assert result["cells"][0]["execution_count"] is None
    assert result["cells"][0]["outputs"] == []
    # Source should be converted to list
    assert result["cells"][0]["source"] == ["print('hi')"]


def test_validate_notebook_missing_cells():
    with pytest.raises(ValueError, match="missing 'cells'"):
        _validate_notebook({"metadata": {}})


def test_validate_preserves_existing_metadata():
    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {"custom": "value"},
        "cells": [],
    }
    result = _validate_notebook(nb)
    assert result["metadata"]["custom"] == "value"
    assert "colab" in result["metadata"]


def test_scan_flags_dangerous_os_system():
    nb = {"cells": [{"cell_type": "code", "source": ["import os\n", "os.system('ls')"]}]}
    result = _scan_code_cells(nb)
    assert "WARNING" in result["cells"][0]["source"][0]


def test_scan_flags_subprocess():
    nb = {"cells": [{"cell_type": "code", "source": ["import subprocess\n", "subprocess.run(['ls'])"]}]}
    result = _scan_code_cells(nb)
    assert "WARNING" in result["cells"][0]["source"][0]


def test_scan_flags_eval():
    nb = {"cells": [{"cell_type": "code", "source": ["eval('1+1')"]}]}
    result = _scan_code_cells(nb)
    assert "WARNING" in result["cells"][0]["source"][0]


def test_scan_leaves_safe_code_alone():
    nb = {"cells": [{"cell_type": "code", "source": ["print('hello')"]}]}
    result = _scan_code_cells(nb)
    assert result["cells"][0]["source"] == ["print('hello')"]


def test_scan_ignores_markdown_cells():
    nb = {"cells": [{"cell_type": "markdown", "source": ["os.system is dangerous"]}]}
    result = _scan_code_cells(nb)
    assert "WARNING" not in result["cells"][0]["source"][0]


def test_safety_disclaimer_cell_exists():
    assert SAFETY_DISCLAIMER_CELL["cell_type"] == "markdown"
    assert "Safety Notice" in "".join(SAFETY_DISCLAIMER_CELL["source"])


def test_validate_notebook_only_markdown_cells():
    """Notebook with only markdown cells validates correctly."""
    nb = {
        "cells": [
            {"cell_type": "markdown", "source": "# Title"},
            {"cell_type": "markdown", "source": "Some text"},
        ]
    }
    result = _validate_notebook(nb)
    assert len(result["cells"]) == 2
    # Markdown cells should not get execution_count
    assert "execution_count" not in result["cells"][0]


def test_validate_notebook_mixed_source_types():
    """Source can be string or list — both should work."""
    nb = {
        "cells": [
            {"cell_type": "code", "source": "print('string')"},
            {"cell_type": "code", "source": ["print('list')"]},
        ]
    }
    result = _validate_notebook(nb)
    # String source should be converted to list
    assert result["cells"][0]["source"] == ["print('string')"]
    # List source should stay as list
    assert result["cells"][1]["source"] == ["print('list')"]


def test_scan_multiple_dangerous_patterns_in_one_cell():
    """Cell with multiple dangerous patterns flags all of them."""
    nb = {"cells": [{"cell_type": "code", "source": ["import os\n", "os.system('ls')\n", "eval('1+1')"]}]}
    result = _scan_code_cells(nb)
    warning = result["cells"][0]["source"][0]
    assert "WARNING" in warning
    assert "os.system" in warning
    assert "eval(" in warning


def test_extract_json_with_malformed_json():
    """Malformed JSON in code fence returns the malformed string (caller handles error)."""
    text = '```json\n{not valid json}\n```'
    result = _extract_json(text)
    assert result == "{not valid json}"


def test_scan_does_not_modify_empty_cells():
    """Cells with empty source are left alone."""
    nb = {"cells": [{"cell_type": "code", "source": []}]}
    result = _scan_code_cells(nb)
    assert result["cells"][0]["source"] == []
