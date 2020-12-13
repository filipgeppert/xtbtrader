import json
import socket
import logging
import time
import ssl
import os
from threading import Thread
import pandas as pd
from datetime import datetime
from settings import DEBUG, BASE_PATH
from src.commands import loginCommand
from src.clients import APIClient, APIStreamClient
from src.trading import Trader, StrategyLoss, StrategyProfit
from src.transactions import create_transaction_info, TransactionType, TransactionCommand, TransactionInfo, \
    calculate_bid_price, read_trades
from environs import Env


def create_logger():
    # logger properties
    logger = logging.getLogger("jsonSocket")
    FORMAT = '[%(asctime)-15s][%(funcName)s:%(lineno)d] %(message)s'
    logging.basicConfig(format=FORMAT)

    file_handler = logging.FileHandler(
        os.path.join(BASE_PATH, 'logs', f"{datetime.now().strftime('%m-%d-%Y-%H-%M-%S')}.log")
    )

    if DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL)

    logger.addHandler(file_handler)
    return logger


def connect(user_id: int, password: str, logger) -> APIClient:
    # create & connect to RR socket
    client = APIClient(logger)

    # connect to RR socket, login
    loginResponse = client.execute(loginCommand(userId=user_id, password=password))
    logger.info(str(loginResponse))

    # check if user logged in correctly
    if loginResponse['status'] == False:
        print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
        raise
    return client


def openTransaction(client: APIClient,
                    symbol: str,
                    volume: float):
    # Get current ticker data
    current_data = client.getCurrentTickPrice(ticker=symbol)
    price = calculate_bid_price(current_data['ask'], current_data['high'])

    transaction_info: TransactionInfo = create_transaction_info(
        command=TransactionCommand.BUY_LIMIT,
        symbol=symbol,
        ttype=TransactionType.ORDER_OPEN,
        price=price,
        volume=volume,
        stop_loss=int(price*StrategyLoss.DEFAULT.value),
        take_profit=int(price*StrategyProfit.DEFAULT.value),
        custom_comment=f"{symbol} - {price}"
    )
    return client.tradeTransaction(transaction_info)


def main():
    logger = create_logger()
    # read login credentials
    env = Env()
    env.read_env()
    user_id = env.str("userId")
    password = env.str("password")
    # read action list
    df_actions = read_trades()
    # establish connection
    client = connect(user_id, password, logger)
    trader = Trader(trades=client.getTrades(), balance_data=client.getMarginLevel())

    # Start daily trading
    # buy new stocks if there is anything on the list
    df_actions_buy = df_actions.query('command == "buy"')
    for i, row in df_actions_buy.iterrows():
        resp = openTransaction(client=client, symbol=row['symbol'], volume=row['volume'])
        status = client.tradeTransactionStatus(order=resp['returnData']['order'])

    # Sell stocks if there is anything to sell on the list
    df_actions_sell = df_actions.query('command == "sell"')
    for i, row in df_actions_sell.iterrows():
        assert row['command'] == "sell"
        resp = trader.close_transaction(client=client, order_id=row['order'])
        status = client.tradeTransactionStatus(order=resp['returnData']['order'])

    # By default we want to keep our stocks and only update stop loss / take profit
    trader.updateStopLossTakeProfit(client)

    # gracefully close RR socket
    client.disconnect()


def download_symbols():
    today = datetime.now().strftime("%d-%m-%Y")
    logger = create_logger()
    # read login credentials
    env = Env()
    env.read_env()
    user_id = env.str("userId")
    password = env.str("password")
    # read action list
    df_actions = read_trades()
    # establish connection
    client = connect(user_id, password, logger)
    symbols = client.getAllSymbols()
    df_symbols = pd.DataFrame(symbols)
    df_symbols.to_csv(os.path.join('data', 'symbols', f'{today}.csv'), index=False)

if __name__ == "__main__":
    # main()
    download_symbols()
