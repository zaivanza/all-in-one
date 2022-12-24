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


with open("erc20.json", "r") as file:
    ERC20_ABI = json.load(file)

with open("private_keys.txt", "r") as f:
    KEYS_LIST = [row.strip() for row in f]

with open("recepients.txt", "r") as f:
    RECEPIENTS = [row.strip() for row in f]

with open("proxies.txt", "r") as f:
    RPOXIES = [row.strip() for row in f]

BINANCE_API_KEY = 'YOUR_API_KEY'
BINANCE_API_SECRET = 'YOUR_API_SECRET'


RPCS = [
    {'chain': 'ETH', 'chain_id': 1, 'rpc': 'https://rpc.ankr.com/eth', 'scan': 'https://etherscan.io/tx', 'token': 'ETH'},

    {'chain': 'OPTIMISM', 'chain_id': 10, 'rpc': 'https://rpc.ankr.com/optimism', 'scan': 'https://optimistic.etherscan.io/tx', 'token': 'ETH'},

    {'chain': 'BNB', 'chain_id': 56, 'rpc': 'https://bsc-dataseed.binance.org', 'scan': 'https://bscscan.com/tx', 'token': 'BNB'},

    {'chain': 'MATIC', 'chain_id': 137, 'rpc': 'https://polygon-rpc.com', 'scan': 'https://polygonscan.com/tx', 'token': 'MATIC'},

    {'chain': 'ARBITRUM', 'chain_id': 42161, 'rpc': 'https://arb1.arbitrum.io/rpc', 'scan': 'https://arbiscan.io/tx', 'token': 'ETH'},

    {'chain': 'AVAXC', 'chain_id': 43114, 'rpc': 'https://api.avax.network/ext/bc/C/rpc', 'scan': 'https://snowtrace.io/tx', 'token': 'AVAX'},

    {'chain': 'NOVA', 'chain_id': 42170, 'rpc': 'https://nova.arbitrum.io/rpc', 'scan': 'https://nova.arbiscan.io/tx', 'token': 'ETH'},

    {'chain': 'FTM', 'chain_id': 250, 'rpc': 'https://rpc.ankr.com/fantom', 'scan': 'https://ftmscan.com/tx', 'token': 'FTM'},
]

text1 = '''
 /$$   /$$  /$$$$$$  /$$$$$$$  /$$       /$$      /$$  /$$$$$$  /$$$$$$$ 
| $$  | $$ /$$__  $$| $$__  $$| $$      | $$$    /$$$ /$$__  $$| $$__  $$
| $$  | $$| $$  \ $$| $$  \ $$| $$      | $$$$  /$$$$| $$  \ $$| $$  \ $$
| $$$$$$$$| $$  | $$| $$  | $$| $$      | $$ $$/$$ $$| $$  | $$| $$  | $$
| $$__  $$| $$  | $$| $$  | $$| $$      | $$  $$$| $$| $$  | $$| $$  | $$
| $$  | $$| $$  | $$| $$  | $$| $$      | $$\  $ | $$| $$  | $$| $$  | $$
| $$  | $$|  $$$$$$/| $$$$$$$/| $$$$$$$$| $$ \/  | $$|  $$$$$$/| $$$$$$$/
|__/  |__/ \______/ |_______/ |________/|__/     |__/ \______/ |_______/                                                                                                                                                                                                          
'''

text2 = '''
      ___          ___                                    ___          ___                  
     /\  \        /\  \        _____                     /\  \        /\  \        _____    
     \:\  \      /::\  \      /::\  \                   |::\  \      /::\  \      /::\  \   
      \:\  \    /:/\:\  \    /:/\:\  \                  |:|:\  \    /:/\:\  \    /:/\:\  \  
  ___ /::\  \  /:/  \:\  \  /:/  \:\__\  ___     ___  __|:|\:\  \  /:/  \:\  \  /:/  \:\__\ 
 /\  /:/\:\__\/:/__/ \:\__\/:/__/ \:|__|/\  \   /\__\/::::|_\:\__\/:/__/ \:\__\/:/__/ \:|__|
 \:\/:/  \/__/\:\  \ /:/  /\:\  \ /:/  /\:\  \ /:/  /\:\~~\  \/__/\:\  \ /:/  /\:\  \ /:/  /
  \::/__/      \:\  /:/  /  \:\  /:/  /  \:\  /:/  /  \:\  \       \:\  /:/  /  \:\  /:/  / 
   \:\  \       \:\/:/  /    \:\/:/  /    \:\/:/  /    \:\  \       \:\/:/  /    \:\/:/  /  
    \:\__\       \::/  /      \::/  /      \::/  /      \:\__\       \::/  /      \::/  /   
     \/__/        \/__/        \/__/        \/__/        \/__/        \/__/        \/__/    
'''

texts = [text1, text2]
colors = ['cyan', 'magenta', 'blue']

RUN_TEXT = random.choice(texts)
RUN_COLOR = random.choice(colors)

def intToDecimal(qty, decimal):
    return int(qty * int("".join(["1"] + ["0"]*decimal)))

def decimalToInt(qty, decimal):
    return qty/ int("".join((["1"]+ ["0"]*decimal)))

def prices():
    currency_price = []
    response = requests.get(url=f'https://api.gateio.ws/api/v4/spot/tickers')
    currency_price.append(response.json())
    return currency_price

def price_token(currency_price, symbol):

    try:

        for currency in currency_price[0]:
            if currency['currency_pair'] == f'{symbol}_USDT':
                price = currency['last']

        if symbol in ['USDC', 'USDT', 'DAI', 'BUSD']:
            price = 1

        return price

    except: 
        return 0

def check_balance(privatekey, rpc_chain, symbol_chain, min_balance):
    try:
            
        web3 = Web3(Web3.HTTPProvider(rpc_chain))
        account = web3.eth.account.privateKeyToAccount(privatekey)
        balance = web3.eth.get_balance(web3.toChecksumAddress(account.address))

        humanReadable = web3.from_wei(balance,'ether')

        try:
            # check price of token
            currency_price = prices()
            for currency in currency_price[0]:
                if currency['currency_pair'] == f'{symbol_chain}_USDT':
                    price_ = Decimal(currency['last'])
                    price = price_ + price_ * Decimal(0.2)
        except: price = 300

        gas = web3.eth.gas_price
        gasPrice = decimalToInt(gas, 18)

        return round(Decimal(humanReadable) - Decimal(Decimal(gasPrice)*Decimal(price)) - Decimal(min_balance), 7)


    except Exception as error:
        # cprint(f'error : {error}', 'yellow')
        None

def check_token_balance(privatekey, rpc_chain, address_contract, min_balance):
    try:

        web3 = Web3(Web3.HTTPProvider(rpc_chain))
        account = web3.eth.account.privateKeyToAccount(privatekey)
        wallet = account.address
        token_contract = web3.eth.contract(address=web3.toChecksumAddress(address_contract), abi=ERC20_ABI) 
        token_balance = token_contract.functions.balanceOf(web3.toChecksumAddress(wallet)).call()

        symbol = token_contract.functions.symbol().call()
        token_decimal = token_contract.functions.decimals().call()

        humanReadable = decimalToInt(token_balance, token_decimal) 

        # cprint(f'\nbalance : {round(humanReadable, 5)} {symbol}', 'white')

        return round(Decimal(humanReadable) - Decimal(min_balance), 7)

    except Exception as error:
        # cprint(f'error : {error}', 'yellow')
        None

def check_rpc(chain):
    for elem in RPCS:
        if elem['chain'] == chain:
            RPC = elem['rpc']
            chainId = elem['chain_id']
            scan = elem['scan']
            token = elem['token']

            return {
                'rpc': RPC, 'chain_id': chainId, 'scan': scan, 'token': token
            }

def value_with_slippage(value: int, percent: float):
    try:
        _percent = percent
        min_value = value - (value * (_percent / 100))
        max_value = value + (value * (_percent / 100))
        random_value = random.uniform(min_value, max_value)
        return random_value
    except Exception as e:
        cprint(e, 'red')

def sleeping(from_sleep, to_sleep):
    x = random.randint(from_sleep, to_sleep)
    for i in tqdm(range(x), desc='sleep ', bar_format='{desc}: {n_fmt}/{total_fmt}'):
        time.sleep(1)

ORBITER_AMOUNT = {
    'ETH': 0.000000000000009001,
    'OPTIMISM': 0.000000000000009007,
    'BNB': 0.000000000000009015,
    'ARBITRUM': 0.000000000000009002,
    'NOVA': 0.000000000000009016,
    'MATIC': 0.000000000000009006,
    'ZKSYNC': 0.000000000000009003,
    'STARKNET': 0.000000000000009004,
}

ORBITER_AMOUNT_STR = {
    'ETH': '9001',
    'OPTIMISM': '9007',
    'BNB': '9015',
    'ARBITRUM': '9002',
    'NOVA': '9016',
    'MATIC': '9006',
    'ZKSYNC': '9003',
    'STARKNET': '9004',
}

OPTIMISM_BRIDGE_ABI = '[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_l1Token","type":"address"},{"indexed":true,"internalType":"address","name":"_l2Token","type":"address"},{"indexed":true,"internalType":"address","name":"_from","type":"address"},{"indexed":false,"internalType":"address","name":"_to","type":"address"},{"indexed":false,"internalType":"uint256","name":"_amount","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"_data","type":"bytes"}],"name":"ERC20DepositInitiated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_l1Token","type":"address"},{"indexed":true,"internalType":"address","name":"_l2Token","type":"address"},{"indexed":true,"internalType":"address","name":"_from","type":"address"},{"indexed":false,"internalType":"address","name":"_to","type":"address"},{"indexed":false,"internalType":"uint256","name":"_amount","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"_data","type":"bytes"}],"name":"ERC20WithdrawalFinalized","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_from","type":"address"},{"indexed":true,"internalType":"address","name":"_to","type":"address"},{"indexed":false,"internalType":"uint256","name":"_amount","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"_data","type":"bytes"}],"name":"ETHDepositInitiated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"_from","type":"address"},{"indexed":true,"internalType":"address","name":"_to","type":"address"},{"indexed":false,"internalType":"uint256","name":"_amount","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"_data","type":"bytes"}],"name":"ETHWithdrawalFinalized","type":"event"},{"inputs":[{"internalType":"address","name":"_l1Token","type":"address"},{"internalType":"address","name":"_l2Token","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"uint32","name":"_l2Gas","type":"uint32"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"depositERC20","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_l1Token","type":"address"},{"internalType":"address","name":"_l2Token","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"uint32","name":"_l2Gas","type":"uint32"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"depositERC20To","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint32","name":"_l2Gas","type":"uint32"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"depositETH","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint32","name":"_l2Gas","type":"uint32"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"depositETHTo","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"deposits","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"donateETH","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_l1Token","type":"address"},{"internalType":"address","name":"_l2Token","type":"address"},{"internalType":"address","name":"_from","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"finalizeERC20Withdrawal","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_from","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"finalizeETHWithdrawal","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_l1messenger","type":"address"},{"internalType":"address","name":"_l2TokenBridge","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"l2TokenBridge","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"messenger","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"stateMutability":"payable","type":"receive"}]'

ARBITRUM_BRIDGE_ABI = '[{"inputs":[{"internalType":"uint256","name":"dataLength","type":"uint256"},{"internalType":"uint256","name":"maxDataLength","type":"uint256"}],"name":"DataTooLarge","type":"error"},{"inputs":[{"internalType":"uint256","name":"expected","type":"uint256"},{"internalType":"uint256","name":"actual","type":"uint256"}],"name":"InsufficientSubmissionCost","type":"error"},{"inputs":[{"internalType":"uint256","name":"expected","type":"uint256"},{"internalType":"uint256","name":"actual","type":"uint256"}],"name":"InsufficientValue","type":"error"},{"inputs":[],"name":"L1Forked","type":"error"},{"inputs":[{"internalType":"address","name":"origin","type":"address"}],"name":"NotAllowedOrigin","type":"error"},{"inputs":[],"name":"NotForked","type":"error"},{"inputs":[],"name":"NotOrigin","type":"error"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"owner","type":"address"}],"name":"NotOwner","type":"error"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"rollup","type":"address"},{"internalType":"address","name":"owner","type":"address"}],"name":"NotRollupOrOwner","type":"error"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"l2CallValue","type":"uint256"},{"internalType":"uint256","name":"deposit","type":"uint256"},{"internalType":"uint256","name":"maxSubmissionCost","type":"uint256"},{"internalType":"address","name":"excessFeeRefundAddress","type":"address"},{"internalType":"address","name":"callValueRefundAddress","type":"address"},{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"RetryableData","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"user","type":"address"},{"indexed":false,"internalType":"bool","name":"val","type":"bool"}],"name":"AllowListAddressSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"isEnabled","type":"bool"}],"name":"AllowListEnabledUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"messageNum","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"data","type":"bytes"}],"name":"InboxMessageDelivered","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"messageNum","type":"uint256"}],"name":"InboxMessageDeliveredFromOrigin","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[],"name":"allowListEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"bridge","outputs":[{"internalType":"contract IBridge","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"dataLength","type":"uint256"},{"internalType":"uint256","name":"baseFee","type":"uint256"}],"name":"calculateRetryableSubmissionFee","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"l2CallValue","type":"uint256"},{"internalType":"uint256","name":"maxSubmissionCost","type":"uint256"},{"internalType":"address","name":"excessFeeRefundAddress","type":"address"},{"internalType":"address","name":"callValueRefundAddress","type":"address"},{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"createRetryableTicket","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"l2CallValue","type":"uint256"},{"internalType":"uint256","name":"maxSubmissionCost","type":"uint256"},{"internalType":"address","name":"excessFeeRefundAddress","type":"address"},{"internalType":"address","name":"callValueRefundAddress","type":"address"},{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"createRetryableTicketNoRefundAliasRewrite","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"depositEth","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"depositEth","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"contract IBridge","name":"_bridge","type":"address"},{"internalType":"contract ISequencerInbox","name":"_sequencerInbox","type":"address"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"isAllowed","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"contract IBridge","name":"","type":"address"}],"name":"postUpgradeInit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"sendContractTransaction","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"sendL1FundedContractTransaction","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"sendL1FundedUnsignedTransaction","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"sendL1FundedUnsignedTransactionToFork","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes","name":"messageData","type":"bytes"}],"name":"sendL2Message","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"messageData","type":"bytes"}],"name":"sendL2MessageFromOrigin","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"sendUnsignedTransaction","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"sendUnsignedTransactionToFork","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"address","name":"withdrawTo","type":"address"}],"name":"sendWithdrawEthToFork","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"sequencerInbox","outputs":[{"internalType":"contract ISequencerInbox","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address[]","name":"user","type":"address[]"},{"internalType":"bool[]","name":"val","type":"bool[]"}],"name":"setAllowList","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_allowListEnabled","type":"bool"}],"name":"setAllowListEnabled","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"l2CallValue","type":"uint256"},{"internalType":"uint256","name":"maxSubmissionCost","type":"uint256"},{"internalType":"address","name":"excessFeeRefundAddress","type":"address"},{"internalType":"address","name":"callValueRefundAddress","type":"address"},{"internalType":"uint256","name":"gasLimit","type":"uint256"},{"internalType":"uint256","name":"maxFeePerGas","type":"uint256"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"unsafeCreateRetryableTicket","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"payable","type":"function"}]'

ABI_ARBI_TO_ETH = '[{"type":"event","name":"L2ToL1Transaction","inputs":[{"type":"address","name":"caller","internalType":"address","indexed":false},{"type":"address","name":"destination","internalType":"address","indexed":true},{"type":"uint256","name":"uniqueId","internalType":"uint256","indexed":true},{"type":"uint256","name":"batchNumber","internalType":"uint256","indexed":true},{"type":"uint256","name":"indexInBatch","internalType":"uint256","indexed":false},{"type":"uint256","name":"arbBlockNum","internalType":"uint256","indexed":false},{"type":"uint256","name":"ethBlockNum","internalType":"uint256","indexed":false},{"type":"uint256","name":"timestamp","internalType":"uint256","indexed":false},{"type":"uint256","name":"callvalue","internalType":"uint256","indexed":false},{"type":"bytes","name":"data","internalType":"bytes","indexed":false}],"anonymous":false},{"type":"event","name":"L2ToL1Tx","inputs":[{"type":"address","name":"caller","internalType":"address","indexed":false},{"type":"address","name":"destination","internalType":"address","indexed":true},{"type":"uint256","name":"hash","internalType":"uint256","indexed":true},{"type":"uint256","name":"position","internalType":"uint256","indexed":true},{"type":"uint256","name":"arbBlockNum","internalType":"uint256","indexed":false},{"type":"uint256","name":"ethBlockNum","internalType":"uint256","indexed":false},{"type":"uint256","name":"timestamp","internalType":"uint256","indexed":false},{"type":"uint256","name":"callvalue","internalType":"uint256","indexed":false},{"type":"bytes","name":"data","internalType":"bytes","indexed":false}],"anonymous":false},{"type":"event","name":"SendMerkleUpdate","inputs":[{"type":"uint256","name":"reserved","internalType":"uint256","indexed":true},{"type":"bytes32","name":"hash","internalType":"bytes32","indexed":true},{"type":"uint256","name":"position","internalType":"uint256","indexed":true}],"anonymous":false},{"type":"function","stateMutability":"view","outputs":[{"type":"bytes32","name":"","internalType":"bytes32"}],"name":"arbBlockHash","inputs":[{"type":"uint256","name":"arbBlockNum","internalType":"uint256"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"arbBlockNumber","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"arbChainID","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"arbOSVersion","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"getStorageGasAvailable","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"isTopLevelCall","inputs":[]},{"type":"function","stateMutability":"pure","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"mapL1SenderContractAddressToL2Alias","inputs":[{"type":"address","name":"sender","internalType":"address"},{"type":"address","name":"unused","internalType":"address"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"myCallersAddressWithoutAliasing","inputs":[]},{"type":"function","stateMutability":"view","outputs":[{"type":"uint256","name":"size","internalType":"uint256"},{"type":"bytes32","name":"root","internalType":"bytes32"},{"type":"bytes32[]","name":"partials","internalType":"bytes32[]"}],"name":"sendMerkleTreeState","inputs":[]},{"type":"function","stateMutability":"payable","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"sendTxToL1","inputs":[{"type":"address","name":"destination","internalType":"address"},{"type":"bytes","name":"data","internalType":"bytes"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"bool","name":"","internalType":"bool"}],"name":"wasMyCallersAddressAliased","inputs":[]},{"type":"function","stateMutability":"payable","outputs":[{"type":"uint256","name":"","internalType":"uint256"}],"name":"withdrawEth","inputs":[{"type":"address","name":"destination","internalType":"address"}]}]'

SUSHISWAP_ABI = '[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"amountADesired","type":"uint256"},{"internalType":"uint256","name":"amountBDesired","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountTokenDesired","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"addLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"},{"internalType":"uint256","name":"liquidity","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountIn","outputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"reserveIn","type":"uint256"},{"internalType":"uint256","name":"reserveOut","type":"uint256"}],"name":"getAmountOut","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsIn","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"reserveA","type":"uint256"},{"internalType":"uint256","name":"reserveB","type":"uint256"}],"name":"quote","outputs":[{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidity","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETH","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"removeLiquidityETHSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermit","outputs":[{"internalType":"uint256","name":"amountToken","type":"uint256"},{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountTokenMin","type":"uint256"},{"internalType":"uint256","name":"amountETHMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityETHWithPermitSupportingFeeOnTransferTokens","outputs":[{"internalType":"uint256","name":"amountETH","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint256","name":"liquidity","type":"uint256"},{"internalType":"uint256","name":"amountAMin","type":"uint256"},{"internalType":"uint256","name":"amountBMin","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"bool","name":"approveMax","type":"bool"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"removeLiquidityWithPermit","outputs":[{"internalType":"uint256","name":"amountA","type":"uint256"},{"internalType":"uint256","name":"amountB","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapETHForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForETHSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMin","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapExactTokensForTokensSupportingFeeOnTransferTokens","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactETH","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"},{"internalType":"uint256","name":"amountInMax","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"name":"swapTokensForExactTokens","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'



