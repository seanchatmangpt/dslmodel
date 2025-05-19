import io
import sys
from pathlib import Path

import pytest
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
import httpx
from unittest.mock import AsyncMock

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

@pytest.fixture(autouse=True)
def mock_groq_api(monkeypatch):
    async def fake_post(self, url, *args, **kwargs):
        # Simulate a plausible Groq API response
        # The structure should match what litellm/pydantic_ai expects
        class FakeResponse:
            status_code = 200
            def json(self):
                # Return a plausible LLM completion structure
                return {
                    "choices": [
                        {"message": {"content": '{"next_trigger": "start", "explanation": "Mocked explanation.", "task": "Task 1", "result": "Mocked result."}'}}
                    ]
                }
            async def aread(self):
                return b''
            async def aclose(self):
                pass
        return FakeResponse()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
