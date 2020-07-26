import pandas as pd
from enum import Enum
import numpy as np
from src.clients import APIClient
from src.transactions import create_transaction_info, TransactionType, TransactionCommand, TransactionInfo, \
    calculate_bid_price, read_trades

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
        # If we don't have any transactions
        if not self.trades.empty:
            self._calculate_stop_loss(strategy=StrategyLoss.DEFAULT)
            self._calculate_take_profit(strategy=StrategyProfit.DEFAULT)

    def _calculate_stop_loss(self, strategy: StrategyLoss):
        trades_profitable = self.trades.profit > 0
        self.trades['sl_new'] = np.nan
        # Calculate new stop loss according to strategy
        self.trades.loc[trades_profitable, 'sl_new'] = (
                self.trades.loc[trades_profitable, 'close_price'] * strategy.value
        )
        self.trades.loc[~trades_profitable, 'sl_new'] = (
                self.trades.loc[~trades_profitable, 'open_price'] * strategy.value
        )
        # Take current stop loss, if it was historically higher
        sl_old_higher = self.trades['sl'] > self.trades['sl_new']
        self.trades.loc[sl_old_higher, 'sl_new'] = (
                self.trades.loc[sl_old_higher, 'sl']
        )

    def _calculate_take_profit(self, strategy: StrategyProfit):
        self.trades['tp_new'] = self.trades['open_price'] * strategy.value

    def get_trade_details(self, order_id: int):
        t = self.trades.loc[self.trades['order'] == order_id].T.squeeze()
        return t

    def close_transaction(self, client: APIClient, order_id: int):
        trade_details = self.get_trade_details(order_id=order_id)
        transaction_info: TransactionInfo = create_transaction_info(
            command=TransactionCommand.SELL,
            symbol=trade_details['symbol'],
            ttype=TransactionType.ORDER_CLOSE,
            price=trade_details['close_price'],
            volume=trade_details['volume'],
            stop_loss=0,
            take_profit=0,
            custom_comment=f"Selling {trade_details['symbol']} - {trade_details['close_price']}",
            order=order_id,
        )
        return client.tradeTransaction(transaction_info)

    def updateStopLossTakeProfit(self, client: APIClient):
        for i, transaction_data in self.trades.iterrows():
            transaction_info: TransactionInfo = create_transaction_info(
                command=transaction_data['cmd'],
                symbol=transaction_data['symbol'],
                ttype=TransactionType.ORDER_MODIFY,
                price=transaction_data['open_price'],
                volume=transaction_data['volume'],
                stop_loss=transaction_data['sl_new'],
                take_profit=transaction_data['tp_new'],
                custom_comment=f"SL/ TP updated {transaction_data['symbol']}",
                order=transaction_data['order'],
            )
            client.tradeTransaction(transaction_info)
