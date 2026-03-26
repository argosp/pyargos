"""
Tests for TrialSet and Trial classes.
"""

import pandas
import pytest
from argos.experimentSetup.dataObjectsFactory import fileExperimentFactory


@pytest.fixture
def simple_exp(exp_simple_path):
    return fileExperimentFactory(exp_simple_path).getExperiment()


@pytest.fixture
def groups_exp(exp_groups_path):
    return fileExperimentFactory(exp_groups_path).getExperiment()


# --- Trial Sets ---

class TestTrialSets:

    def test_simple_has_two_trial_sets(self, simple_exp):
        assert len(simple_exp.trialSet) == 2

    def test_trial_set_names(self, simple_exp):
        names = set(simple_exp.trialSet.keys())
        assert "New Trial Type" in names
        assert "New Trial Type 1" in names

    def test_trial_set_dict_access(self, simple_exp):
        ts = simple_exp.trialSet["New Trial Type"]
        assert ts.name == "New Trial Type"

    def test_trial_set_experiment_reference(self, simple_exp):
        ts = simple_exp.trialSet["New Trial Type"]
        assert ts.experiment is simple_exp

    def test_trial_set_has_properties(self, simple_exp):
        ts = simple_exp.trialSet["New Trial Type"]
        assert isinstance(ts.properties, list)

    def test_trial_set_properties_table(self, simple_exp):
        ts = simple_exp.trialSet["New Trial Type"]
        assert isinstance(ts.propertiesTable, pandas.DataFrame)

    def test_groups_has_one_trial_set(self, groups_exp):
        assert len(groups_exp.trialSet) == 1

    def test_trial_set_has_name_in_metadata(self, simple_exp):
        """Trial set metadata should have a name field."""
        ts = simple_exp.trialSet["New Trial Type"]
        assert "name" in ts._metadata


# --- Trials ---

class TestTrials:

    def test_simple_trial_count(self, simple_exp):
        """New Trial Type has 3 trials."""
        ts = simple_exp.trialSet["New Trial Type"]
        assert len(ts) == 3

    def test_trial_names(self, simple_exp):
        ts = simple_exp.trialSet["New Trial Type"]
        names = set(ts.keys())
        assert "New Trial" in names
        assert "New Trial 1" in names
        assert "New Trial 1 cloned" in names

    def test_trial_dict_access(self, simple_exp):
        trial = simple_exp.trialSet["New Trial Type"]["New Trial"]
        assert trial.name == "New Trial"

    def test_trial_set_reference(self, simple_exp):
        trial = simple_exp.trialSet["New Trial Type"]["New Trial"]
        assert trial.trialSet is simple_exp.trialSet["New Trial Type"]

    def test_trial_experiment_reference(self, simple_exp):
        trial = simple_exp.trialSet["New Trial Type"]["New Trial"]
        assert trial.experiment is simple_exp

    def test_trial_has_created_date(self, simple_exp):
        """Trial metadata should have a createdDate field."""
        trial = simple_exp.trialSet["New Trial Type"]["New Trial"]
        assert "createdDate" in trial._metadata

    def test_trial_properties_is_dict(self, simple_exp):
        trial = simple_exp.trialSet["New Trial Type"]["New Trial"]
        assert isinstance(trial.properties, dict)

    def test_trial_properties_table(self, simple_exp):
        trial = simple_exp.trialSet["New Trial Type"]["New Trial"]
        assert isinstance(trial.propertiesTable, pandas.DataFrame)

    def test_empty_trial_set(self, simple_exp):
        """New Trial Type 1 has no trials."""
        ts = simple_exp.trialSet["New Trial Type 1"]
        assert len(ts) == 0


# --- Trial with devices ---

class TestTrialWithDevices:

    def test_groups_trial_has_entities(self, groups_exp):
        trial = groups_exp.trialSet["New Trial Type"]["New Trial"]
        entities = trial.entities
        assert isinstance(entities, dict)
        assert len(entities) > 0

    def test_groups_trial_entities_table(self, groups_exp):
        trial = groups_exp.trialSet["New Trial Type"]["New Trial"]
        df = trial.entitiesTable
        assert isinstance(df, pandas.DataFrame)
        assert len(df) > 0

    def test_groups_trial_entity_has_attributes(self, groups_exp):
        """New Device in the trial should have attributes 'one' and 'two'."""
        trial = groups_exp.trialSet["New Trial Type"]["New Trial"]
        entities = trial.entities
        assert "New Device" in entities
        device_props = entities["New Device"]
        assert "one" in device_props
        assert "two" in device_props

    def test_groups_trial_entity_attribute_values(self, groups_exp):
        """Attribute values should match the JSON."""
        trial = groups_exp.trialSet["New Trial Type"]["New Trial"]
        device_props = trial.entities["New Device"]
        assert device_props["one"] == "1"
        assert device_props["two"] == "3"


# --- Trials table ---

class TestTrialsTable:

    def test_trials_table(self, simple_exp):
        ts = simple_exp.trialSet["New Trial Type"]
        df = ts.trialsTable
        assert isinstance(df, pandas.DataFrame)
        assert len(df) == 3

    def test_trials_table_all_sets(self, simple_exp):
        df = simple_exp.trialsTableAllSets
        assert isinstance(df, pandas.DataFrame)
        assert "trialSet" in df.columns

    def test_trials_table_method(self, simple_exp):
        df = simple_exp.trialsTable("New Trial Type")
        assert isinstance(df, pandas.DataFrame)
        assert len(df) == 3
