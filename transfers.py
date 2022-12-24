from web3 import Web3
from termcolor import cprint
import time
import json
import random
from tqdm import tqdm
import decimal
import requests
from tabulate import tabulate
from decimal import Decimal
from config import *

table = []
def transfer_token(privatekey, amount_to_transfer, to_address, chain_id, scan, rpc_chain, address_contract, ERC20_ABI):
    try:

        web3 = Web3(Web3.HTTPProvider(rpc_chain))

        token_contract = web3.eth.contract(address=Web3.toChecksumAddress(address_contract), abi=ERC20_ABI)
        account = web3.eth.account.privateKeyToAccount(privatekey)
        address = account.address
        nonce = web3.eth.get_transaction_count(address)

        symbol = token_contract.functions.symbol().call()
        token_decimal = token_contract.functions.decimals().call()

        amount = intToDecimal(amount_to_transfer, token_decimal) 

        gasLimit = web3.eth.estimate_gas({'to': Web3.toChecksumAddress(address), 'from': Web3.toChecksumAddress(to_address),'value': web3.toWei(0.0001, 'ether')}) 
        gasPrice = web3.eth.gas_price

        if chain_id == 1:

            contract_txn = token_contract.functions.transfer(
                Web3.toChecksumAddress(to_address),
                int(amount)
                ).buildTransaction({
                    'type': '0x2',
                    'chainId': chain_id,
                    'gas': gasLimit,
                    'maxFeePerGas': random.randrange(20000000000, 25000000000, 9), 
                    # 'maxFeePerGas': web3.to_wei('25', 'gwei'),
                    'maxPriorityFeePerGas': web3.to_wei('1.5', 'gwei'),
                    'nonce': nonce,
                })
        
        else:

            contract_txn = token_contract.functions.transfer(
                Web3.toChecksumAddress(to_address),
                int(amount)
                ).buildTransaction({
                    'chainId': chain_id,
                    'gasPrice': gasPrice,
                    'gas': gasLimit,
                    'nonce': nonce,
                })

        tx_signed = web3.eth.account.signTransaction(contract_txn, privatekey)
        tx_hash = web3.eth.sendRawTransaction(tx_signed.rawTransaction)

        cprint(f'\n>>> transfer : {decimal.Decimal(str(amount_to_transfer))} {symbol} | {address} => {to_address} | {scan}/{web3.toHex(tx_hash)}', 'green')
        table.append([f'{decimal.Decimal(str(amount_to_transfer))} {symbol}', address, to_address, '\u001b[32msend\u001b[0m'])

    except Exception as error:
        cprint(f'\n>>> transfer : {privatekey} | {error}', 'red')
        try:
            table.append([f'{decimal.Decimal(str(amount_to_transfer))} {symbol}', address, to_address, '\u001b[31merror\u001b[0m'])
        except:
            table.append([f'{symbol}', address, to_address, '\u001b[31merror\u001b[0m'])
    
def transfer_eth(privatekey, amount_to_transfer, to_address, chain_id, scan, rpc_chain, symbol):
    try:

        web3 = Web3(Web3.HTTPProvider(rpc_chain))

        account = web3.eth.account.privateKeyToAccount(privatekey)
        address = account.address
        nonce = web3.eth.get_transaction_count(address)

        amount = intToDecimal(amount_to_transfer, 18) 

        gasLimit = web3.eth.estimate_gas({'to': Web3.toChecksumAddress(address), 'from': Web3.toChecksumAddress(address),'value': amount}) 
        gasPrice = web3.eth.gas_price
        
        if chain_id == 1:

            contract_txn = {
                'type': '0x2',
                'chainId': chain_id,
                'gas': gasLimit,
                'maxFeePerGas': random.randrange(20000000000, 25000000000, 9), 
                # 'maxFeePerGas': web3.to_wei('25', 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei('1.5', 'gwei'),
                'nonce': nonce,
                'to': Web3.toChecksumAddress(to_address),
                'value': int(amount)
            }
        
        else:

            contract_txn = {
                'chainId': chain_id,
                'gasPrice': gasPrice,
                'gas': gasLimit,
                'nonce': nonce,
                'to': Web3.toChecksumAddress(to_address),
                'value': int(amount)
            }

        tx_signed = web3.eth.account.signTransaction(contract_txn, privatekey)
        tx_hash = web3.eth.sendRawTransaction(tx_signed.rawTransaction)

        cprint(f'\n>>> transfer : {decimal.Decimal(str(amount_to_transfer))} {symbol} | {address} => {to_address} | {scan}/{web3.toHex(tx_hash)}', 'green')
        table.append([f'{decimal.Decimal(str(amount_to_transfer))} {symbol}', address, to_address, '\u001b[32msend\u001b[0m'])

    except Exception as error:
        cprint(f'\n>>> transfer : {privatekey} | {error}', 'red')
        try:
            table.append([f'{decimal.Decimal(str(amount_to_transfer))} {symbol}', address, to_address, '\u001b[31merror\u001b[0m'])
        except:
            table.append([f'{symbol}', address, to_address, '\u001b[31merror\u001b[0m'])


def transfer(privatekey, to_address, CHAIN, AMOUNT_TO_TRANSFER, ADDRESS_CONTRACT, MIN_BALANCE, MIN_AMOUNT):

    data = check_rpc(CHAIN)
    rpc_chain = data['rpc']
    chain_id = data['chain_id']
    scan = data['scan']
    symbol_chain = data['token']

    if ADDRESS_CONTRACT == '':

        if AMOUNT_TO_TRANSFER == 'all_balance':
            AMOUNT_TO_TRANSFER = check_balance(privatekey, rpc_chain, symbol_chain, MIN_BALANCE)

        if AMOUNT_TO_TRANSFER > MIN_AMOUNT:

            transfer_eth(
                privatekey, 
                AMOUNT_TO_TRANSFER, 
                to_address, 
                chain_id, 
                scan, 
                rpc_chain, 
                symbol_chain
            )

    else:

        if AMOUNT_TO_TRANSFER == 'all_balance':
            AMOUNT_TO_TRANSFER = check_token_balance(privatekey, rpc_chain, ADDRESS_CONTRACT, MIN_BALANCE)

        if AMOUNT_TO_TRANSFER > MIN_AMOUNT:

            transfer_token(
                privatekey, 
                AMOUNT_TO_TRANSFER, 
                to_address, 
                chain_id, 
                scan, 
                rpc_chain, 
                ADDRESS_CONTRACT,
                ERC20_ABI
            )

