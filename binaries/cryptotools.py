import requests

def cryptoprice(coin = "BTC") -> float:
    match coin:
        case "BTC":
            url = "https://www.cfbenchmarks.com/data/indices/BRTI"
        case "ETH":
            url = "https://www.cfbenchmarks.com/data/indices/ETHUSD_RTI"
        case _:
            print("Enter a valid coin.")
            return 0.0
    response = requests.get(url)
    tgt = "font-semibold tabular-nums md:text-2xl\">$"
    idx = response.text.find(tgt) + len(tgt)
    s = response.text[idx:idx+10]
    while len(s) and not s[-1].isdigit():
        s = s[:-1]
    s = s.replace(",", "")
    return float(s)