import time
from termcolor import cprint
import random
from tabulate import tabulate

from swap import *
from transfers import *
from bridges import *
from config import *
from binance import *
from debank import checker_main


if __name__ == "__main__":

    cprint(RUN_TEXT, RUN_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth', RUN_COLOR)

    def check_balance():

        # закомментируй что-либо если не хочешь чтобы парсилась эта инфа
        func = [
            'protocols',
            'tokens',
            # 'nfts'
        ]
        
        # баланс монет выше этого числа в $ эквиваленте будут записаны в таблицу, если меньше, то только в total value
        MIN_TABLE_AMOUNT = 1 
        checker_main(func, MIN_TABLE_AMOUNT)

    def main():

        zero = -1
        for privatekey in KEYS_LIST:
            zero = zero + 1

            cprint(f'\n=============== start : {privatekey} ===============', 'white')

            usdc_optimism = '0x7f5c764cbc14f9669b88837ca1490cca17c31607'
            usdc_arbitrum = '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8'

            def swap_1inch():

                # ETH | OPTIMISM | BNB | MATIC | FTM | ARBITRUM | AVAXC 

                CHAIN = 'OPTIMISM' 
                FROM_TOKEN_ADDRESS = '0x7f5c764cbc14f9669b88837ca1490cca17c31607' # пусто, если eth
                TO_TOKEN_ADDRESS = '' # пусто, если eth
                # AMOUNT_TO_SWAP = 80
                AMOUNT_TO_SWAP = 'all_balance'
                # AMOUNT_TO_SWAP = round(random.uniform(25, 30), 0) # от 1 до 3, 5 цифр после точки
                # MIN_BALANCE = round(random.uniform(0.005, 0.01), 5) # останется FROM_TOKEN на балансе после свапа
                MIN_BALANCE = 0 # останется FROM_TOKEN на балансе после свапа
                MIN_AMOUNT = 0 # если AMOUNT_TO_SWAP меньше этого числа, тогда не свапаем
                swaps(privatekey, CHAIN, FROM_TOKEN_ADDRESS, TO_TOKEN_ADDRESS, AMOUNT_TO_SWAP, MIN_BALANCE, MIN_AMOUNT)

            def bridge_orbiter():

                # ETH | OPTIMISM | BNB | MATIC | FTM | ARBITRUM | NOVA | AVAXC
                
                FROM_CHAIN = 'ARBITRUM'
                TO_CHAIN = 'NOVA'
                # AMOUNT_TO_BRIDGE = 'all_balance'
                AMOUNT_TO_BRIDGE = round(random.uniform(0.03, 0.04), 6)
                # AMOUNT_TO_BRIDGE = 10
                MIN_BALANCE = 0 # останется токенов на балансе после бриджа
                orbiter_bridge(privatekey, FROM_CHAIN, TO_CHAIN, AMOUNT_TO_BRIDGE, MIN_BALANCE)

            def bridge_eth_arbitrum():
                AMOUNT_TO_BRIDGE = 'all_balance'
                # AMOUNT_TO_BRIDGE = round(random.uniform(0.03, 0.04), 6)
                # AMOUNT_TO_BRIDGE = 10
                MIN_BALANCE = round(random.uniform(0.025, 0.035), 6) # останется токенов на балансе после бриджа

            def transfer_tokens():

                # ETH | OPTIMISM | BNB | MATIC | FTM | ARBITRUM | NOVA | AVAXC

                to_address = RECEPIENTS[zero]

                CHAIN = 'OPTIMISM' 
                ADDRESS_CONTRACT = '' # пусто если eth

                # AMOUNT_TO_TRANSFER = round(random.uniform(1, 2), 3)
                # AMOUNT_TO_TRANSFER = 0.01
                AMOUNT_TO_TRANSFER = 'all_balance'
                MIN_BALANCE = round(random.uniform(0.015, 0.02), 6) # останется токенов на балансе после бриджа
                MIN_AMOUNT = 0.005 # если AMOUNT_TO_TRANSFER меньше этого числа, тогда не выводим

                transfer(privatekey, to_address, CHAIN, AMOUNT_TO_TRANSFER, ADDRESS_CONTRACT, MIN_BALANCE, MIN_AMOUNT)

            def binance():

                # ETH | BSC | AVAXC | MATIC | ARBITRUM | OPTIMISM | APT

                amm = random.randint(2, 6)
                amount_to_withdraw = round(random.uniform(0.21, 0.23), amm)
                # amount_to_withdraw = 0.001
                symbol = 'ETH'
                network = 'ARBITRUM'
                binance_withdraw(
                    privatekey, 
                    amount_to_withdraw, # amount_to_withdraw
                    symbol, # symbol_to_withdraw
                    network # network
                    )

            # swap_1inch()
            # sleeping(20, 30)

            # bridge_orbiter()
            # sleeping(20, 30)

            # bridge_eth_arbitrum()
            # sleeping(60, 140)

            # transfer_tokens()
            # sleeping(20, 30)

            # binance()

            
    check_balance()
    # main()



