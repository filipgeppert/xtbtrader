from typing import TypedDict
import time
import pandas as pd
import os
from settings import BASE_PATH
from decimal import Decimal, getcontext


class TransactionCommand:
    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5
    BALANCE = 6
    CREDIT = 7


class TransactionType:
    ORDER_OPEN = 0
    # order pending, only used in the streaming getTrades  command
    ORDER_PENDING = 1
    ORDER_CLOSE = 2
    # order modify, only used in the tradeTransaction command
    ORDER_MODIFY = 3
    # order delete, only used in the tradeTransaction command
    ORDER_DELETE = 4


class TransactionStatus:
    ERROR = 0
    PENDING = 1
    ACCEPTED = 3
    REJECTED = 4


class TransactionInfo(TypedDict):
    cmd: TransactionCommand
    customComment: str
    expiration: int
    offset: int
    # 0 or position number for closing/modifications
    order: int
    price: float
    sl: float
    symbol: str
    tp: float
    type: TransactionType
    volume: float


def create_transaction_info(
        command: TransactionCommand,
        symbol: str,
        ttype: TransactionType,
        expiration_offset_hours=1,
        custom_comment="",
        offset=0,
        order=0,
        price=False,
        stop_loss=False,
        take_profit=False,
        volume=False,
    ) -> TransactionInfo:
    getcontext().prec = 2
    ti = dict()
    ti['cmd'] = command
    ti['customComment'] = custom_comment
    ti['type'] = ttype
    ti['expiration'] = int(time.time() * 1000) + expiration_offset_hours * 60 * 60 * 1000
    ti['order'] = order
    ti['symbol'] = symbol
    ti['offset'] = offset
    ti['price'] = round(price, 2)
    ti['sl'] = round(stop_loss, 2)
    ti['tp'] = round(take_profit if take_profit else price * 2, 2)
    ti['volume'] = round(volume, 2)
    return ti


def calculate_bid_price(*args):
    candidates = [a for a in args if a > 0]
    return min(candidates)


def read_trades():
    df = pd.read_csv(os.path.join(BASE_PATH, 'data', 'trades.csv'), dtype=
                        {"volume": float, "symbol": str, "commmand": str, "sl_strategy": str, "order": int}
                     )
    return df
