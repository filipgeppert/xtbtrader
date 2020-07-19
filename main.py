import json
import socket
import logging
import time
import ssl
from threading import Thread
import pandas as pd
from settings import DEBUG
from src.commands import loginCommand
from src.clients import APIClient, APIStreamClient
from src.transactions import create_transaction_info, TransactionType, TransactionCommand, TransactionInfo, \
    calculate_bid_price
from environs import Env


def create_logger():
    # logger properties
    logger = logging.getLogger("jsonSocket")
    FORMAT = '[%(asctime)-15s][%(funcName)s:%(lineno)d] %(message)s'
    logging.basicConfig(format=FORMAT)

    if DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.CRITICAL)
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


def makeTransaction(client: APIClient,
                    symbol: str,
                    volume: float):
    # Get current ticker data
    current_data = client.getCurrentTickPrice(ticker=symbol)
    price = calculate_bid_price(current_data['ask'], current_data['high'])

    transaction_info: TransactionInfo = create_transaction_info(
        command=TransactionCommand.BUY,
        symbol=symbol,
        ttype=TransactionType.ORDER_OPEN,
        price=price,
        volume=volume,
        stop_loss=0.0,
        take_profit=0.0,
        custom_comment=f"{symbol} - {price}"
    )
    return client.tradeTransaction(transaction_info)


def main():
    logger = create_logger()
    # read login credentials
    env = Env()
    env.read_env()
    user_id = env.int("userId")
    password = env.str("password")
    # establish connection
    client = connect(user_id, password, logger)

    # Buy some stocks
    resp = makeTransaction(client, "ETHERCLASSIC", 10.0)
    status = client.tradeTransactionStatus(order=resp['returnData']['order'])

    # gracefully close RR socket
    client.disconnect()


if __name__ == "__main__":
    main()
