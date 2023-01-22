import sqlite3

db_conn = sqlite3.connect('Server.db')
db_conn.execute(f'DELETE FROM Accesses WHERE guestId = 1')
db_conn.execute(f'INSERT INTO Accesses (path, guestId) VALUES("new/path.txt", 1)')
accesses = db_conn.execute(f'SELECT path, guestId FROM Accesses').fetchall()
db_conn.commit()
print(accesses)
