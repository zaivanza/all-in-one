from web3 import Web3
from termcolor import cprint
import time
import json
import random
from tqdm import tqdm
import decimal
from config import *

def bridge(privatekey, amount, RPC, chain_id, scan):

    try:

        web3 = Web3(Web3.HTTPProvider(RPC))
        account = web3.eth.account.privateKeyToAccount(privatekey)
        address_wallet = account.address

        nonce = web3.eth.get_transaction_count(address_wallet)

        contract_txn = {
            'chainId': chain_id,
            'nonce': nonce,
            'to': '0x80C67432656d59144cEFf962E8fAF8926599bCF8',
            'value': intToDecimal(amount, 18),
            # 'gas': 80124,
            'gasPrice': web3.eth.gas_price,
        }

        if chain_id == 42170:
            gasLimit = web3.eth.estimate_gas({'to': Web3.toChecksumAddress(address_wallet), 'from': Web3.toChecksumAddress(address_wallet),'value': web3.toWei(0.0001, 'ether')}) + random.randint(50000, 100000)
        else:
            gasLimit = web3.eth.estimate_gas(contract_txn)

        contract_txn['gas'] = int(gasLimit + gasLimit * 0.2)

        cprint(amount, 'green')

        signed_txn = web3.eth.account.sign_transaction(
            contract_txn, private_key=privatekey)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        cprint(
            f'\n>>> bridge | {scan}/{web3.toHex(tx_hash)}', 'green')
    except Exception as error:
        cprint(f'\n>>> bridge | {error}', 'red')

def orbiter_bridge(privatekey, from_chain, to_chain, AMOUNT_TO_BRIDGE, MIN_BALANCE):

    cprint(f'\nstart : orbiter bridge {from_chain} => {to_chain}', 'yellow')

    amount_to_chain = ORBITER_AMOUNT[to_chain]
    str_amount_to_chain = ORBITER_AMOUNT_STR[to_chain]

    data = check_rpc(from_chain)
    rpc_chain = data['rpc']
    chain_id = data['chain_id']
    scan = data['scan']
    symbol_chain = data['token']

    if AMOUNT_TO_BRIDGE == 'all_balance':
        AMOUNT_TO_BRIDGE = float(check_balance(privatekey, rpc_chain, symbol_chain, MIN_BALANCE))

    if AMOUNT_TO_BRIDGE < 0.10101:
        decimal.getcontext().prec = 17
    else:
        decimal.getcontext().prec = 18

    if AMOUNT_TO_BRIDGE > 0.015:

        while True:

            try:
                amount = random.uniform(0.001, 0.0015)
                amount = round(AMOUNT_TO_BRIDGE - amount, 18)
                amount = round(amount, 14)
                amount = decimal.Decimal(amount) + decimal.Decimal(amount_to_chain)
                
                while True:
                    if str(amount)[-4:] == str_amount_to_chain:
                        break
                    amount = random.uniform(0.0010, 0.0015)
                    amount = round(AMOUNT_TO_BRIDGE - amount, 18)
                    amount = round(amount, 14)
                    amount = decimal.Decimal(amount) + decimal.Decimal(amount_to_chain)

                break

            except Exception as ex: 
                cprint(ex, 'red')
                time.sleep(10)

        bridge(privatekey, amount, rpc_chain, chain_id, scan)

    else:
        cprint('AMOUNT_TO_BRIDGE less 0.015', 'yellow')
