# SugarchainTGBot

##### A telegram tipbot which utilises a REST [api](https://api.sugarchain.org) and [python-bitcoin-utils](https://github.com/Nugetzrul3/python-bitcoin-utils)

### Config
1. Create a `configs` folder and make a new `config.json` file within it
2. Use the template below to suit your coin:
    
       {
          "token": "YOUR BOT TOKEN HERE",
          "coin": {
            "ticker": "COIN TICKER",
            "coin_name": "COIN NAME IN LOWERCASE",
            "minFee": "MINIMUM TX FEE"
          },
          "apiUrl": "API URL WITH ADDRESS INDEX"
        }

### How to run?
1. Clone this repository and create configs directory like shown above.
2. In the repository directory, run a python [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
3. Once virtual environment is running, clone this [repository](https://github.com/Nugetzrul3/python-bitcoin-utils)
4. In the `python-bitcoin-utils` directory, run `python3 setup.py install` and let it finish.
5. Go back to Telegram Bot directory and run `pip install -r requirements.txt`. This should install telegram.py and requests library.
6. Once completed, run `python3 bot.py`.
7. Success! The bot is now running 😀