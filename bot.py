from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import json
import requests
import db
from bitcoinutils.setup import setup
from bitcoinutils.keys import P2wpkhAddress, P2wshAddress, P2shAddress, PrivateKey, PublicKey
from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.script import Script, OP_CODES

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

config = {}
with open("configs/config.json", "r") as f:
    config = (json.load(f))

### COMMANDS

def help(update, ctx):
    user = update.message.from_user
    if user["username"]:
        if not db.checkUser(str(user["id"])):
            wif = genAddress()
            db.addUser(str(user["username"]), str(user["id"]), str(wif))
            ctx.bot.send_message(chat_id=update.message.chat_id, text=f"[{user['first_name']}](tg://user?id={user['id']}), You have been successfully registered", parse_mode="MarkdownV2")
            ctx.bot.send_message(chat_id=update.message.chat_id, text=f"""
    Hey there [{user['first_name']}](tg://user?id={user['id']})\\. Here are my commands:
    1\\. /help
    2\\. /price
    3\\. /tip @user amount
    4\\. /deposit
    5\\. /balance
            """, parse_mode="MarkdownV2")
        else:
            ctx.bot.send_message(chat_id=update.message.chat_id, text=f"""
    Hey there [{user['first_name']}](tg://user?id={user['id']})\\. Here are my commands:
    1\\. /help
    2\\. /price
    3\\. /tip @user amount
    4\\. /deposit
    5\\. /balance
            """, parse_mode="MarkdownV2")
    else:
        ctx.bot.send_message(chat_id=update.message.chat_id, text=f"[{user['first_name']}](tg://user?id={user['id']}), please set a username before using this bot", parse_mode="MarkdownV2")

def price(update, ctx):

    price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={config['coin']['coin_name']}&vs_currencies=usd,btc").json()

    btc = str(format(price["sugarchain"]["btc"], '.8f'))
    usd = str(price["sugarchain"]["usd"])

    ctx.bot.send_message(chat_id=update.message.chat_id, text=f"Current {config['coin']['ticker']}/BTC price: {btc} BTC\nCurrent {config['coin']['ticker']}/USD price: ${usd}")

def tipSomeone(update, ctx):
    user = update.message.from_user
    args = update.message.text.split(" ")

    if not db.checkUser(user["id"]):
        ctx.bot.send_message(chat_id=update.message.chat_id,
                             text="It looks like you haven't registered yet. Please run /help first to register yourself")
    else:
        target = None
        try:
            target = args[1][1:]
        except IndexError:
            target = target

        amount = None
        try:
            amount = args[2]
        except IndexError:
            amount = amount

        if target is not None:
            if not db.getUserID(target):
                ctx.bot.send_message(chat_id=update.message.chat_id,
                                     text="Oops, looks like your sending to a user who hasn't registered. Ask them to do /help to register!\nPlease be mindful that usernames are case senstive. Make sure that the case of the target is correct.")
            else:
                if user["username"] == target:
                    ctx.bot.send_message(chat_id=update.message.chat_id, text="😆 You can't tip yourself!")
                else:
                    if amount is not None:
                        if isFloat(amount):
                            if float(amount) > 0:
                                keyboard = [
                                    [InlineKeyboardButton("Yes", callback_data=f"Y, {target}, {amount}, {user['id']}"),
                                     InlineKeyboardButton("No", callback_data=f"N, {target}, {amount}, {user['id']}")]
                                ]
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                ctx.bot.send_message(chat_id=update.message.chat_id,
                                                     text=f"You are about to send {amount} {config['coin']['ticker']} to @{target}. Please click Yes to confirm",
                                                     reply_markup=reply_markup)
                            else:
                                ctx.bot.send_message(chat_id=update.message.chat_id,
                                                     text="You cannot send negative amounts!")
                        else:
                            ctx.bot.send_message(chat_id=update.message.chat_id,
                                                 text="Invalid amount of SUGAR. Please try again")
                    else:
                        ctx.bot.send_message(chat_id=update.message.chat_id, text="No amount specified!")
        else:
            ctx.bot.send_message(chat_id=update.message.chat_id, text="No user specified!")


def deposit(update, ctx):
    user = update.message.from_user

    if not db.checkUser(user["id"]):
        ctx.bot.send_message(chat_id=update.message.chat_id, text="It looks like you haven't registered yet. Please run /help first to register yourself")
    else:

        address = getAddress(user["id"])

        ctx.bot.send_message(chat_id=update.message.chat_id, text=f"Your deposit address: {address}")

def balance(update, ctx):
    user = update.message.from_user

    if not db.checkUser(user["id"]):
        ctx.bot.send_message(chat_id=update.message.chat_id, text="It looks like you haven't registered yet. Please run /help first to register yourself")
    else:
        balance = getBalance(user["id"])

        ctx.bot.send_message(chat_id=update.message.chat_id, text=f"You current balance: {balance} {config['coin']['ticker']}")

### FUNCTIONS

def isFloat(amount):
    try:
        float(amount)
        return True
    except ValueError:
        return False


def genAddress():
    # Initialise bitcoin.py
    setup('mainnet')

    priv = PrivateKey()
    wif = priv.to_wif(compressed=True)

    return wif


def tip(update, ctx):
    # Initialise bitcoin.py
    setup('mainnet')
    query = update.callback_query
    chID = query.message.chat.id
    msgID = query.message.message_id
    query.answer()
    data = str(query.data).split(", ")
    sender = str(query.from_user.id)
    target = db.getUserID(data[1])
    if sender == data[3]:
        if data[0] == "Y":
            ctx.bot.delete_message(chat_id=chID, message_id=msgID)
            sender_wif = db.getWIF(sender)
            target_address = getAddress(target)
            sender_address = getAddress(sender)
            sender_balance = getBalance(sender)
            value = 0
            amount = convertToSatoshis(float(data[2]))
            api = requests.get(f"{config['apiUrl']}/unspent/{sender_address}").json()["result"]
            print(api)
            print(sender_balance)
            ctx.bot.send_message(chat_id=chID, text=f"Success, sent @{data[1]} {data[2]} {config['coin']['ticker']}")
        elif data[0] == "N":
            ctx.bot.delete_message(chat_id=chID, message_id=msgID)
            ctx.bot.send_message(chat_id=chID, text=f"You declined sending @{data[1]} {data[2]} {config['coin']['ticker']}")


def getBalance(id: str):

    address = getAddress(id)

    getBalance = requests.get(f"{config['apiUrl']}/balance/{address}").json()["result"]["balance"]
    userBalance = getBalance / 100000000

    return userBalance


def getAddress(id: str):
    # Initialise bitcoin.py
    setup('mainnet')
    wif = db.getWIF(id)

    priv = PrivateKey.from_wif(f"{wif}")

    pub = priv.get_public_key()

    address = pub.get_segwit_address().to_string()

    return address

def convertToSatoshis(amount: float):
    return amount * 100000000


### LAUNCH

def main():

    updater = Updater(token=config["token"], use_context=True, workers=10)

    dispatcher = updater.dispatcher

    help_handler = CommandHandler('help', help)
    price_handler = CommandHandler('price', price)
    tip_command = CommandHandler('tip', tipSomeone)
    deposit_handler = CommandHandler('deposit', deposit)
    balance_handler = CommandHandler('balance', balance)
    tip_handler = CallbackQueryHandler(tip)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(price_handler)
    dispatcher.add_handler(tip_command)
    dispatcher.add_handler(tip_handler)
    dispatcher.add_handler(deposit_handler)
    dispatcher.add_handler(balance_handler)

    updater.start_polling()
    updater.idle()
    updater.stop()


if __name__ == '__main__':
    main()


