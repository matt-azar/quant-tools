from binaries import *

def main(ticker, K, abbrev=False, info_only=False, ttt=None):
    if ttt is None:
        ttt = get_ttt()
    S0 = price(ticker)
    vix = price('^VIX')
    daily_vol = get_daily_volatility(ticker)
    historical_vol = daily_vol * 252**0.5
    garch_vol = get_nyu_garch_vol(ticker)
    
    if ticker == '^GSPC':
        sigma = max(vix / 100, garch_vol, historical_vol)
    elif ticker == '^NDX':
        sigma = max(1.5 * vix / 100, garch_vol, historical_vol)
    else:
        sigma = max(garch_vol, historical_vol)
        
    if ttt > 30 / 365:
        print("Black-Scholes pricing model.\n") if not abbrev else None
        p_above = blackscholes_P_above(S0, K, sigma, ttt=ttt)
    else:
        print("Bachelier pricing model.\n") if not abbrev else None
        p_above = bachelier_P_above(S0, K, sigma, ttt=ttt)
    
    if info_only or not abbrev:
        print(f"Daily Vol:       {daily_vol:.3%}, (S0 +/- {S0*daily_vol:.2f})")
        print(f"Historical Vol:  {historical_vol:.2%}")
        print(f"GARCH Vol:       {garch_vol:.2%}") if garch_vol else print("GARCH Vol:\t N/A")
        print(f"VIX:             {vix:.2f}")
        if not info_only:
            print()
            print_P_above(S0, K, sigma, ttt=ttt, P_above=p_above)
    else:
        print(f"Above: {p_above:.2%}, Below: {1-p_above:.2%}")

if __name__ == "__main__":
    ticker = input("Ticker (default = ^GSPC): ")
    ticker = "^GSPC" if ticker == "" else ticker

    K = float(input("Strike: "))
    
    abbrev = input("Abbreviated info? [y/N]: ")
    abbrev = True if abbrev == "y" else False

    info_only = input("Info only? [y/N]: ")
    info_only = True if info_only == "y" else False

    print(f"\n{ticker} current price: {price(ticker):.2f} ({datetime.now():%D %T})\n")
    
    main(ticker, K, abbrev, info_only)