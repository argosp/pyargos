"""
Tests for argos.utils.jsonutils — loadJSON, processJSONToPandas, convertJSONtoPandas.
"""

import json
import os
import pandas
import pytest
from argos.utils.jsonutils import loadJSON, processJSONToPandas, convertJSONtoPandas


class TestLoadJSONFromDict:

    def test_dict_passthrough(self):
        data = {"key": "value"}
        result = loadJSON(data)
        assert result == data

    def test_dict_not_copied(self):
        """Dict input should be returned as-is (same object)."""
        data = {"key": "value"}
        result = loadJSON(data)
        assert result is data


class TestLoadJSONFromString:

    def test_json_string(self):
        result = loadJSON('{"a": 1, "b": 2}')
        assert result == {"a": 1, "b": 2}

    def test_invalid_json_string_raises(self):
        with pytest.raises(ValueError):
            loadJSON("not valid json and not a file path")


class TestLoadJSONFromFile:

    def test_file_path(self, tmp_path):
        filepath = tmp_path / "test.json"
        filepath.write_text('{"loaded": true}')
        result = loadJSON(str(filepath))
        assert result == {"loaded": True}

    def test_file_object(self, tmp_path):
        filepath = tmp_path / "test.json"
        filepath.write_text('{"loaded": true}')
        with open(filepath) as f:
            result = loadJSON(f)
        assert result == {"loaded": True}

    def test_nonexistent_file_raises(self):
        with pytest.raises(ValueError):
            loadJSON("/nonexistent/path/to/file.json")


class TestLoadJSONInvalidType:

    def test_int_raises(self):
        with pytest.raises(ValueError):
            loadJSON(42)

    def test_list_raises(self):
        with pytest.raises(ValueError):
            loadJSON([1, 2, 3])


class TestProcessJSONToPandas:

    def test_flat_json(self):
        data = {"a": 1, "b": 2}
        result = processJSONToPandas(data)
        assert isinstance(result, pandas.DataFrame)
        assert len(result) == 2

    def test_nested_json(self):
        data = {"parent": {"child1": 1, "child2": 2}}
        result = processJSONToPandas(data)
        assert isinstance(result, pandas.DataFrame)
        assert len(result) == 2

    def test_list_values_are_expanded(self):
        data = {"items": [10, 20, 30]}
        result = processJSONToPandas(data)
        assert len(result) == 3

    def test_custom_column_names(self):
        data = {"x": 1}
        result = processJSONToPandas(data, nameColumn="path", valueColumn="val")
        assert "path" in result.columns
        assert "val" in result.columns


class TestConvertJSONtoPandas:

    def test_flat_json(self):
        data = {"a": 1, "b": 2}
        result = convertJSONtoPandas(data)
        assert isinstance(result, pandas.DataFrame)

    def test_accepts_file_path(self, tmp_path):
        filepath = tmp_path / "test.json"
        filepath.write_text('{"x": 1, "y": 2}')
        result = convertJSONtoPandas(str(filepath))
        assert isinstance(result, pandas.DataFrame)
