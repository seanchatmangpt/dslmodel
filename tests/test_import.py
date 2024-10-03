"""Test dslmodel."""

import dslmodel


def test_import() -> None:
    """Test that the app can be imported."""
    assert isinstance(dslmodel.__name__, str)
