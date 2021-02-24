from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.utils.helpers import escape_markdown

from datetime import datetime
from decimal import Decimal
import strict_rfc3339
import threading
import requests
import platform
import logging
import time
import db
import os

from bitcoinutils.transactions import Transaction, TxInput, TxOutput
from bitcoinutils.keys import P2wpkhAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.setup import setup
from bitcoinutils import constants

from configs import config
from langs import langs as lang

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

### COMMANDS

timestart = int(time.time())

constants.NETWORK_WIF_PREFIXES['mainnet'] = config.coin['WIF_PREFIX']
constants.NETWORK_SEGWIT_PREFIXES['mainnet'] = config.coin['bech32']
constants.NETWORK_P2PKH_PREFIXES['mainnet'] = config.coin['P2PKH_PREFIX']
constants.NETWORK_P2SH_PREFIXES['mainnet'] = config.coin['P2SH_PREFIX']

def help(update, ctx):
    gettime = str(update.message.date).split()
    timetoconvert = gettime[0] + "T" + gettime[1]
    timestamp = strict_rfc3339.rfc3339_to_timestamp(timetoconvert)

    print(update.message.chat_id)

    if timestart < int(timestamp):

        user = update.message.from_user
        language = str()

        if update.message.chat.type == "private":
            language = db.getLang(user["id"])
        else:
            language = getLang(update.message.chat_id)

        if user["username"]:
            if not db.checkUser(str(user["id"])):
                wif = genAddress()
                db.addUser(str(user["username"]), str(user["id"]), str(wif))
                ctx.bot.send_message(chat_id=update.message.chat_id, text=f"[{escape_markdown(user['first_name'], 2)}](tg://user?id={user['id']}), {lang[language]['help']['success-regsiter']}", parse_mode="MarkdownV2")
                if update.message.chat.type == "private":
                    ctx.bot.send_message(chat_id=update.message.chat_id, text=f"""
{lang[language]['help']['part-1']} [{escape_markdown(user['first_name'], 2)}](tg://user?id={user['id']})\\. {lang[language]['help']['part-2']}
1\\. /help
2\\. /price
3\\. /info
4\\. /tip @user amount
5\\. /deposit
6\\. /balance
7\\. /withdraw address amount
8\\. /export
9\\. /setlang lang \\(en, zh, id\\)
10\\. /about
                    """, parse_mode="MarkdownV2")
                    ctx.bot.send_message(chat_id=update.message.chat_id,
                                         text=lang[language]['help']['warning-msg'],
                                         parse_mode="MarkdownV2")
                else:
                    ctx.bot.send_message(chat_id=update.message.chat_id, text=f"""
{lang[language]['help']['part-1']} [{escape_markdown(user['first_name'], 2)}](tg://user?id={user['id']})\\. {lang[language]['help']['part-2']}
1\\. /help
2\\. /price
3\\. /tip @user amount
                    """, parse_mode="MarkdownV2")
                    ctx.bot.send_message(chat_id=update.message.chat_id,
                                         text=lang[language]['help']['warning-msg'],
                                         parse_mode="MarkdownV2")
            else:
                if user["username"] != db.getUserName(str(user["id"])):
                    db.updateUser(str(user["id"]), user["username"])

                if update.message.chat.type == "private":

                    ctx.bot.send_message(chat_id=update.message.chat_id, text=f"""
{lang[language]['help']['part-1']} [{escape_markdown(user['first_name'], 2)}](tg://user?id={user['id']})\\. {lang[language]['help']['part-2']}
1\\. /help
2\\. /price
3\\. /info
4\\. /tip @user amount
5\\. /deposit
6\\. /balance
7\\. /withdraw address amount
8\\. /export
9\\. /setlang lang \\(en, zh, id\\)
10\\. /about
                    """, parse_mode="MarkdownV2")
                    ctx.bot.send_message(chat_id=update.message.chat_id,
                                         text=lang[language]['help']['warning-msg'],
                                         parse_mode="MarkdownV2")
                else:
                    ctx.bot.send_message(chat_id=update.message.chat_id, text=f"""
{lang[language]['help']['part-1']} [{escape_markdown(user['first_name'], 2)}](tg://user?id={user['id']})\\. {lang[language]['help']['part-2']}
1\\. /help
2\\. /price
3\\. /tip @user amount
                    """, parse_mode="MarkdownV2")
                    ctx.bot.send_message(chat_id=update.message.chat_id,
                                         text=lang[language]['help']['warning-msg'],
                                         parse_mode="MarkdownV2")
        else:
            ctx.bot.send_message(chat_id=update.message.chat_id, text=f"[{escape_markdown(user['first_name'], 2)}](tg://user?id={user['id']}), please set a username before using this bot", parse_mode="MarkdownV2")

def price(update, ctx):
    gettime = str(update.message.date).split()
    timetoconvert = gettime[0] + "T" + gettime[1]
    timestamp = strict_rfc3339.rfc3339_to_timestamp(timetoconvert)

    if timestart < int(timestamp):

        price = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={config.coin['coin_name']}&vs_currencies=usd,btc").json()

        btc = str(format(price["sugarchain"]["btc"], '.8f'))
        usd = str(price["sugarchain"]["usd"])

        ctx.bot.send_message(chat_id=update.message.chat_id, text=f"""
Current {config.coin['ticker']}/BTC price: {btc} BTC
Current {config.coin['ticker']}/USD price: ${usd}
""", parse_mode="HTML")

def info(update, ctx):
    gettime = str(update.message.date).split()
    timetoconvert = gettime[0] + "T" + gettime[1]
    timestamp = strict_rfc3339.rfc3339_to_timestamp(timetoconvert)

    if timestart < int(timestamp):

        user = update.message.from_user
        language = str()

        if update.message.chat.type == "private":
            language = db.getLang(user["id"])
        else:
            language = getLang(update.message.chat_id)

        if update.message.chat.type == "private":

            info = requests.get(f"{config.apiUrl}/info").json()

            height = str(info["result"]["blocks"])
            hashrate = formathash(info["result"]["nethash"])
            diff = format(info["result"]["difficulty"], ".8f")
            supply = format(info["result"]["supply"] / 100000000, ".8f")

            ctx.bot.send_message(chat_id=update.message.chat_id, text=f"""
{lang[language]['info']['block-height']} <code>{height}</code>
{lang[language]['info']['net-hash']} <code>{hashrate}</code>
{lang[language]['info']['difficulty']} <code>{diff}</code>
{lang[language]['info']['supply']} <code>{supply}</code> {config.coin["ticker"]}
""", parse_mode="HTML")
        else:
            ctx.bot.send_message(chat_id=update.message.chat_id,
                                 text=lang[language]['error']['general']['dm-only'])

def tip(update, ctx):
    gettime = str(update.message.date).split()
    timetoconvert = gettime[0] + "T" + gettime[1]
    timestamp = strict_rfc3339.rfc3339_to_timestamp(timetoconvert)

    if timestart < int(timestamp):

        user = update.message.from_user
        args = update.message.text.split(" ")

        language = str()

        if update.message.chat.type == "private":
            language = db.getLang(user["id"])
        else:
            language = getLang(update.message.chat_id)

        if not db.checkUser(user["id"]):
            ctx.bot.send_message(chat_id=update.message.chat_id,
                                 text=lang[language]['error']['general']['dm-only'])
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
                                         text=lang[language]['error']['tip']['re-register'])
                else:
                    if user["username"] == target:
                        ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[language]['tip']['tip-yourself'])
                    else:
                        if amount is not None:
                            if isFloat(amount):
                                if float(amount) > float(config.coin['minFee']):
                                    print(db.getUserID(target))
                                    keyboard = [
                                        [
                                            InlineKeyboardButton("Yes", callback_data=f"Y,{db.getUserID(target)},{amount},{user['id']},t"),
                                            InlineKeyboardButton("No", callback_data=f"N,{db.getUserID(target)},{amount},{user['id']},t")
                                        ]
                                    ]
                                    reply_markup = InlineKeyboardMarkup(keyboard)
                                    ctx.bot.send_message(chat_id=update.message.chat_id,
                                                         text=f"{lang[language]['tip']['part-1']} {amount} {config.coin['ticker']} {lang[language]['tip']['part-2']} {format(float(config.coin['minFee']), '.8f')} {lang[language]['tip']['part-2']} @{target}. {lang[language]['tip']['part-4']}",
                                                         reply_markup=reply_markup)
                                else:
                                    ctx.bot.send_message(chat_id=update.message.chat_id,
                                                         text=lang[language]['error']['tip']['negative-amount'])
                            else:
                                ctx.bot.send_message(chat_id=update.message.chat_id,
                                                     text=lang[language]['error']['tip']['invalid-amount'])
                        else:
                            ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[language]['error']['tip']['no-amount'])
            else:
                ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[language]['error']['tip']['no-user'])

def deposit(update, ctx):
    gettime = str(update.message.date).split()
    timetoconvert = gettime[0] + "T" + gettime[1]
    timestamp = strict_rfc3339.rfc3339_to_timestamp(timetoconvert)

    if timestart < int(timestamp):

        user = update.message.from_user
        userlang = db.getLang(user['id'])

        if update.message.chat.type == "private":

            if not db.checkUser(user["id"]):
                ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['error']['not-registered'])
            else:

                address = getAddress(user["id"])

                ctx.bot.send_message(chat_id=update.message.chat_id, text=f"{lang[userlang]['deposit']['part-1']} <code>{address}</code>", parse_mode="HTML")

        else:
            ctx.bot.send_message(chat_id=update.message.chat_id,
                                 text=lang[userlang]['error']['general']['dm-only'])

def balance(update, ctx):
    gettime = str(update.message.date).split()
    timetoconvert = gettime[0] + "T" + gettime[1]
    timestamp = strict_rfc3339.rfc3339_to_timestamp(timetoconvert)

    if timestart < int(timestamp):

        user = update.message.from_user
        userlang = db.getLang(user['id'])

        if update.message.chat.type == "private":

            if not db.checkUser(user["id"]):
                ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['error']['not-registered'])
            else:
                balance = getBalance(user["id"])

                ctx.bot.send_message(chat_id=update.message.chat_id, text=f"{lang[userlang]['balance']['part-1']} {balance} {config.coin['ticker']}")
        else:
            ctx.bot.send_message(chat_id=update.message.chat_id,
                                 text=lang[userlang]['error']['general']['dm-only'])

def withdraw(update, ctx):
    gettime = str(update.message.date).split()
    timetoconvert = gettime[0] + "T" + gettime[1]
    timestamp = strict_rfc3339.rfc3339_to_timestamp(timetoconvert)

    if timestart < int(timestamp):

        user = update.message.from_user
        userlang = db.getLang(user["id"])

        if update.message.chat.type == "private":

            args = update.message.text.split(" ")
            sender_address = getAddress(user['id'])

            if not db.checkUser(user['id']):
                ctx.bot.send_message(chat_id=update.message.chat_id,
                                     text=lang[userlang]['error']['not-registered'])
            else:
                address = None
                try:
                    address = str(args[1])[7:]
                except IndexError:
                    address = address

                amount = None
                try:
                    amount = args[2]
                except IndexError:
                    amount = amount

                if address is not None:
                    if checkAdd("sugar1q" + address):
                        if ("sugar1q" + address) != str(sender_address):
                            if amount is not None:
                                if isFloat(amount):
                                    if float(amount) > float(config.coin['minFee']):
                                        keyboard = [
                                            [
                                                InlineKeyboardButton("Yes", callback_data=f"Y,{address},{amount},{user['id']},w"),
                                                InlineKeyboardButton("No", callback_data=f"N,{address},{amount},{user['id']},w")
                                            ]
                                        ]
                                        reply_markup = InlineKeyboardMarkup(keyboard)
                                        ctx.bot.send_message(chat_id=update.message.chat_id,
                                                             text=f"{lang[userlang]['withdraw']['part-1']} {amount} {config.coin['ticker']}, {lang[userlang]['withdraw']['part-2']} {format(float(config.coin['minFee']), '.8f')} {lang[userlang]['withdraw']['part-3']} {'sugar1q' + address}. {lang[userlang]['withdraw']['part-4']}",
                                                             reply_markup=reply_markup)
                                    else:
                                        ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['error']['withdraw']['negative-amount'])
                                else:
                                    ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['error']['withdraw']['invalid-amount'])
                            else:
                                ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['error']['withdraw']['no-amount'])
                        else:
                            ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['error']['withdraw']['same-address'])
                    else:
                        ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['error']['withdraw']['invalid-address'])
                else:
                    ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['error']['withdraw']['no-address'])

        else:
            ctx.bot.send_message(chat_id=update.message.chat_id,
                                 text=lang[userlang]['error']['dm-only'])

def export(update, ctx):
    gettime = str(update.message.date).split()
    timetoconvert = gettime[0] + "T" + gettime[1]
    timestamp = strict_rfc3339.rfc3339_to_timestamp(timetoconvert)

    if timestart < int(timestamp):
        user = update.message.from_user
        userlang = db.getLang(user["id"])
        if update.message.chat.type == "private":
            ctx.bot.send_message(chat_id=update.message.chat_id, text=f"{lang[userlang]['export']['part-1']} <code>{db.getWIF(user['id'])}</code>. {lang[userlang]['export']['part-2']}", parse_mode="HTML")
        else:
            ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['error']['general']['dm-only'])

def setLang(update, ctx):
    gettime = str(update.message.date).split()
    timetoconvert = gettime[0] + "T" + gettime[1]
    timestamp = strict_rfc3339.rfc3339_to_timestamp(timetoconvert)

    if timestart < int(timestamp):
        user = update.message.from_user
        args = update.message.text.split(" ")
        language = getLang(update.message.chat_id)

        if update.message.chat.type == "private":
            if args[1] in ["en", "zh", "id", "ru"]:
                if args[1] == db.getLang(user["id"]):
                    userlang = db.getLang(user["id"])
                    ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['setlang']['same-lang'])
                else:
                    db.setLang(user["id"], args[1])
                    userlang = db.getLang(user["id"])
                    ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['setlang']['set-lang'])
            else:
                userlang = db.getLang(user["id"])
                ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[userlang]['setlang']['invalid-lang'])
        else:
            ctx.bot.send_message(chat_id=update.message.chat_id, text=lang[language]['error']['general']['dm-only'])

def about(update, ctx):
    gettime = str(update.message.date).split()
    timetoconvert = gettime[0] + "T" + gettime[1]
    timestamp = strict_rfc3339.rfc3339_to_timestamp(timetoconvert)

    if timestart < int(timestamp):
        user = update.message.from_user
        language = getLang(update.message.chat_id)
        if update.message.chat.type == "private":
            ctx.bot.send_message(chat_id=update.message.chat_id,
                                 text=lang[language]['about'], parse_mode="MarkdownV2")
        else:
            ctx.bot.send_message(chat_id=update.message.chat_id,
                                 text=lang[language]['error']['general']['dm-only'])

### FUNCTIONS

def isFloat(amount):
    try:
        float(amount)
        return True
    except ValueError:
        return False

def getLang(chatid):
    if str(chatid) == config.chat['chinese']:
        return 'zh'
    elif str(chatid) == config.chat['indonesian']:
        return 'id'
    elif str(chatid) == config.chat['russian']:
        return 'ru'
    else:
        return 'en'

def formathash(hash: int):
    if hash < 1e3:
        return format(hash, ".2f") + " H/s"
    elif 1e3 <= hash < 1e6:
        return format(hash / 1e3, ".2f") + " KH/s"
    elif 1e6 <= hash < 1e9:
        return format(hash / 1e6, ".2f") + " MH/s"
    elif 1e9 <= hash < 1e12:
        return format(hash / 1e9, ".2f") + " GH/s"
    elif 1e12 <= hash < 1e15:
        return format(hash / 1e12, ".2f") + " TH/s"


def genAddress():
    # Initialise bitcoin.py
    setup('mainnet')

    priv = PrivateKey()
    wif = priv.to_wif(compressed=True)

    return wif


def tip_or_withdrawFunc(update, ctx):
    # Initialise bitcoin.py
    setup('mainnet')
    query = update.callback_query
    chID = query.message.chat.id
    msgID = query.message.message_id
    query.answer()
    data = str(query.data).split(",")
    sender = str(query.from_user.id)
    userlang = db.getLang(sender)
    if sender == data[3]:
        if data[4] == "t":
            target = data[1]
            if data[0] == "Y":
                ctx.bot.delete_message(chat_id=chID, message_id=msgID)

                sender_wif = PrivateKey(db.getWIF(sender))
                fee = convertToSatoshis(Decimal(config.coin['minFee']))
                target_address = P2wpkhAddress(getAddress(target))
                sender_address = P2wpkhAddress(getAddress(sender))
                sender_balance = 0
                amount = convertToSatoshis(Decimal(data[2])) + fee

                unspent = requests.get(f"{config.apiUrl}/unspent/{sender_address.to_string()}").json()["result"]
                txin = []
                for i in range(0, len(unspent)):
                    sender_balance += unspent[i]['value']
                    txin.append(TxInput(unspent[i]['txid'], unspent[i]['index']))

                if sender_balance >= amount:

                    txout = []
                    txout.append(TxOutput((amount - fee), target_address.to_script_pub_key()))

                    txchange = sender_balance - amount
                    if txchange > 0:
                        txout.append(TxOutput(txchange, sender_address.to_script_pub_key()))

                    script_code = Script(['OP_DUP', 'OP_HASH160', sender_wif.get_public_key().to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])

                    tx = Transaction(txin, txout, has_segwit=True)

                    tx.witnesses = []

                    for i in range(0, len(unspent)):
                        value = unspent[i]['value']
                        sig = sender_wif.sign_segwit_input(tx, i, script_code, value)
                        tx.witnesses.append(Script([sig, sender_wif.get_public_key().to_hex()]))

                    post_data = {
                        'raw': tx.serialize()
                    }

                    txid = requests.post(f"{config.apiUrl}/broadcast", data=post_data).json()['result']

                    ctx.bot.send_message(chat_id=chID, text=f"{lang[userlang]['tip-yes-no']['text-yes']} @{db.getUserName(data[1])} {data[2]} {config.coin['ticker']}.")
                    ctx.bot.send_message(chat_id=chID, text=f"[{lang[userlang]['tip-yes-no']['view-transaction']}](https://sugar\\.wtf/esplora/tx/{str(txid)})", parse_mode="MarkdownV2")
                else:
                    ctx.bot.send_message(chat_id=chID, text=lang[userlang]['error']['tip']['insufficient-funds'])

            elif data[0] == "N":
                ctx.bot.delete_message(chat_id=chID, message_id=msgID)
                ctx.bot.send_message(chat_id=chID, text=f"{lang[userlang]['tip-yes-no']['text-no']} @{db.getUserName(data[1])} {data[2]} {config.coin['ticker']}")

        elif data[4] == "w":
            if data[0] == "Y":
                ctx.bot.delete_message(chat_id=chID, message_id=msgID)

                sender_wif = PrivateKey(db.getWIF(sender))
                fee = convertToSatoshis(Decimal(config.coin['minFee']))
                sender_address = P2wpkhAddress(getAddress(sender))
                sender_balance = 0
                amount = convertToSatoshis(Decimal(data[2])) + fee
                target_address = P2wpkhAddress("sugar1q" + data[1])

                unspent = requests.get(f"{config.apiUrl}/unspent/{sender_address.to_string()}").json()['result']

                txin = []
                for i in range(0, len(unspent)):
                    sender_balance += unspent[i]['value']
                    txin.append(TxInput(unspent[i]['txid'], unspent[i]['index']))

                if sender_balance >= amount:
                    txout = []
                    
                    txout.append(TxOutput((amount - fee), target_address.to_script_pub_key()))

                    txchange = sender_balance - amount
                    if txchange > 0:
                        txout.append(TxOutput(txchange, sender_address.to_script_pub_key()))

                    script_code = Script(['OP_DUP', 'OP_HASH160', sender_wif.get_public_key().to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])

                    tx = Transaction(txin, txout, has_segwit=True)

                    tx.witnesses = []

                    for i in range(0, len(unspent)):
                        value = unspent[i]['value']
                        sig = sender_wif.sign_segwit_input(tx, i, script_code, value)
                        tx.witnesses.append(Script([sig, sender_wif.get_public_key().to_hex()]))

                    post_data = {
                        'raw': tx.serialize()
                    }

                    txid = requests.post(f"{config.apiUrl}/broadcast", data=post_data).json()['result']

                    ctx.bot.send_message(chat_id=chID, text=f"{lang[userlang]['withdraw-yes-no']['text-yes']} {data[2]} {config.coin['ticker']} to address {target_address.to_string()} ")
                    ctx.bot.send_message(chat_id=chID, text=f"[{lang[userlang]['withdraw-yes-no']['view-transaction']}](https://sugar\\.wtf/esplora/tx/{str(txid)})", parse_mode="MarkdownV2")
                else:
                    ctx.bot.send_message(chat_id=chID, text=lang[userlang]['error']['withdraw']['insufficient-funds'])
            elif data[0] == "N":
                ctx.bot.delete_message(chat_id=chID, message_id=msgID)
                ctx.bot.send_message(chat_id=chID, text=f"{lang[userlang]['withdraw-yes-no']['text-no']} {data[2]} {config.coin['ticker']} to address {'sugar1q' + data[1]}")


def getBalance(id: str):

    address = getAddress(id)

    getBalance = requests.get(f"{config.apiUrl}/balance/{address}").json()["result"]["balance"]
    userBalance = Decimal(str(getBalance / 100000000))

    return userBalance


def checkAdd(address: str):
    check = requests.get(f"{config.apiUrl}/balance/{address}").json()

    if check['error']:
        return False
    else:
        return True


def getAddress(id: str):
    # Initialise bitcoin.py
    setup('mainnet')
    wif = db.getWIF(id)

    priv = PrivateKey.from_wif(f"{wif}")

    pub = priv.get_public_key()

    address = pub.get_segwit_address().to_string()

    return address


def convertToSatoshis(amount: Decimal):
    return int(round(amount * 100000000))

def convertToSugar(amount: int):
    return Decimal(amount / 100000000)


def backup():
    path = 'dbbackup'
    t = threading.Timer(600.0, backup)
    t.daemon = True
    t.start()
    if os.path.exists(path):
        if platform.system() == "Windows":
            if os.path.exists(f"{path}\\tguserdb.db"):
                os.system(f"del {path}\\tguserdb.db")
            os.system(f"copy tguserdb.db {path}\\tguserdb.db /y")
            print(f"{datetime.utcnow()} UTC Database backed up :)")
        elif platform.system() == "Linux":
            if os.path.exists(f"{path}/tguserdb.db"):
                os.system(f"rm -rf {path}/tguserdb.db")
            os.system(f"cp tguserdb.db {path}/tguserdb.db")
            print(f"{datetime.utcnow()} UTC Database backed up :)")
    else:
        if platform.system() == "Windows":
            os.mkdir(path)
            os.system(f"copy tguserdb.db {path}\\tguserdb.db /y")
            print(f"{datetime.utcnow()} UTC Database backed up :)")
        elif platform.system() == "Linux":
            os.mkdir(path)
            os.system(f"cp tguserdb.db {path}/tguserdb.db")
            print(f"{datetime.utcnow()} UTC Database backed up :)")

backup()


### LAUNCH

def main():

    updater = Updater(token=config.token, use_context=True, workers=10)

    dispatcher = updater.dispatcher

    help_command = CommandHandler('help', help)
    price_command = CommandHandler('price', price)
    info_command = CommandHandler('info', info)
    tip_command = CommandHandler('tip', tip)
    deposit_command = CommandHandler('deposit', deposit)
    balance_command = CommandHandler('balance', balance)
    withdraw_command = CommandHandler('withdraw', withdraw)
    setlang_command = CommandHandler('setlang', setLang)
    about_command = CommandHandler('about', about)
    export_command = CommandHandler('export', export)

    tip_or_withdraw_handler = CallbackQueryHandler(tip_or_withdrawFunc)
    dispatcher.add_handler(help_command)
    dispatcher.add_handler(price_command)
    dispatcher.add_handler(info_command)
    dispatcher.add_handler(tip_command)
    dispatcher.add_handler(deposit_command)
    dispatcher.add_handler(balance_command)
    dispatcher.add_handler(withdraw_command)
    dispatcher.add_handler(setlang_command)
    dispatcher.add_handler(about_command)
    dispatcher.add_handler(export_command)

    dispatcher.add_handler(tip_or_withdraw_handler)

    updater.start_polling()
    updater.idle()
    updater.stop()


if __name__ == '__main__':
    main()


