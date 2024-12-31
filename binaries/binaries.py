import numpy as np
import pandas_datareader.data as web
from scipy.stats import norm
from zoneinfo import ZoneInfo
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import requests

timezone_et = ZoneInfo('America/New_York')

def get_r(index: int = 2) -> float:
    """
    index = 0: 3 month treasuries,
    index = 1: 6 month treasuries,
    index = 2: 12 month treasuries
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    series = ['TB3MS', 'TB6MS', 'TB1YR']
    r: float = 0.0
    try:
        df = web.DataReader(series, 'fred', start_date, end_date)
        r = df[series[index]].iloc[-1] / 100
        return r
    except:
        if not r:
            print("Unable to download risk-free rate.")
        return r if r else 0.04
    
risk_free_rate = get_r()

def get_T(year, month, day, hour) -> datetime:
    return datetime(year, month, day, hour, tzinfo=timezone_et)

def get_market_close() -> datetime:
    T = datetime.now(tz=timezone_et)
    if T.hour >= 16:
        T = T.replace(day=T.day+1)
    T = T.replace(hour=16, minute=0, second=0, microsecond=0)
    return T

def get_ttt(T: datetime = get_market_close()) -> float:
    """
    Calculate the time in years until time T.
    """
    t = datetime.now(tz=timezone_et)
    time_delta = T - t
    years = time_delta.total_seconds() / (365 * 24 * 60 * 60)
    assert years > 0.0, "Time T has passed."
    return years

def calculate_apy(ttt, at_risk=None, to_win=100.0) -> float:
    """
    When to_win=100.0, at_risk can be interpreted as price in cents per share.
    """
    profit = to_win / at_risk
    rate = np.log(profit) / ttt
    return rate * 100

def get_1y_prices(ticker: str) -> pd.DataFrame:
    data = yf.download(ticker, period='1y', interval='1d', progress=False)
    adj_close_prices = data[('Adj Close', ticker)]
    adj_close_prices.dropna(inplace=True)
    daily_returns = adj_close_prices.pct_change().dropna()
    return daily_returns

def price(ticker: str) -> float:
    data = yf.download(ticker, period='1d', interval='1m', progress=False)
    S0 = data[('Adj Close', ticker)].iloc[-1]
    return S0

def calculate_historical_volatility(returns: pd.DataFrame) -> float:
    """
    Calculate historical volatility over the timeframe of a set of returns.
    """
    sigma = returns.std()
    volatility = sigma * len(returns)**0.5
    return volatility  

def blackscholes_P_above(
    S0: float, 
    K: float, 
    sigma: float, 
    T: datetime = None, 
    ttt: float = None, 
    r: float = risk_free_rate
) -> float:
    """
    Calculate the probability that the price of a security will be above K
    at time T using the Black-Scholes model.

    Parameters:
        S0 (float): Initial price of the security.
        K (float): Strike price.
        sigma (float): Volatility.
        T (datetime, optional): Time of maturity.
        ttt (float, optional): Time to maturity in years.
        r (float): Risk-free rate.

    Returns:
        float: Probability that the price will exceed K at time T.
    """
    # sigma *= (24/6.5)**0.5
    if T:
        ttt = get_ttt(T)
    assert ttt > 0.0, "Time T has passed."
    d1 = (np.log(S0 / K) + (0.5 * sigma**2 + r) * ttt) / (sigma * ttt**0.5)
    d2 = d1 - sigma * ttt**0.5
    return norm.cdf(d2)

def bachelier_P_above(
    S0: float, 
    K: float, 
    sigma: float, 
    T: datetime = None, 
    ttt: float = None, 
    r: float = risk_free_rate
) -> float:
    """
    Calculate the probability that the price of a security will be above K
    at time T using the Bachelier model.

    Parameters:
        S0 (float): Initial price of the security.
        K (float): Strike price.
        sigma (float): Absolute volatility (Bachelier).
        T (datetime, optional): Time of maturity.
        ttt (float, optional): Time to maturity in years.
        r (float): Risk-free rate.

    Returns:
        float: Probability that the price will exceed K at time T.
    """
    sigma *= S0 # converts volatility to absolute volatility
    # sigma *= (24/6.5)**0.5
    if T:
        ttt = get_ttt(T)
    assert ttt > 0.0, "Time T has passed."
    mu = S0 + (r * S0) * ttt
    z = (mu - K) / (sigma * ttt**0.5)
    return norm.cdf(z)

def P(K, ticker='^GSPC', sigma=price('^VIX') / 100):
    return bachelier_P_above(S0=price(ticker), K=K, sigma=sigma, T=get_market_close())

def print_P_above(S0, K, sigma, T=None, ttt=None, P_above=None) -> None:
    if not P_above:
        P_above = blackscholes_P_above(S0, K, sigma, T)
    if ttt is None:
        assert T, "Input a time T or a time-to-target ttt."
        ttt = get_ttt(T)
    assert ttt > 0.0, "Time T has passed."
    hours_remaining = 24 * 365 * ttt
    print(f"Datetime:\t {datetime.now(tz=timezone_et):%D %T} ET")
    print(f"Hours to T:\t {hours_remaining:.3f}")
    print()
    print(f"Price:\t\t {S0:,.2f}")
    print(f"Strike price:\t {K:,}")
    print()
    print(f"Volatility:\t {sigma:.4f}")
    print(f"Risk-free rate:\t {risk_free_rate:.4f}")
    print()
    print(f"P(above)%:\t {P_above:.4%}")
    print(f"P(below)%:\t {1 - P_above:.4%}")

def get_value(P_above: float, call_price: float) -> float:
    if P_above > call_price:
        print("Buy yes.")
    else:
        print("Buy no.")
    value = abs(P_above - call_price)
    return value

def calculate_bollinger_bands(
    ticker: str, 
    period: int = 20, 
    std_dev: float = 2.0, 
    intraday: bool = True
) -> pd.DataFrame:
    """
    Calculate the Bollinger Bands for a given stock ticker using the yfinance module.

    Args:
        ticker (str): The stock ticker symbol.
        period (int): The period for the moving average and standard deviation (default is 20).
        std_dev (float): The number of standard deviations for the bands (default is 2.0).

    Returns:
        DataFrame: A DataFrame containing the closing prices, SMA, upper band, and lower band.
    """
    period += 1
    data = yf.download(ticker, period="1y", interval="1d", progress=False)
    
    if 'Close' not in data:
        raise ValueError("The data for the given ticker is not available.")

    if intraday:
        data = yf.download(ticker, period="1mo", interval="30m", progress=False)
        data.index = pd.to_datetime(data.index)
        data = data.between_time("10:00", "16:00")

    data['SMA'] = data['Close'].rolling(window=period).mean()
    data['STD'] = data['Close'].rolling(window=period).std()
    data['Upper Band'] = data['SMA'] + (std_dev * data['STD'])
    data['Lower Band'] = data['SMA'] - (std_dev * data['STD'])
    
    return data[['Close', 'SMA', 'Upper Band', 'Lower Band']]

def get_daily_volatility(ticker='^GSPC', period='1mo', interval='1d') -> float:
    """
    Calculate the daily volatility of the S&P 500 index.

    Parameters:
    - ticker (str): The ticker symbol for the index (default is '^GSPC').
    - period (str): The historical time range (e.g., '5d', '1mo').
    - interval (str): The interval for the data (e.g., '1d', '1h').

    Returns:
    - float: The daily volatility.
    """
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty:
            raise RuntimeError("No data fetched. Check ticker or internet connection.")
        close_prices = data['Close']
        if isinstance(close_prices, pd.DataFrame):
            close_prices = close_prices.squeeze()
        log_returns = np.log(close_prices / close_prices.shift(1)).dropna()
        daily_volatility = log_returns.std()
        return daily_volatility.item()
    except Exception as e:
        raise RuntimeError(f"Error calculating daily volatility: {e}")
    
def get_nyu_garch_vol(ticker='^GSPC') -> float: 
    tickers = {
        '^GSPC': "https://vlab.stern.nyu.edu/volatility/VOL.SPX%3AIND-R.GARCH",
        '^NDX':  "https://vlab.stern.nyu.edu/volatility/VOL.CCMP%3AIND-R.GARCH",
        '^DJI':  "https://vlab.stern.nyu.edu/volatility/VOL.INDU%3AIND-R.GARCH"
    }
    
    if ticker not in tickers:
        print(f"(GARCH Volatility) Ticker '{ticker}' not supported. Supported tickers are: {list(tickers.keys())}.")
        return 0
    
    url = tickers[ticker]
    response = requests.get(url)
    
    if response.status_code == 200:
        try:
            tgt = "font-weight:bold;padding-left:5px\">"
            idx = response.text.find(tgt) + len(tgt)
            s = response.text[idx:idx+5]
            while len(s) and not s[-1].isdigit():
                s = s[:-1]
            garch_vol = float(s) / 100
            return garch_vol
        except ValueError:
            print(ValueError("[get_nyu_garch_vol] Unable to parse the GARCH volatility from response text."))
    else:
        print(ConnectionError(f"[get_nyu_garch_vol] Failed to retrieve NYU GARCH volatility data. Status code: {response.status_code}"))
