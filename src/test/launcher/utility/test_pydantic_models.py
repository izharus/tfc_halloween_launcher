"""Tests for src/launcher/utillity/pydantic_models.py"""
import pydantic
import pytest
from src.launcher.utility.pydantic_models import MapJson


def test_map_json_empty_modpacks_variable():
    """Unsure that modpacks variable could not be empty."""
    with pytest.raises(pydantic.ValidationError):
        MapJson(**{})
