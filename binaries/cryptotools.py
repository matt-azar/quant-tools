import requests

def cryptoprice(coin = "BTC") -> float:
    urls = {
        "BTC": "https://www.cfbenchmarks.com/data/indices/BRTI",
        "ETH": "https://www.cfbenchmarks.com/data/indices/ETHUSD_RTI"
    }
    if coin not in urls:
        raise ValueError("Unsupported coin.")
    url = urls[coin]
    response = requests.get(url)
    tgt = "font-semibold tabular-nums md:text-2xl\">$"
    idx = response.text.find(tgt) + len(tgt)
    assert idx != -1, "Unable to parse price."
    s = response.text[idx:idx+10]
    while len(s) and not s[-1].isdigit():
        s = s[:-1]
    s = s.replace(",", "")
    return float(s)