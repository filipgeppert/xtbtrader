from src.clients import APIClient, JsonSocket, APIStreamClient
import time
from unittest.mock import Mock
from pytest_mock import mocker
import logging
import pytest


class MockResponse:
    @staticmethod
    def getCurrentTickPrice(*args, **kwargs):
        return {'symbol': kwargs['ticker'],
                'ask': 6.097,
                'bid': 5.865,
                'high': 5.973,
                'low': 5.835,
                'askVolume': 784,
                'bidVolume': 172,
                'timestamp': int(time.time() * 1000),
                'level': 0,
                'exemode': 1,
                'spreadRaw': 0.232,
                'spreadTable': 232.0}


@pytest.fixture
def api_client(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse.getCurrentTickPrice(*args, **kwargs)

    monkeypatch.setattr(APIClient, "getCurrentTickPrice", mock_get)
    logger = logging.getLogger("jsonSocket")
    api_client = APIClient(logger)
    return api_client

