import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
from numpy import log
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import requests

timezone_et = ZoneInfo('America/New_York')

def price(ticker: str) -> float:
    try:
        data = yf.download(ticker, period='1d', interval='1m', progress=False)
        S0 = data[('Adj Close', ticker)].iloc[-1]
        return S0
    except Exception:
        # yf.download() generates error message automatically.
        return 0.0

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
        # print("Unable to download risk-free rate. Using default value.")
        return 0.04
    
risk_free_rate = get_r()

def get_T(year, month, day, hour) -> datetime:
    return datetime(year, month, day, hour, tzinfo=timezone_et)

def get_market_close(h: int = 16) -> datetime:
    T = datetime.now(tz=timezone_et)
    if T.hour >= h:
        T = T.replace(day=T.day+1)
    T = T.replace(hour=h, minute=0, second=0, microsecond=0)
    return T

def get_tau(T: datetime = get_market_close()) -> float:
    """
    Calculate the time in years until time T.
    """
    t = datetime.now(tz=timezone_et)
    tau = T - t
    years = tau.total_seconds() / (365 * 24 * 60 * 60)
    assert years > 0.0, "Time T has passed."
    return years
  
def calculate_historical_volatility(returns: pd.DataFrame) -> float:
    """
    Calculate historical volatility over the timeframe of a set of returns.
    """
    sigma = returns.std()
    volatility = sigma * len(returns)**0.5
    return volatility 

def get_1y_prices(ticker: str) -> pd.DataFrame:
    data = yf.download(ticker, period='1y', interval='1d', progress=False)
    adj_close_prices = data[('Adj Close', ticker)]
    adj_close_prices.dropna(inplace=True)
    daily_returns = adj_close_prices.pct_change().dropna()
    return daily_returns

def calculate_apy(tau, at_risk=None, to_win=100.0) -> float:
    """
    When to_win=100.0, at_risk can be interpreted as price in cents per share.
    """
    profit = to_win / at_risk
    rate = log(profit) / tau
    return rate * 100

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
        log_returns = log(close_prices / close_prices.shift(1)).dropna()
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
        # print(f"(GARCH Volatility) Ticker '{ticker}' not supported. Supported tickers are: {list(tickers.keys())}.")
        return 0.0
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
