# SugarchainTGBot

##### A telegram tipbot which utilises a REST [api](https://api.sugarchain.org) and [python-bitcoin-utils](https://github.com/Nugetzrul3/python-bitcoin-utils)

### Config
1. Create a `configs` folder and make a new `config.py` file within it
2. Use the template below to suit your coin:

```python
token = "BOT_API_TOKEN"
coin = {
    "ticker": "COIN_TICKER",
    "coin_name": "coin_name_lowercase",
    "minFee": "MINIMUM_TX_RELAY_FEE",
    "P2PKH_PREFIX": "PREFIX_IN_BYTE_FORM (EXAMPLE: b'\x3F')",
    "P2SH_PREFIX": "PREFIX_IN_BYTE_FORM",
    "WIF_PREFIX": "PREFIX_IN_BYTE_FORM",
    "bech32": "bech32_segwit_prefix"
}
apiUrl = "API_URL_WITH_ADDRESSINDEX_ENABLED"
```

### How to run?
1. Clone this repository and create configs directory like shown above.
2. In the repository directory, run a python [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
3. Once virtual environment is running, run `pip install -r requirements.txt`. This will install all required libraries.
4. Once completed, run `python3 bot.py`.
5. Success! The bot is now running 😀