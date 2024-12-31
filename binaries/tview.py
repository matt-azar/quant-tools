from binaries import *
from main import main
from os import system
from time import sleep
from datetime import datetime

ticker = input("Ticker (default = ^GSPC): ")
ticker = "^GSPC" if ticker == "" else ticker

now = datetime.now()
default_date = now.replace(hour=16, minute=0, second=0, microsecond=0)
default_date_str = default_date.strftime("%Y%m%d%H")

date = (
    input(f"Expiration (yyyymmddhh) [default: {default_date_str}]: ") 
    or default_date_str
)
year = int(date[:4])
month = int(date[4:6])
day = int(date[6:8])
hour = int(date[8:])

T = get_T(
    year=year,
    month=month,
    day=day,
    hour=hour
)

K = float(input("K: "))
period = input("Period: ")
period = int(period) if period != "" else 10

if __name__ == "__main__":
    while 1:
        system('clear')
        print(f"{ticker} current price: {price(ticker):.2f} ({datetime.now():%D %T})\n")
        print(f"{K=:.2f}")
        main(ticker, K, abbrev=True)
        print()
        sleep(period)
