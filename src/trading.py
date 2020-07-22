import pandas as pd
from enum import Enum
import numpy as np


class StrategyLoss(Enum):
    AGGRESSIVE = 0.5
    DEFAULT = 0.7
    SAFE = 0.9


class StrategyProfit(Enum):
    AGGRESSIVE = 3.0
    DEFAULT = 1.5
    SAFE = 1.3


class Trader:
    def __init__(self, trades, balance_data):
        self.trades = pd.DataFrame(trades)
        self.stocks_hold = ['EURUSD']
        self.balance = balance_data['balance']
        self.currency = balance_data['currency']
        self.margin = balance_data['margin']
        self.margin_free = balance_data['margin_free']
        self.calculate_stop_loss(strategy=StrategyLoss.DEFAULT)
        self.calculate_take_profit(strategy=StrategyProfit.DEFAULT)

    def calculate_stop_loss(self, strategy: StrategyLoss):
        trades_profitable = self.trades.profit > 0
        self.trades['sl_new'] = np.nan
        self.trades.loc[trades_profitable, 'sl_new'] = (
                self.trades.loc[trades_profitable, 'close_price'] * strategy.value
        )
        self.trades.loc[~trades_profitable, 'sl_new'] = (
                self.trades.loc[~trades_profitable, 'open_price'] * strategy.value
        )

    def calculate_take_profit(self, strategy: StrategyProfit):
        self.trades['tp_new'] = self.trades['open_price'] * strategy.value

    def get_trade_details(self, order_id: int):
        t = self.trades.loc[self.trades['order'] == order_id].T.squeeze()
        return t
