import pytest
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from src.api.review import router
from redis.asyncio import Redis


@pytest.fixture
def test_app():
    # test app
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def test_client(test_app):
    # test client
    return TestClient(test_app)


@pytest.fixture
def mock_redis():
    redis_mock = AsyncMock(spec=Redis)
    redis_mock.get.return_value = json.dumps({
        "found_files": ["file1.py"],
        "review_result": {"review": "Good code"}
    })
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = True
    return redis_mock