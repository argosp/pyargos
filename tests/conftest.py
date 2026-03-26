"""
Shared fixtures for experimentSetup tests.

Each fixture loads a different example experiment to test
different features (simple, groups with containment, no attributes,
v2.0.0 format).
"""

import os
import pytest

EXAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "argos", "experimentSetup", "example_exp")


@pytest.fixture
def exp_simple_path():
    """Path to the simple experiment (v3.0.0, multiple device types, no devices on trial)."""
    return os.path.join(EXAMPLE_DIR, "exp_simple")


@pytest.fixture
def exp_groups_path():
    """Path to the groups experiment (v3.0.0, containment, attributes on trial)."""
    return os.path.join(EXAMPLE_DIR, "exp_groups")


@pytest.fixture
def exp_groups_noattr_path():
    """Path to the groups experiment without attributes (v3.0.0, containment, no attributes)."""
    return os.path.join(EXAMPLE_DIR, "exp_groups_noattr")


@pytest.fixture
def raptor_zip_path():
    """Path to the Raptor2023 ZIP file (v2.0.0 format)."""
    return os.path.join(EXAMPLE_DIR, "Raptor2023.zip")


@pytest.fixture
def haifa_zip_path():
    """Path to the Haifa2014 ZIP file (v3.0.0 format)."""
    return os.path.join(EXAMPLE_DIR, "experiment_Haifa2014.zip")
