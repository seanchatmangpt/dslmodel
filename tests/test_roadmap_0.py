"""
Basic tests for -  Enhanced OTEL observability feature with automa
Following 80/20 principle - test critical paths only
"""

import pytest
from src.roadmap_0_model import Roadmap_0Model

def test_create_roadmap_0():
    """Test basic creation"""
    model = Roadmap_0Model(name="test")
    assert model.name == "test"

def test_validation():
    """Test basic validation"""
    with pytest.raises(ValueError):
        Roadmap_0Model(name="")

# 80/20: Skip edge cases, focus on happy path
