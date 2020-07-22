
def test_get_order_data(trader):
    d = trader.get_trade_details(212828097)
    assert d['cmd'] == 0
    assert d['symbol'] == "ORCL.US_4"

