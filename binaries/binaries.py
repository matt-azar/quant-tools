from math import log
from numpy import random
from scipy.stats import norm
from datetime import datetime
from qftools import price, risk_free_rate, get_tau, get_market_close, timezone_et, get_daily_volatility

def above(
    S0: float, 
    K: float, 
    sigma: float, 
    T: datetime = None, 
    tau: float = None, 
    r: float = risk_free_rate,
    rho: float = -5.0,
    stochastic_sigma: callable = None,
) -> float:
    """
    Calculate the probability that the price of a security will be above K
    at time T using the Black-Scholes model.

    Parameters:
        S0 (float): Initial price of the security.
        K (float): Strike price.
        sigma (float): Volatility.
        T (datetime, optional): Time of maturity.
        tau (float, optional): Time to maturity in years.
        r (float): Risk-free rate.
        rho (float): Sensitivity of volatility to price changes.
        stochastic_sigma (callable, optional): A function that takes (t, sigma, *args) and returns 
            the volatility for a given time t. If None, uses constant volatility.

    Returns:
        float: Probability that the price will exceed K at time T.
    """
    if not K: return -1
    if T:
        tau = get_tau(T)
    assert tau > 0.0, "Time T has passed."

    # NOTE: Added 1/29/2025. Experimental.
    sigma1 = sigma * (1 + rho * (K - S0) / S0)
    sigma1 -= (sigma1 - sigma) / 2
    sigma = sigma1
    
    # NOTE: Added 1/28/2025. Experimental.
    if stochastic_sigma:
        sigma = stochastic_sigma(0, sigma)
        
    d1 = (log(S0 / K) + (0.5 * sigma**2 + r) * tau) / (sigma * tau**0.5)
    d2 = d1 - sigma * tau**0.5
    
    return norm.cdf(d2)

def get_VoV() -> float:
    """
    Returns:
        float: Annualized historical volatility of volatility for the SP500.
    """
    try:
        return get_daily_volatility('^VIX') * 252**0.5
    except:
        return 0

# TODO: figure out how to use this
def stochastic_vol(
    sigma: float,
    mean_reversion: float = 0.1, 
    vol_of_vol: float = get_VoV(),
    long_term_vol: float = 0.25, 
    dt: float = 1/(60*24)/252,
) -> float:
    """
    Stochastic volatility model based on an Ornstein-Uhlenbeck process, suitable for short-term market volatility.

    Parameters:
        base_sigma (float): Initial or previous volatility.
        mean_reversion (float): Speed at which volatility reverts to the long-term mean.
        vol_of_vol (float): The standard deviation of volatility changes (volatility of volatility).
        long_term_vol (float): The long-term mean volatility (mean reversion target).
        dt (float): Time step in years (default assumes 1-minute steps).

    Returns:
        float: New volatility value for the next step.
    """
    drift = mean_reversion * (long_term_vol - sigma) * dt
    diffusion = vol_of_vol * dt**0.5 * random.normal()
    new_sigma = sigma + drift + diffusion
    diff = abs(sigma - new_sigma)
    print(diff)
    return sigma + diff # interested in worst case scenario (max volatility)

# NOTE: Probably useless for binary options...
def bachelier_P_above(
    S0: float, 
    K: float, 
    sigma: float, 
    T: datetime = None, 
    tau: float = None, 
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
        tau (float, optional): Time to maturity in years.
        r (float): Risk-free rate.

    Returns:
        float: Probability that the price will exceed K at time T.
    """
    # sigma *= S0 # converts volatility to absolute volatility
    # (makes the Bachelier model nearly identical to GBM)
    if T:
        tau = get_tau(T)
    assert tau > 0.0, "Time T has passed."
    mu = S0 + (r * S0) * tau
    z = (mu - K) / (sigma * tau**0.5)
    return norm.cdf(z)

# NOTE: isn't this just black scholes?
def gbm_above(
    S0: float, 
    K: float, 
    sigma: float, 
    T: datetime = None, 
    tau: float = None, 
    r: float = risk_free_rate
) -> float:
    """
    Calculate the probability that the price of a security will be above K
    at time T using the Geometric Brownian Motion (GBM) model.

    Parameters:
        S0 (float): Initial price of the security.
        K (float): Strike price.
        sigma (float): Relative volatility (GBM).
        T (datetime, optional): Time of maturity.
        tau (float, optional): Time to maturity in years.
        r (float): Risk-free rate.

    Returns:
        float: Probability that the price will exceed K at time T.
    """
    if T:
        tau = get_tau(T)
    assert tau > 0.0, "Time T has passed."
    
    # Adjust drift for GBM
    drift = log(S0) + (r - 0.5 * sigma**2) * tau
    volatility = sigma * tau**0.5
    
    # Calculate the standard normal z-score
    z = (drift - log(K)) / volatility
    
    return norm.cdf(z)


# def P(K, ticker, sigma):
    # return bachelier_P_above(S0=price(ticker), K=K, sigma=sigma, T=get_market_close())

def print_P_above(S0, K, sigma, T=None, tau=None, P_above=None) -> None:
    if not P_above:
        P_above = above(S0, K, sigma, T)
    if tau is None:
        assert T, "Input a time T or a time until expiration tau."
        tau = get_tau(T)
    assert tau > 0.0, "Time T has passed."
    hours_remaining = 24 * 365 * tau
    print(f"Datetime:       {datetime.now(tz=timezone_et):%D %T} ET")
    print(f"Hours to T:     {hours_remaining:.3f}")
    print() 
    print(f"Price:          {S0:,.2f}")
    print(f"Strike price:   {K:,}")
    print()
    print(f"Volatility:     {sigma:.4f}")
    print(f"Risk-free rate: {risk_free_rate:.4f}")
    print()
    print(f"P(above)%:      {P_above:.4%}")
    print(f"P(below)%:      {1 - P_above:.4%}")

def get_value(P_above: float, call_price: float) -> float:
    if P_above > call_price:
        print("Buy yes.")
    else:
        print("Buy no.")
    value = abs(P_above - call_price)
    return value
