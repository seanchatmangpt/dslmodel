import io
import sys
from pathlib import Path

import pytest
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

# Mock Clock Fixture Example
class MockClock:
    def __init__(self):
        from datetime import datetime
        self.current = datetime(2023, 1, 1, tzinfo=pytz.UTC)

    def advance(self, delta):
        """Advance the clock by a timedelta."""
        self.current += delta

    def get_current_time(self):
        return self.current

@pytest.fixture
def mock_clock():
    """Provides a mock clock for testing."""
    return MockClock()

@pytest.fixture
def scheduler(mock_clock):
    """Provides a scheduler that uses the mock clock."""
    scheduler = BackgroundScheduler(timezone=pytz.UTC, timefunc=mock_clock.get_current_time)
    yield scheduler
    scheduler.shutdown()


# Helper fixture to capture output from print statements
@pytest.fixture
def captured_output():
    return io.StringIO()


# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))
