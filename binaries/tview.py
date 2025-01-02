from main import *
from os import system
from time import sleep
from datetime import datetime

ticker = input("Ticker (default = ^GSPC): ")
ticker = "^GSPC" if ticker == "" else ticker

close = input("Closing hour [default=16]: ")
close = 16 if close == "" else int(close)

K = float(input("K: "))
period = input("Refresh rate (seconds) [default=10]: ")
period = 10 if period == "" else int(period)

if __name__ == "__main__":
    while 1:
        system('clear')
        print(f"{ticker} current price: {price(ticker):.2f} ({datetime.now():%D %T})\n")
        print(f"{K=:.2f}")
        main(ticker, K, abbrev=True, close=close)
        print()
        sleep(period)
