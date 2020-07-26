from src.trading import Trader


def test_get_order_data(trader):
    d = trader.get_trade_details(212828097)
    assert d['cmd'] == 0
    assert d['symbol'] == "ORCL.US_4"


def test_sl_calculation(balance, trades):
    sl_new = trades[0]['open_price'] * 0.9
    trades[0]['sl'] = sl_new
    t = Trader(trades=trades, balance_data=balance)
    assert t.get_trade_details(trades[0]['order'])['sl_new'] == sl_new


