import numpy as np
from scipy.stats import norm
from datetime import datetime
from qftools import price, risk_free_rate, get_ttt, get_market_close, timezone_et

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
    if T:
        ttt = get_ttt(T)
    assert ttt > 0.0, "Time T has passed."
    mu = S0 + (r * S0) * ttt
    z = (mu - K) / (sigma * ttt**0.5)
    return norm.cdf(z)

def P(K, ticker, sigma):
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
