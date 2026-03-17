import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from notebook_generator import _extract_json, _validate_notebook


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
