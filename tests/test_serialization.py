"""
Tests for toJSON serialization and __str__/__repr__.
"""

import json
import pytest
from argos.experimentSetup.dataObjectsFactory import fileExperimentFactory


@pytest.fixture
def groups_exp(exp_groups_path):
    return fileExperimentFactory(exp_groups_path).getExperiment()


class TestTrialSetToJSON:

    def test_to_json_returns_dict(self, groups_exp):
        ts = groups_exp.trialSet["New Trial Type"]
        result = ts.toJSON()
        assert isinstance(result, dict)

    def test_to_json_has_name(self, groups_exp):
        ts = groups_exp.trialSet["New Trial Type"]
        result = ts.toJSON()
        assert result["name"] == "New Trial Type"

    def test_to_json_has_trials(self, groups_exp):
        ts = groups_exp.trialSet["New Trial Type"]
        result = ts.toJSON()
        assert "trials" in result
        assert "New Trial" in result["trials"]

    def test_to_json_has_properties(self, groups_exp):
        ts = groups_exp.trialSet["New Trial Type"]
        result = ts.toJSON()
        assert "properties" in result


class TestTrialToJSON:

    def test_to_json_returns_dict(self, groups_exp):
        trial = groups_exp.trialSet["New Trial Type"]["New Trial"]
        result = trial.toJSON()
        assert isinstance(result, dict)

    def test_to_json_has_name(self, groups_exp):
        trial = groups_exp.trialSet["New Trial Type"]["New Trial"]
        result = trial.toJSON()
        assert result["name"] == "New Trial"

    def test_str_is_valid_json(self, groups_exp):
        trial = groups_exp.trialSet["New Trial Type"]["New Trial"]
        parsed = json.loads(str(trial))
        assert isinstance(parsed, dict)

    def test_repr_is_valid_json(self, groups_exp):
        trial = groups_exp.trialSet["New Trial Type"]["New Trial"]
        parsed = json.loads(repr(trial))
        assert "name" in parsed


class TestEntityTypeToJSON:

    @pytest.mark.xfail(reason="Entity.toJSON() calls self.entityType.name but entityType is a str, not EntityType object", strict=True)
    def test_to_json_returns_dict(self, groups_exp):
        et = groups_exp.entityType["New Device Type"]
        result = et.toJSON()
        assert isinstance(result, dict)

    @pytest.mark.xfail(reason="Entity.toJSON() calls self.entityType.name but entityType is a str", strict=True)
    def test_to_json_has_entities(self, groups_exp):
        et = groups_exp.entityType["New Device Type"]
        result = et.toJSON()
        assert "entities" in result
        assert "New Device" in result["entities"]

    @pytest.mark.xfail(reason="Entity.toJSON() calls self.entityType.name but entityType is a str", strict=True)
    def test_to_json_has_properties(self, groups_exp):
        et = groups_exp.entityType["New Device Type"]
        result = et.toJSON()
        assert "properties" in result
