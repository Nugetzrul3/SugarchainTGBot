import sqlite3

connection = sqlite3.connect("tguserdb.db")
cursor = connection.cursor()
table_create = "CREATE TABLE IF NOT EXISTS userlist(name TEXT, userid TEXT, wif TEXT, lang TEXT)"
cursor.execute(table_create)
def addUser(username: str, id: str, wif: str):
    connection = sqlite3.connect("tguserdb.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO userlist (name, userid, wif) VALUES (?,?,?)", [username, id, wif])
    connection.commit()
    connection.close()

def checkUser(id: str):
    connection = sqlite3.connect("tguserdb.db")
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM userlist WHERE userid='{id}'")

    if cursor.fetchall() == []:
        return False
    else:
        return True

def getUserID(username: str):
    connection = sqlite3.connect("tguserdb.db")
    cursor = connection.cursor()
    cursor.execute(f"SELECT userid FROM userlist WHERE name='{username}'")

    if cursor.fetchall() == []:
        return False
    else:
        connection = sqlite3.connect("tguserdb.db")
        cursor = connection.cursor()
        cursor.execute(f"SELECT userid FROM userlist WHERE name='{username}'")
        return list(cursor.fetchall()[0])[0]

def getUserName(id: str):
    connection = sqlite3.connect("tguserdb.db")
    cursor = connection.cursor()
    cursor.execute(f"SELECT name FROM userlist WHERE userid='{id}'")

    return list(cursor.fetchall()[0])[0]

def updateUser(id: str, username: str):
    connection = sqlite3.connect("tguserdb.db")
    cursor = connection.cursor()
    cursor.execute(f"UPDATE userlist SET name = '{username}' WHERE userid = '{id}'")
    connection.commit()
    connection.close()

def setLang(id: str, lang: str):
    connection = sqlite3.connect("tguserdb.db")
    cursor = connection.cursor()
    cursor.execute(f"UPDATE userlist SET lang = '{lang}' WHERE userid = '{id}'")
    connection.commit()
    connection.close()

def getLang(id: str):
    connection = sqlite3.connect("tguserdb.db")
    cursor = connection.cursor()
    cursor.execute(f"SELECT lang FROM userlist WHERE userid = '{id}'")

    return list(cursor.fetchall()[0])[0]


def getWIF(id: str):
    connection = sqlite3.connect("tguserdb.db")
    cursor = connection.cursor()
    cursor.execute(f"SELECT wif FROM userlist WHERE userid='{id}'")

    return list(cursor.fetchall()[0])[0]

