import requests, json, time, random
from pyuseragents import random as random_useragent
from termcolor import cprint
from tabulate import tabulate
from config import *


def debank_tokens(address, headers):

    try:

        url = f'https://api.debank.com/token/cache_balance_list?user_addr={address}'

        result = []

        while True:
            try:
                proxy = RPOXIES[random.randint(0,len(RPOXIES)-1)]
                proxies = {
                'http': proxy,
                'https': proxy,
                }
                headers['user-agent'] = random_useragent()
                response = requests.get(url=url, headers=headers, proxies=proxies)

                if response.status_code == 200:
                    result.append(response.json())
                    break


            except Exception as error: 
                cprint(f'довыебывался : {error}', 'red')
                sleeping(60, 60)

        return result

    except Exception as error:
        cprint(error, 'red')

def debank_nft(address, headers, chain):

    try:

        result = []
        url = f'https://api.debank.com/nft/collection_list?user_addr={address}&chain={chain}'

        while True:

            proxy = RPOXIES[random.randint(0,len(RPOXIES)-1)]
            proxies = {
                'http': proxy,
                'https': proxy,
            }
            headers['user-agent'] = random_useragent()
            response = requests.get(url=url, headers=headers, proxies=proxies)

            if response.status_code == 200:
                response = response.json()
                if response['data']['job']: 
                    time.sleep(3)
                else:
                    result.append(response)
                    break

        return result

    except Exception as error:
        cprint(error, 'red')

def debank_protocols(address, headers):

    try:

        url = f'https://api.debank.com/portfolio/project_list?user_addr={address}'
        
        result = []

        while True:
            proxy = RPOXIES[random.randint(0,len(RPOXIES)-1)]
            proxies = {
            'http': proxy,
            'https': proxy,
            }
            headers['user-agent'] = random_useragent()
            response = requests.get(url=url, headers=headers, proxies=proxies)

            if response.status_code == 200:
                result.append(response.json())
                break

        return result

    except Exception as error:
        cprint(error, 'red')


table_tokens = {
    'table': [],
    'total_value': []
}
def done_tokens(result, MIN_TABLE_AMOUNT):

    try:

        for x in result[0]['data']:

            chain  = x['chain'].upper()
            price = x['price']
            amount = x['amount']
            symbol = x['optimized_symbol']

            value = amount * price

            if value > MIN_TABLE_AMOUNT:
                table_tokens['table'].append([chain, round(amount, 4), symbol, f'{int(value)} $'])
            table_tokens['total_value'].append(value)

    except Exception as error:
        cprint(error, 'red')

table_nfts = []
def done_nft(result):

    try:

        for x in result[0]['data']['result']['data']:

            amount = x['amount']
            name = x['name']

            table_nfts.append([name, amount])

    except Exception as error:
        cprint(error, 'red')

table_protocols = {
    'table': [],
    'total_value': [],
    'table_txt': [],
}
def done_protocols(result, MIN_TABLE_AMOUNT):

    try:
        for portfolio_list in result[0]['data']:

            project = portfolio_list['name']

            for x in portfolio_list['portfolio_item_list']:
                value = int(x['stats']['asset_usd_value'])

            if value > MIN_TABLE_AMOUNT:

                table_protocols['table'].append([project, f'{value} $'])
                table_protocols['table_txt'].append([project, value])
                table_protocols['total_value'].append(value)

            else:
                table_protocols['total_value'].append(value)

    except Exception as error:
        None


def checker_main(func, MIN_TABLE_AMOUNT):

    total_balance = []

    file = open('debank.txt', 'w')

    for key in KEYS_LIST:

        try:
            web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
            address = web3.eth.account.privateKeyToAccount(key).address
        except: 
            address = key

        headers = {
            'accept': '*/*',
            'accept-language': 'ru,en;q=0.9',
            'origin': 'https://debank.com',
            'referer': 'https://debank.com/',
            'source': 'web',
            # 'user-agent': random_useragent()
        }

        cprint(f'\n>>> {address}\n', 'yellow')
        file.write(f'\n>>> {address}\n')

        if 'tokens' in func:

            table_tokens['table'].clear()
            table_tokens['total_value'].clear()

            result = debank_tokens(address, headers)
            done_tokens(result, MIN_TABLE_AMOUNT)

            table = table_tokens['table']

            if len(table) > 0:

                head_table = ['chain', 'amount', 'symbol', 'result']
                done = tabulate(table, head_table, tablefmt='double_outline')
                cprint(done, 'white')
                file.write(f'\n{done}\n')

        if 'protocols' in func:

            table_protocols['table'].clear()
            table_protocols['total_value'].clear()
            table_protocols['table_txt'].clear()

            result = debank_protocols(address, headers)
            done_protocols(result, MIN_TABLE_AMOUNT)
            
            if len(table_protocols['table']) > 0:

                table =  table_protocols['table']
                head_table = ['project', 'result']
                done = tabulate(table, head_table, tablefmt='double_outline')
                cprint(done, 'white')

                table_txt =  table_protocols['table_txt']
                done_txt = tabulate(table_txt, head_table, tablefmt='double_outline')
                file.write(f'\n{done_txt}\n')

        if 'nfts' in func:

            table_nfts.clear()

            chains = ['op', 'eth', 'arb', 'matic', 'bsc']

            for chain in chains:

                result = debank_nft(address, headers, chain)
                done_nft(result)

            if len(table_nfts) > 0:
                head_table = ['name', 'amount']
                done = tabulate(table_nfts, head_table, tablefmt='double_outline')
                cprint(done, 'white')
                file.write(f'\n{done}\n')

        total_value = table_tokens['total_value'] + table_protocols['total_value']
        done = f'total value : {int(sum(total_value))} $'
        cprint(done, 'cyan')
        file.write(f'\n{done}\n')

        total_balance.append(int(sum(total_value)))

    done = f'\nTOTAL BALANCE : {sum(total_balance)} $'
    cprint(done, 'yellow')
    file.write(f'\n{done}\n')
    file.close()


