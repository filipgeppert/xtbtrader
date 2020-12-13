from src.trading import Trader, create_transaction_info, TransactionCommand, TransactionType
import pytest


def test_get_order_data(trader):
    d = trader.get_trade_details(212828097)
    assert d['cmd'] == 0
    assert d['symbol'] == "ORCL.US_4"


def test_sl_calculation(balance, trades):
    sl_new = trades[0]['open_price'] * 0.9
    trades[0]['sl'] = sl_new
    t = Trader(trades=trades, balance_data=balance)
    assert t.get_trade_details(trades[0]['order'])['sl_new'] == sl_new


def test_create_transaction_info():
    ti = create_transaction_info(
        command=TransactionCommand.BUY_LIMIT,
        symbol="ABC",
        ttype=TransactionType.ORDER_OPEN,
        stop_loss=float(1.2912312),
        take_profit=1,
        volume=1.2090090
    )
    assert ti['sl'] == 1.29
    assert ti['tp'] == 1.00
    assert ti['volume'] == 1
