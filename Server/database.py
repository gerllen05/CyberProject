import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('Server.db')

        self.conn.execute('''CREATE TABLE IF NOT EXISTS Users (
            userId INTEGER PRIMARY KEY AUTOINCREMENT ,
            login STRING NOT NULL ,
            password STRING NOT NULL ,
            clientId INTEGER ,
            openedFilePath STRING ,
            regTime STRING NOT NULL ,
            lastLogInTime STRING )''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS Accesses (
            creatorId INTEGER NOT NULL ,
            guestId INTEGER NOT NULL ,
            path STRING NOT NULL ,
            FOREIGN KEY (creatorId) REFERENCES Users (userId) ,
            FOREIGN KEY (guestId) REFERENCES Users (userId) )''')
        
        self.conn.execute(f'UPDATE Users SET clientId = NULL, openedFilePath = NULL')
        self.conn.commit()
        self.conn.close()