import sqlite3
import os

db_conn = sqlite3.connect('Server/Server.db')
db_conn.execute(f'DELETE FROM Accesses WHERE guestId = 2')
db_conn.execute(f'INSERT INTO Accesses (path, guestId) VALUES("popopopa/path.txt", 2)')
accesses = db_conn.execute(f'SELECT path, guestId FROM Accesses').fetchall()
db_conn.commit()
print(accesses)

# path = "1234/12345/123456/name.txt"
# name = path.split('/')[-1]
# dirs = ""
# for dir in path.replace(name, "").split('/'):
#     if dir:
#         dirs += dir + "/"
#         print(dirs)
#         os.mkdir(dirs)

