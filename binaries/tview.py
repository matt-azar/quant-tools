from main import *
from os import system
from time import sleep
from datetime import datetime
from itertools import count

ticker = input("Ticker (default = ^GSPC): ")
ticker = "^GSPC" if ticker == "" else ticker

close = input("Closing hour [default=16]: ")
close = 16 if close == "" else int(close)

K = []

for i in count(1):
    k = input(f"K{i}: ")
    if not k:
        break
    try:
        K.append(float(k))
    except ValueError:
        print("Please enter a valid number for strike K.")

period = input("Refresh rate (seconds) [default=10]: ")
period = 10 if period == "" else int(period)

if __name__ == "__main__":
    while True:
        system('clear')
        print(f"{ticker} current price: {price(ticker):.2f} ({datetime.now():%D %T})\n")
        for k in K:
            print(f"K={k}")
            main(ticker, k, print_tau=False)
            print()
        main(print_tau=True)  
        sleep(period)
