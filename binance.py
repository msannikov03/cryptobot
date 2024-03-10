import urllib.parse
import hashlib
import hmac
import requests
import time
import json

with open('config.json') as config_file:
    config = json.load(config_file)
    
API_URL = "https://api.binance.us"
API_KEY = config["binance_api_key"]
SECRET_KEY = config["binance_api_secret"]

def generate_signature(data, secret):
    query_string = urllib.parse.urlencode(data)
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def send_request(method, endpoint, data):
    headers = {
        'X-MBX-APIKEY': API_KEY
    }
    data['timestamp'] = int(time.time() * 1000)
    data['signature'] = generate_signature(data, SECRET_KEY)
    if method == 'GET':
        response = requests.get(f"{API_URL}{endpoint}", headers=headers, params=data)
    elif method == 'POST':
        response = requests.post(f"{API_URL}{endpoint}", headers=headers, params=data)
    else:
        raise ValueError("Method must be 'GET' or 'POST'")
    return response.json()

def send_public_request(endpoint):
    headers = {
        'X-MBX-APIKEY': API_KEY
    }
    response = requests.get(f"{API_URL}{endpoint}", headers=headers)
    return response.json()

def place_market_buy_order(symbol, quantity):
    data = {
        'symbol': symbol,
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': quantity
    }
    return send_request('POST', '/api/v3/order', data)

def place_market_sell_order(symbol, quantity):
    data = {
        'symbol': symbol,
        'side': 'SELL',
        'type': 'MARKET',
        'quantity': quantity
    }
    return send_request('POST', '/api/v3/order', data)

def place_limit_buy_order(symbol, quantity, price):
    data = {
        'symbol': symbol,
        'side': 'BUY',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': quantity,
        'price': price
    }
    return send_request('POST', '/api/v3/order', data)

def place_limit_sell_order(symbol, quantity, price):
    data = {
        'symbol': symbol,
        'side': 'SELL',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': quantity,
        'price': price
    }
    return send_request('POST', '/api/v3/order', data)

def fetch_open_orders(symbol):
    data = {
        'symbol': symbol
    }
    return send_request('GET', '/api/v3/openOrders', data)

def fetch_active_balances_and_prices():
    account_info = send_request('GET', '/api/v3/account', {})
    active_balances = [balance for balance in account_info['balances'] if float(balance['free']) > 0]

    all_prices = send_public_request('/api/v3/ticker/price')
    prices_dict = {item['symbol']: item['price'] for item in all_prices}

    exchange_info = send_public_request('/api/v3/exchangeInfo')
    min_qty_dict = {}
    for symbol_info in exchange_info['symbols']:
        for filter in symbol_info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                min_qty_dict[symbol_info['symbol']] = filter['minQty']

    active_balances_with_prices = []
    for balance in active_balances:
        asset = balance['asset']
        free_balance = balance['free']

        matching_symbols = [f"{asset}USDT", f"{asset}USD", f"{asset}USD4"]
        current_price = None
        min_qty = None
        for symbol in matching_symbols:
            if symbol in prices_dict:
                current_price = prices_dict[symbol]
                min_qty = min_qty_dict.get(symbol, 'No min qty found')
                break

        if current_price is None:
            current_price = 'No price found'
        
        active_balances_with_prices.append({
            'asset': asset,
            'free_balance': free_balance,
            'current_price': current_price,
            'min_qty': min_qty
        })

    return active_balances_with_prices

active_balances_with_prices = fetch_active_balances_and_prices()
print(json.dumps(active_balances_with_prices, indent=4))


# print(place_market_buy_order('BTCUSDT', 0.0001))
# print(place_market_sell_order('BTCUSDT', 0.0001))
# print(place_limit_buy_order('BTCUSDT', 0.001, '30000'))
# print(place_limit_sell_order('BTCUSDT', 0.001, '70000'))
# print(fetch_open_orders('BTCUSDT'))