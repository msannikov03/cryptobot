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

# print(place_market_buy_order('BTCUSDT', 0.0001))
# print(place_market_sell_order('BTCUSDT', 0.001))
# print(place_limit_buy_order('BTCUSDT', 0.001, '30000'))
# print(place_limit_sell_order('BTCUSDT', 0.001, '70000'))
# print(fetch_open_orders('BTCUSDT'))