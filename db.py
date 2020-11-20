import sqlite3

connection = sqlite3.connect("tguserdb.db")
cursor = connection.cursor()
table_create = "CREATE TABLE IF NOT EXISTS userlist(name TEXT, userid TEXT, wif TEXT)"
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
    cursor.execute(f"SELECT * FROM userlist WHERE userid={id}")

    if cursor.fetchall() == []:
        return False
    else:
        return True

def removeUser(id: str):
    connection = sqlite3.connect("tguserdb.db")
    cursor = connection.cursor()

    cursor.execute(f"DELETE FROM userlist WHERE userid={id}")

    connection.commit()
    connection.close()

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
    cursor.execute(f"SELECT name FROM userlist WHERE userid={id}")

    return list(cursor.fetchall()[0])[0]

def getWIF(id: str):
    connection = sqlite3.connect("tguserdb.db")
    cursor = connection.cursor()
    cursor.execute(f"SELECT wif FROM userlist WHERE userid='{id}'")

    return list(cursor.fetchall()[0])[0]

