import asyncio

import pytest


async def some_async_setup():
    await asyncio.sleep(0.1)  # Simulate setup work


async def some_async_teardown():
    await asyncio.sleep(0.1)  # Simulate teardown work


@pytest.fixture
async def async_resource():
    await some_async_setup()
    yield "data"
    await some_async_teardown()


async def test_with_async_fixture(async_resource):
    assert async_resource == "data"
