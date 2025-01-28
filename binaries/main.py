from binaries import above, print_P_above
from qftools import get_market_close, get_tau, price, get_daily_volatility, get_nyu_garch_vol
from cryptotools import cryptoprice
from datetime import datetime

def main(
    ticker    = "^GSPC",
    K         = 0,
    abbrev    = True,
    info_only = False,
    tau       = None,
    close     = 16,
    print_tau = False,
    S0        = None,
):
    if tau is None:
        T = get_market_close(close)
        tau = get_tau(T)
    if S0 is None: S0 = price(ticker)
    vix = price('^VIX')
    daily_vol = get_daily_volatility(ticker)
    historical_vol = daily_vol * 252**0.5
    garch_vol = get_nyu_garch_vol(ticker)
    
    match ticker:
        case "^GSPC":
            sigma = max(vix / 100, garch_vol, historical_vol)
        case "^NDX":
            sigma = max(1.5 * vix / 100, garch_vol, historical_vol)
        case "BTC-USD":
            S0 = cryptoprice("BTC")
            sigma = 1.02 * historical_vol
        case "ETH-USD":
            S0 = cryptoprice("ETH")
            sigma = 1.02 * historical_vol
        case _:
            sigma = max(garch_vol, historical_vol)
        
    p_above = above(S0, K, sigma, tau=tau)
    
    if info_only or not abbrev:
        print(f"Daily Vol:       {daily_vol:.3%}, (S0 +/- {S0*daily_vol:.2f})")
        print(f"Historical Vol:  {historical_vol:.2%}")
        print(f"GARCH Vol:       {garch_vol:.2%}") if garch_vol else None
        print(f"VIX:             {vix:.2f}") if vix else None
        if not info_only:
            print()
            print_P_above(S0, K, sigma, tau=tau, P_above=p_above)
    else:
        print(f"Above: {p_above:.2%}\nBelow: {1-p_above:.2%}") if K else None
        if print_tau:
            hours_remaining = 24 * 365 * tau
            print(f"Hours to T: {hours_remaining:.3f} ({close=})")

if __name__ == "__main__":
    ticker = input("Ticker (default = ^GSPC): ")
    ticker = "^GSPC" if ticker == "" else ticker

    K = float(input("Strike: "))
    
    abbrev = input("Abbreviated info? [y/N]: ")
    abbrev = True if abbrev == "y" else False

    info_only = input("Info only? [y/N]: ")
    info_only = True if info_only == "y" else False

    print(f"\n{ticker} current price: {price(ticker):.2f} ({datetime.now():%D %T})\n")
    
    main(ticker=ticker, K=K, abbrev=abbrev, info_only=info_only)