import sqlite3
import ast
import json
import operator

#Adds the user to the database taking their info as dictionary
def addToUsers(dictionary):
    database = sqlite3.connect("myDatabase.db")
    cursor = database.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, location TEXT, ip TEXT, port TEXT, lastLogin TEXT, publicKey TEXT, picture TEXT, lastUpdated TEXT, description TEXT, encoding TEXT, position TEXT, fullname TEXT, encryption TEXT, decryptionKey TEXT);")
    userFound = False
    for row in cursor.execute("""SELECT username FROM users"""):
        if row[0] == dictionary['username']:
            userFound = True
    if userFound:
        cursor.executemany("""
            UPDATE users
                SET
                    location = :location, ip = :ip, port = :port, lastLogin = :lastLogin
                WHERE username = :username""", (dictionary,))
    else:
        cursor.executemany("""
            INSERT INTO
                users
                    (username, location, ip, port, lastLogin)
                VALUES
                    (:username, :location, :ip, :port, :lastLogin)""", (dictionary,))
    database.commit()
    cursor.close()
    database.close()

#Returns user as a dictionary
def getUser(username):
    database = sqlite3.connect("myDatabase.db")
    cursor = database.cursor()
    for row in cursor.execute("""SELECT * FROM users"""):
        if row[0] == username:
            user = dictionaryFactory(cursor,row)
            return user
    return {}

#Returns user as json dictionary with relevant info for getProfile API
def getUserProfile(username):
    database = sqlite3.connect("myDatabase.db")
    cursor = database.cursor()
    for row in cursor.execute("""SELECT username, fullname, lastUpdated, position, description, location, picture, encoding, encryption, decryptionKey FROM users"""):
        if row[0] == username:
            profile = dictionaryFactory(cursor, row)
            del profile['username']
            jsonDict = json.dumps(profile)
            return jsonDict
    return {}

#Updates user profile for dictionary input
def updateUserProfile(dictionary):
    database = sqlite3.connect("myDatabase.db")
    cursor = database.cursor()
    cursor.executemany("""
            UPDATE users
                SET
                    fullname = :fullname, position = :position, description = :description, picture = :picture, lastUpdated = :lastUpdated
                WHERE username = :username""", (dictionary,))
    database.commit()
    cursor.close()
    database.close()

#Adds message to the database
def addMessage(dictionary):
    database = sqlite3.connect("myDatabase.db")
    cursor = database.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (messageID TEXT, stamp TEXT, message TEXT, contentType TEXT, answer TEXT);")
    messageID = dictionary['sender'] + ":" + dictionary['destination']
    dictionary['messageID'] = messageID
    cursor.executemany("""
                    INSERT INTO
                        messages
                            (messageID, stamp, message, contentType, answer)
                        VALUES
                            (:messageID, :stamp, :message, 'plain/text', :answer)""", (dictionary,))
    database.commit()
    cursor.close()
    database.close()

#Retrieves all of the messages between this user and their current conversation partner
def getMessages(dictionary):
    messageID = dictionary['username'] + ":" + dictionary['profile']
    secondID = dictionary['profile'] + ":" + dictionary['username']
    database = sqlite3.connect("myDatabase.db")
    cursor = database.cursor()
    dictionary = {}
    messageDict = {}
    position = 0
    for row in cursor.execute("""SELECT * FROM messages"""):
        if row[0] == messageID or row[0] == secondID:
            dictionary[row[1]] = position
            message = dictionaryFactory(cursor, row)
            messageDict[position] = message
            position += 1
    sortedList = sorted(dictionary, key=dictionary.get)
    newDictionary = {}
    for number in range(len(sortedList)):
        newDictionary[number] = messageDict[dictionary[sortedList[number]]]
        messageDict[dictionary[sortedList[number]]]
    return newDictionary

#Adds the sent file to the database
def addFile(dictionary):
    database = sqlite3.connect("myDatabase.db")
    cursor = database.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (messageID TEXT, stamp TEXT, message TEXT, content_type TEXT);")
    messageID = dictionary['sender'] + ":" + dictionary['destination']
    dictionary['messageID'] = messageID
    cursor.executemany("""
                    INSERT INTO
                        messages
                            (messageID, stamp, message, contentType, answer)
                        VALUES
                            (:messageID, :stamp, :filename, :content_type, :answer)""", (dictionary,))
    database.commit()
    cursor.close()
    database.close()

#Adds the received profile to database
def addProfile(dictionary):
    database = sqlite3.connect("myDatabase.db")
    cursor = database.cursor()
    cursor.executemany("""
        UPDATE users
            SET
                picture = :picture, lastUpdated = :lastUpdated, description = :description, encoding = :encoding, position = :position, fullname = :fullname, encryption        = :encryption,  decryptionKey = :decryptionKey
            WHERE username = :username""", (dictionary,))
    database.commit()
    cursor.close()
    database.close()

#Returns a dictionary version of which row we're reading in a database
def dictionaryFactory(cursor, row):
    dictionary = {}
    for idx, col in enumerate(cursor.description):
        dictionary[col[0]] = row[idx]
    return dictionary


