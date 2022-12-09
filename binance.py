import time
import json
import ccxt
from ccxt.base.errors import InvalidAddress, InvalidOrder, ExchangeError
from termcolor import cprint
from web3 import Web3
import random
from config import *

def binance_withdraw(privatekey, amount_to_withdraw, symbol_to_withdraw, network):

    if len(privatekey) > 50:
        web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
        address_wallet = web3.eth.account.privateKeyToAccount(privatekey).address
    else:
        address_wallet = privatekey

    account_binance = ccxt.binance({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'spot'
        }
    })

    try:

        account_binance.withdraw(
            code = symbol_to_withdraw,
            amount = amount_to_withdraw,
            address = address_wallet,
            tag = None, 
            params = {
                "network": network
            }
        )
        cprint(f">>> Успешно | {address_wallet} | {amount_to_withdraw}", "green")
    except ExchangeError as error:
        cprint(f">>> Неудачно | {address_wallet} | ошибка : {error}", "red")



