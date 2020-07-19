from src.clients import APIClient, JsonSocket, APIStreamClient
import time
from unittest.mock import Mock
from pytest_mock import mocker
import logging
import pytest
from src.transactions import calculate_bid_price


def test_get_current_tick_price_a(api_client):
    r = api_client.getCurrentTickPrice(ticker="BITCOIN")
    assert r['symbol'] == "BITCOIN"


@pytest.mark.parametrize("test_input,expected", [
    ([0, 1, 1], 1),
    ([1, 2], 1),
])
def test_calculate_bid_price(test_input, expected):
    assert calculate_bid_price(*test_input) == expected

