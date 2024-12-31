import numpy as np
import pandas as pd
from scipy.stats import norm
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

timezone_et = ZoneInfo('America/New_York')

def get_btc_price():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        price = data['bitcoin']['usd']
        return price
    else:
        raise Exception(f"Error fetching BTC price. Status code: {response.status_code}")

def get_eth_price():
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': 'ethereum',
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        price = data['ethereum']['usd']
        return price
    else:
        raise Exception(f"Error fetching ETH price. Status code: {response.status_code}")

def get_historical_btc_prices():
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': '365',
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        prices = data['prices']
        return prices
    else:
        raise Exception(f"Error fetching BTC prices. Status code: {response.status_code}")

def get_historical_eth_prices():
    url = 'https://api.coingecko.com/api/v3/coins/ethereum/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': '365',
        'interval': 'daily'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        prices = data['prices']
        return prices
    else:
        raise Exception(f"Error fetching BTC prices. Status code: {response.status_code}")

def calculate_annualized_volatility(prices):
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.sort_values('date')
    df['return'] = df['price'].pct_change()
    daily_volatility = df['return'].std()
    annualized_volatility = daily_volatility * np.sqrt(365)
    return annualized_volatility

def get_T(year, month, day, hour):
    return datetime(year, month, day, hour, tzinfo=timezone_et)

def get_ttt(future_time: datetime) -> float:
    current_time = datetime.now(tz=timezone_et)
    elapsed_time = future_time - current_time
    days_in_year = 365.25
    years_elapsed = elapsed_time.total_seconds() / (days_in_year * 24 * 60 * 60)
    return years_elapsed

def get_apy(ttt, at_risk=None, to_win=100.0) -> float:
    """
    When to_win=100.0, at_risk can be interpreted as price in cents per share.
    """
    profit = to_win / at_risk
    rate = np.log(profit) / ttt
    return rate*100

def calculate_P_above(S0, K, sigma, r, T):
    ttt = get_ttt(T)
    d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * ttt) / (sigma * np.sqrt(ttt))
    d2 = d1 - sigma * np.sqrt(ttt)
    return norm.cdf(d2)

def print_P_above(P_above, S0, K, sigma, T, ETH=False):
    hours_remaining = format(24 * 365 * get_ttt(T), '.3f')
    print("Date - time:\t", datetime.now(tz=timezone_et))
    print("Hours to T:\t", hours_remaining)
    print()
    if ETH:
        print("ETH price:\t", format(S0, ','))
    else:
        print("BTC price:\t", format(S0, ','))
    print("Strike price:\t", format(K, ','))
    print("Volatility:\t", round(sigma, 4))
    print("P(above):\t", round(P_above, 4))
    
def get_str_P_above(P_above, S0, K, sigma, T, ETH=False):
    hours_remaining = str(format(24 * 365 * get_ttt(T), '.3f'))
    minutes_remaining = 60 * float(hours_remaining[-4:])
    hours_remaining = int(float(hours_remaining))
    s = "Date - time:\t" + str(datetime.now(tz=timezone_et))
    s += f"\nHours to T:\t\t{hours_remaining}:{round(minutes_remaining, 2)}\n"
    if ETH:
        s += "ETH price:\t\t" + str(format(S0, ','))
    else:
        s += "BTC price:\t\t" + str(format(S0, ','))
    s += "\nStrike price:\t" + str(format(K, ','))
    s += "\nVolatility:\t\t" + str(round(sigma, 4))
    s += "\nP(above):\t\t" + str(round(P_above, 4))
    s += "\n"
    return s