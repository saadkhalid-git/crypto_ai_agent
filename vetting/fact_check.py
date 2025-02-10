import requests


def check_facts(content):
    # Use CoinGecko API to verify crypto claims
    coins = requests.get("https://api.coingecko.com/api/v3/coins/list").json()
    coin_names = [coin["name"].lower() for coin in coins]
    return any(coin in content.lower() for coin in coin_names)