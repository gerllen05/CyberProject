import sqlite3

def create_db():
    conn = sqlite3.connect('Server.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS Users (
        userId INTEGER PRIMARY KEY AUTOINCREMENT ,
        login STRING NOT NULL ,
        password STRING NOT NULL ,
        clientId INTEGER ,
        openedFilePath STRING ,
        regTime STRING NOT NULL ,
        lastLogInTime STRING )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS Accesses (
        creatorId INTEGER NOT NULL ,
        guestId INTEGER NOT NULL ,
        path STRING NOT NULL ,
        FOREIGN KEY (creatorId) REFERENCES Users (userId) ,
        FOREIGN KEY (guestId) REFERENCES Users (userId) )''')
    conn.close()

if __name__ == '__main__':
    create_db()

