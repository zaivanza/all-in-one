import time
import json
import ccxt
from ccxt.base.errors import InvalidAddress, InvalidOrder, ExchangeError
from termcolor import cprint
import random
from config import *

def binance_withdraw(address_wallet, amount_to_withdraw, symbol_to_withdraw, network):


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



