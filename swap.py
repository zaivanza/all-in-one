from web3 import Web3
from termcolor import cprint
import time
import json
import random
import requests
from config import *

def get_api_call_data(url):
    try: 
        call_data = requests.get(url)
    except Exception as e:
        print(e)
        return get_api_call_data(url)
    try:
        api_data = call_data.json()
        return api_data
    except Exception as e: 
        print(call_data.text) 

def inch_approve(web3, privatekey, address_wallet, amount_to_swap, from_token_address, symbol, scan, chain_id, nonce):
    try:

        _1inchurl = f'https://api.1inch.io/v4.0/{chain_id}/approve/transaction?tokenAddress={from_token_address}&amount={amount_to_swap}'
        json_data = get_api_call_data(_1inchurl)

        tx = {
            "nonce": nonce,
            "to": web3.toChecksumAddress(json_data["to"]),
            "data": json_data["data"],
            "gasPrice": web3.eth.gas_price,
            "gas": web3.eth.estimate_gas({'to': Web3.toChecksumAddress(address_wallet), 'from': Web3.toChecksumAddress(address_wallet),'value': web3.toWei(0.0001, 'ether')}) + random.randint(50000, 100000),
        }

        signed_tx = web3.eth.account.signTransaction(tx, privatekey)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        cprint(f'\n>>> approve {symbol} : {scan}/{web3.toHex(tx_hash)}', 'green')
    except Exception as error:
        cprint(f'\n>>> approve {address_wallet} | {symbol} | {error}', 'red')

table = []
def inch_sell(rpc_chain, privatekey, amount, from_token_address, to_token_address, ERC20_ABI, scan, chain_id):
    try:

        web3 = Web3(Web3.HTTPProvider(rpc_chain))
        account = web3.eth.account.privateKeyToAccount(privatekey)
        address_wallet = account.address
        nonce = web3.eth.getTransactionCount(address_wallet)

        try:
            from_token_contract = web3.eth.contract(address=web3.toChecksumAddress(from_token_address), abi=ERC20_ABI) 
            from_symbol = from_token_contract.functions.symbol().call()
            from_token_decimal = from_token_contract.functions.decimals().call()
            amount_to_swap = intToDecimal(amount, from_token_decimal) 
            inch_approve(web3, privatekey, address_wallet, amount_to_swap, from_token_address, from_symbol, scan, chain_id, nonce)
            time.sleep(random.randint(10, 15))
            nonce = nonce+1
        except : 
            from_symbol = 'NATIVE_ETH'
            from_token_decimal = 18
            amount_to_swap = intToDecimal(amount, from_token_decimal) 

        try:
            to_token_contract = web3.eth.contract(address=web3.toChecksumAddress(to_token_address), abi=ERC20_ABI) 
            to_symbol = to_token_contract.functions.symbol().call()
        except : to_symbol = 'NATIVE_ETH'


        _1inchurl = f'https://api.1inch.io/v4.0/{chain_id}/swap?fromTokenAddress={from_token_address}&toTokenAddress={to_token_address}&amount={amount_to_swap}&fromAddress={address_wallet}&slippage=2'
        json_data = get_api_call_data(_1inchurl)

        tx = json_data['tx']
        tx['nonce'] = nonce
        tx['to'] = Web3.toChecksumAddress(tx['to'])
        tx['gasPrice'] = int(tx['gasPrice'])
        tx['value'] = int(tx['value'])
        signed_tx = web3.eth.account.signTransaction(tx, privatekey)
        tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

        table.append([address_wallet, '\u001b[32mswap\u001b[0m'])
        cprint(f'\n>>> swap {from_symbol} => {to_symbol} | {scan}/{web3.toHex(tx_hash)}', 'green')
    except Exception as error:
        cprint(f'\n>>> swap {from_symbol} => {to_symbol} | {address_wallet} | {error}', 'red')
        table.append([address_wallet, '\u001b[31mnot_swap\u001b[0m'])

def swaps(privatekey, CHAIN, FROM_TOKEN_ADDRESS, TO_TOKEN_ADDRESS, AMOUNT_TO_SWAP, MIN_BALANCE, MIN_AMOUNT):

    data = check_rpc(CHAIN)
    rpc_chain = data['rpc']
    chain_id = data['chain_id']
    scan = data['scan']
    symbol_chain = data['token']

    if TO_TOKEN_ADDRESS == '':
        TO_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE" # ETH

    if FROM_TOKEN_ADDRESS == '':
        FROM_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE" # ETH

    if AMOUNT_TO_SWAP == 'all_balance':

        if FROM_TOKEN_ADDRESS == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': # eth
            AMOUNT_TO_SWAP = check_balance(privatekey, rpc_chain, symbol_chain, MIN_BALANCE)

        else:
            AMOUNT_TO_SWAP = check_token_balance(privatekey, rpc_chain, FROM_TOKEN_ADDRESS, MIN_BALANCE)

    if AMOUNT_TO_SWAP > MIN_AMOUNT:

        inch_sell(rpc_chain, privatekey, AMOUNT_TO_SWAP, FROM_TOKEN_ADDRESS, TO_TOKEN_ADDRESS, ERC20_ABI, scan, chain_id)


