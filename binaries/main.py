from binaries import *

def main(ticker, K, abbrev=False, info_only=False, ttt=None, close=16):
    if ttt is None:
        T = get_market_close(close)
        ttt = get_ttt(T)
    S0 = price(ticker)
    # vix = price('^VIX')
    vix = 0.0 # to suppress yf messages if vix isn't loading
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
            sigma = 1.00 * historical_vol
        case "ETH-USD":
            S0 = cryptoprice("ETH")
            sigma = 1.00 * historical_vol
        case _:
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
        print(f"GARCH Vol:       {garch_vol:.2%}") if garch_vol else None
        print(f"VIX:             {vix:.2f}") if vix else None
        if not info_only:
            print()
            print_P_above(S0, K, sigma, ttt=ttt, P_above=p_above)
    else:
        print(f"Above: {p_above:.2%}, Below: {1-p_above:.2%}")
        if close != 16:
            hours_remaining = 24 * 365 * ttt
            if hours_remaining < 1.0:
                print(f"Minutes to T: {60 * hours_remaining:.3f}")
            else:
                print(f"Hours to T: {hours_remaining:.3f}")

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