""" Collection of functions to retrieve balance information from various exchanges"""

import pandas as pd
import ccxt as cx
import json
from requests import post
import time
import urllib.parse
import hashlib
import hmac
import base64
import requests
from pycoingecko import CoinGeckoAPI

cg=CoinGeckoAPI()

green_list = ["USD.M", "ZUSD", "USD", "DYDX", "USD Funding"]
blue_list = ["EUR.M", "ZEUR", "EUR"]


# Help for deploying web app: https://devcenter.heroku.com/articles/procfile

# Retrieve the json object from the API
def get_ticker(url):
    url_req = requests.get(url)

    # Covert to a json object
    url_json = json.loads(url_req.text)
    return url_json


#Gets the euro price
def get_euro_price():
    alpha_rates_usd_url = 'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=EUR&to_currency=USD&apikey=<API KEY>'

    ticker=get_ticker(alpha_rates_usd_url)

    price=ticker["Realtime Currency Exchange Rate"]["5. Exchange Rate"]

    return float(price)


#Retrieves the price of a given token from the coingecko API
def get_price( token):



    coins_list = cg.get_coins_list()
    token_price=0
    edited_token=""


    #slpit the token
    if "." in token and token not in green_list and token not in blue_list:
        edited_token=token.split(".")[0].lower()
    elif " " in token and token not in green_list and token not in blue_list:
        edited_token=token.split(" ")[0].lower()
    elif token in green_list:
        return 1
    elif token in blue_list:
        token_price=get_euro_price()
        return token_price
    else:
        edited_token=token.lower()


    for coin in coins_list:
        if coin["symbol"]==edited_token  and "wormhole" not in coin["id"] :
            token_id=coin["id"]
            price=cg.get_price(ids=token_id, vs_currencies="usd")[token_id]["usd"]
            token_price=price


    return token_price





#Adds up the total amount for each coin
def counter(account_book,totals_book):

    for pair in account_book:

        if pair not in totals_book:
            totals_book.update({pair: account_book[pair]})
        else:
            totals_book[pair] += float(account_book[pair])

    return totals_book




def get_kraken_signature(urlpath, data, secret):

    postdata = urllib.parse.urlencode(data)
    encoded = (str(data['nonce']) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


def kraken_request(uri_path, data, api_key, api_sec):
    api_url = "https://api.kraken.com"
    headers = {}
    headers['API-Key'] = api_key
    # get_kraken_signature() as defined in the 'Authentication' section
    headers['API-Sign'] = get_kraken_signature(uri_path, data, api_sec)
    req = post((api_url + uri_path), headers=headers, data=data)
    return req



# get balances for Kraken
def get_kraken():

    kraken_book={}
    df_ready_book={}


    api_key = '<KEY>'
    api_sec = 'SECRET'
    resp = kraken_request('/0/private/Balance', {"nonce": str(int(1000 * time.time()))}, api_key, api_sec)
    balances = json.loads(resp.content)


    wallets = balances['result']

    for pair in wallets:
        if float(wallets[pair]) >0:
            #Add Exceptions for XRP and XLM
            if 'XXRP'==pair or 'XXLM'==pair:
                mock_pair = pair.replace('X', '')
                mock_pair.strip()
                new_pair=f'X{mock_pair}'
                kraken_book.update({new_pair: float(wallets[pair])})
            elif pair=='XLTC':
                kraken_book.update({'LTC': float(wallets[pair])})
            elif pair=='XETH':
                kraken_book.update({'ETH': float(wallets[pair])})
            elif pair=='XXBT':
                kraken_book.update({'BTC': float(wallets[pair])})
            elif pair=='XXDG':
                kraken_book.update({'XDG': float(wallets[pair])})
            else:
                kraken_book.update({pair:float(wallets[pair])})

    # Make dict dataframe ready
    for coin in kraken_book:
        df_ready_book.update({coin: [kraken_book[coin]]})



    kraken_df=pd.DataFrame(df_ready_book)

    return {'df':kraken_df, 'book':kraken_book}




# get balances for bitfinex
def get_bitfinex():

    api_key='<KEY>'
    api_sec='<SECRET>'
    bitfinex_book = {}
    df_ready_book={}

    bitfinex = cx.bitfinex({
        'apiKey': api_key,
        'secret': api_sec,
    })

    wallets = bitfinex.fetch_balance()['info']



    for wallet in wallets:
        if float(wallet['amount']) >0:
            if wallet['currency']=='ust':
                bitfinex_book.update({wallet['currency'].upper().replace('T','DT'): float(wallet['amount'])})
            elif wallet['type']=='deposit':
                bitfinex_book.update({f"{wallet['currency'].upper()} Funding": float(wallet['amount'])})
            else:
                bitfinex_book.update({wallet['currency'].upper(): float(wallet['amount'])})


    #price_dict=get_bitfinex_prices()


    # Make dict dataframe ready
    for coin in bitfinex_book:
        df_ready_book.update({coin: [bitfinex_book[coin]]})

    """
    #Copy the dict
    copy_df=df_ready_book

    #Calculate the dollar value and append to the copy for each
    for entry in df_ready_book:
        for coin in price_dict:


            if " " in entry and coin in entry:

                #amount= df_ready_book[entry][0]
                price=price_dict[coin]
                #dollar_value= amount*price
                copy_df[entry].append(price)

            elif coin==entry:
                #amount = df_ready_book[entry][0]
                price = price_dict[coin]
                #dollar_value = amount * price
                copy_df[entry].append(price)


    #Make all entries the same length
    for entry in copy_df:

        entry_list= copy_df[entry]

        if len(entry_list)!=2:
            entry_list.append(1.00000)
    """


    bitfinex_df= pd.DataFrame(df_ready_book)
    return {'df':bitfinex_df, 'book':bitfinex_book}




# get balances of Coinbase wallets
def get_coinbase():

    coinbase_book={}
    df_ready_book={}


    key = '<KEY>'
    secret = '<SECRET>'
    passphrase = '<PHRASE>'

    coinbase = cx.coinbasepro({
        "apiKey": key,
        "secret": secret,
        "password": passphrase,
        "enableRateLimit": True
    })





    wallets=coinbase.fetch_balance()['info']

    for wallet in wallets:
        #print(wallet['currency'],':',float(wallet['balance']))
        if float(wallet['balance']) > 0:
            coinbase_book.update({wallet['currency']:float(wallet['balance'])})

    #Make dict dataframe ready
    for coin in coinbase_book:
        df_ready_book.update({coin:[coinbase_book[coin]]})




    coinbase_df= pd.DataFrame(df_ready_book)




    return {'df':coinbase_df, 'book':coinbase_book}




#Calculates the total balance of each coin from all accounts
def get_total():


    kraken_book = get_kraken()
    coinbase_book = get_coinbase()
    bitfinex_book = get_bitfinex()
    totals_book={}
    df_ready_book={}

    #Get the totals of all accounts
    totals_book= counter(account_book=kraken_book["book"],totals_book=totals_book)
    totals_book=counter(account_book=coinbase_book["book"],totals_book=totals_book)
    totals_book=counter(account_book=bitfinex_book["book"],totals_book=totals_book)

    #Create a dataframe ready dict
    for coin in totals_book:
        df_ready_book.update({coin: [totals_book[coin]]})

    totals_df=pd.DataFrame(df_ready_book)

    return {'totals_df':totals_df,"totals_dict":df_ready_book, "kraken_df":kraken_book["df"],"coinbase_df":coinbase_book["df"],"bitfinex_df":bitfinex_book["df"]}







