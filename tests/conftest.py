from src.clients import APIClient, JsonSocket, APIStreamClient
import time
from unittest.mock import Mock
from pytest_mock import mocker
import logging
import pytest
from src.trading import Trader

trade_data = [
    {
        "cmd": 0,
        "order": 212828097,
        "digits": 2,
        "offset": 0,
        "order2": 212828091,
        "position": 212828097,
        "symbol": "ORCL.US_4",
        "comment": "",
        "customComment": None,
        "commission": -6.0,
        "storage": -0.42,
        "margin_rate": 0.0,
        "close_price": 56.07,
        "open_price": 56.19,
        "nominalValue": 0.0,
        "profit": -12.0,
        "volume": 100.0,
        "sl": 0.0,
        "tp": 0.0,
        "closed": False,
        "timestamp": 1595435193892,
        "spread": 0,
        "taxes": 0.0,
        "open_time": 1595354069000,
        "open_timeString": "Tue Jul 21 19:54:29 CEST 2020",
        "close_time": None,
        "close_timeString": None,
        "expiration": None,
        "expirationString": None
    }
]

balance_data = {'balance': 99961.63,
                'margin': 19649.43,
                'currency': 'USD',
                'credit': 0.0,
                'equityFX': 100693.88,
                'equity': 100693.88,
                'margin_free': 80312.2,
                'margin_level': 512.45,
                'stockValue': 0.0,
                'stockLock': 0.0,
                'cashStockValue': 0.0
                }


@pytest.fixture
def balance():
    return balance_data


@pytest.fixture
def trades():
    return trade_data


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

    @staticmethod
    def getTrades(*args, **kwargs):
        return [{
            "close_price": 1.3256,
            "close_time": None,
            "close_timeString": None,
            "closed": False,
            "cmd": 0,
            "comment": "Web Trader",
            "commission": 0.0,
            "customComment": "Some text",
            "digits": 4,
            "expiration": None,
            "expirationString": None,
            "margin_rate": 0.0,
            "offset": 0,
            "open_price": 1.4,
            "open_time": 1272380927000,
            "open_timeString": "Fri Jan 11 10:03:36 CET 2013",
            "order": 7497776,
            "order2": 1234567,
            "position": 1234567,
            "profit": -2196.44,
            "sl": 0.0,
            "storage": -4.46,
            "symbol": "EURUSD",
            "timestamp": 1272540251000,
            "tp": 0.0,
            "volume": 0.10
        }]


@pytest.fixture
def api_client(monkeypatch):
    def mock_get_current_tick_price(*args, **kwargs):
        return MockResponse.getCurrentTickPrice(*args, **kwargs)

    def mock_get_trades(*args, **kwargs):
        return MockResponse.getTrades(*args, **kwargs)

    monkeypatch.setattr(APIClient, "getCurrentTickPrice", mock_get_current_tick_price)
    monkeypatch.setattr(APIClient, "getTrades", mock_get_trades)
    logger = logging.getLogger("jsonSocket")
    api_client = APIClient(logger)
    return api_client


@pytest.fixture()
def trader(balance, trades):
    return Trader(trades=trades, balance_data=balance_data)
