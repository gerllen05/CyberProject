import sqlite3

def create_db():
    conn = sqlite3.connect('Server.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS Users (
        userId INTEGER PRIMARY KEY AUTOINCREMENT ,
        login STRING NOT NULL ,
        password STRING NOT NULL ,
        clientId INTEGER ,
        online BOOLEAN NOT NULL )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS Accesses (
        path STRING NOT NULL ,
        guestId INTEGER NOT NULL ,
        FOREIGN KEY (guestId) REFERENCES Users (userId) )''')
    conn.close()

if __name__ == '__main__':
    create_db()

